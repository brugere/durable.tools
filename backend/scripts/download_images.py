#!/usr/bin/env python3
"""
Download product images for washing machines and store them as local assets for the website.

Strategy:
- For each machine without a local image, try existing amazon_image_url
- If missing, attempt lightweight lookup via AmazonProductLookup (optional toggle)
- Download image to frontend/public/machines/{id}.jpg
- Save relative path in DB (local_image_path)
"""

import asyncio
import os
from pathlib import Path
import logging
import aiohttp
from typing import Optional, Dict, List, Tuple
import re
from io import BytesIO
from PIL import Image

from app.duckdb_utils import get_connection
from app.amazon_lookup import AmazonProductLookup
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Resolve where to save images
# Priority 1: explicit env var for shared public dir (works in Docker)
HERE = Path(__file__).resolve()
PUBLIC_DIR_ENV = os.getenv('FRONTEND_PUBLIC_DIR')
if PUBLIC_DIR_ENV:
    PUBLIC_DIR = Path(PUBLIC_DIR_ENV).resolve() / 'machines'
else:
    # Priority 2: discover repo root by walking up to find frontend/public
    repo_root: Optional[Path] = None
    cur = HERE.parent
    while True:
        if (cur / 'frontend' / 'public').exists():
            repo_root = cur
            break
        if cur.parent == cur:
            break
        cur = cur.parent
    if repo_root is None:
        # Fallback: assume repo at two levels up (host local run)
        repo_root = HERE.parents[2]
    PUBLIC_DIR = repo_root / 'frontend' / 'public' / 'machines'

# Ensure DUCKDB_PATH points to local writable file when running outside container
os.environ.setdefault('DUCKDB_PATH', str((repo_root if 'repo_root' in locals() and repo_root is not None else HERE.parents[2]) / 'backend' / 'duckdb' / 'washing_machines.duckdb'))


NET_SEMAPHORE: Optional[asyncio.Semaphore] = None


def _base_delay_seconds() -> float:
    try:
        ms = int(os.environ.get('BASE_DELAY_MS', '250'))
    except ValueError:
        ms = 250
    # add small jitter +/- 20%
    jitter = 1.0 + random.uniform(-0.2, 0.2)
    return max(0.0, (ms / 1000.0) * jitter)


async def fetch_bytes(session: aiohttp.ClientSession, url: str, *, max_retries: int = 4) -> Optional[bytes]:
    attempt = 0
    backoff_base = 1.0
    while attempt <= max_retries:
        try:
            # base pacing to mitigate rate limits/bans
            await asyncio.sleep(_base_delay_seconds())
            if NET_SEMAPHORE is not None:
                async with NET_SEMAPHORE:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        if resp.status == 200:
                            return await resp.read()
                        if resp.status in (429, 503) or 500 <= resp.status < 600:
                            raise aiohttp.ClientResponseError(resp.request_info, resp.history, status=resp.status)
                        logger.warning(f"Failed to fetch {url}: {resp.status}")
                        return None
            else:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    if resp.status in (429, 503) or 500 <= resp.status < 600:
                        raise aiohttp.ClientResponseError(resp.request_info, resp.history, status=resp.status)
                    logger.warning(f"Failed to fetch {url}: {resp.status}")
                    return None
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                logger.warning(f"Error fetching {url}: {e} (no more retries)")
                return None
            sleep_s = backoff_base * (2 ** (attempt - 1)) * (1.0 + random.uniform(0, 0.25))
            logger.info(f"Retrying fetch {url} in {sleep_s:.1f}s (attempt {attempt}/{max_retries})")
            await asyncio.sleep(sleep_s)


def is_good_amazon_image(url: Optional[str]) -> bool:
    if not url:
        return False
    u = url.lower()
    # Prefer product CDN images
    if "m.media-amazon.com" in u and "/images/i/" in u:
        # filter out sprites, logos, placeholders
        bad_terms = ["sprite", "logo", "nav", "placeholder", "no_image", "noimage", "g/" ]
        return not any(term in u for term in bad_terms)
    # Some images hosted elsewhere might still be fine, but be conservative
    return False


async def fetch_text(session: aiohttp.ClientSession, url: str, *, max_retries: int = 4) -> Optional[str]:
    attempt = 0
    backoff_base = 1.0
    while attempt <= max_retries:
        try:
            await asyncio.sleep(_base_delay_seconds())
            if NET_SEMAPHORE is not None:
                async with NET_SEMAPHORE:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        if resp.status in (429, 503) or 500 <= resp.status < 600:
                            raise aiohttp.ClientResponseError(resp.request_info, resp.history, status=resp.status)
                        logger.warning(f"Failed to fetch page {url}: {resp.status}")
                        return None
            else:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    if resp.status in (429, 503) or 500 <= resp.status < 600:
                        raise aiohttp.ClientResponseError(resp.request_info, resp.history, status=resp.status)
                    logger.warning(f"Failed to fetch page {url}: {resp.status}")
                    return None
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                logger.warning(f"Error fetching page {url}: {e} (no more retries)")
                return None
            sleep_s = backoff_base * (2 ** (attempt - 1)) * (1.0 + random.uniform(0, 0.25))
            logger.info(f"Retrying page {url} in {sleep_s:.1f}s (attempt {attempt}/{max_retries})")
            await asyncio.sleep(sleep_s)


def extract_image_from_amazon_html(html: str) -> Optional[str]:
    # 1) og:image meta
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m and is_good_amazon_image(m.group(1)):
        return m.group(1)

    # 2) JSON-LD image field
    m = re.search(r'"image"\s*:\s*"(https?://[^"]+?)"', html, re.IGNORECASE)
    if m and is_good_amazon_image(m.group(1)):
        return m.group(1)

    # 3) landingImage data-old-hires
    m = re.search(r'id=\"landingImage\"[^>]+data-old-hires=\"([^\"]+)\"', html, re.IGNORECASE)
    if m and is_good_amazon_image(m.group(1)):
        return m.group(1)

    # 4) data-a-dynamic-image JSON map – pick first key
    m = re.search(r'id=\"landingImage\"[^>]+data-a-dynamic-image=\"(\{.+?\})\"', html, re.IGNORECASE)
    if m:
        try:
            # Unescape quotes inside attribute
            json_like = m.group(1).replace('&quot;', '"')
            # Keys are image URLs: {"https://...jpg":[...],"https://...jpg":[...]}
            url_match = re.search(r'"(https?://[^"]+?)"\s*:\s*\[', json_like)
            if url_match and is_good_amazon_image(url_match.group(1)):
                return url_match.group(1)
        except Exception:
            pass

    # 5) generic main image within imageBlock
    m = re.search(r'<img[^>]+id=\"landingImage\"[^>]+src=\"([^\"]+)\"', html, re.IGNORECASE)
    if m and is_good_amazon_image(m.group(1)):
        return m.group(1)
    return None


# ---------------- Vendor site lookup -----------------

def normalize_brand_name(brand: str) -> str:
    b = brand.lower().strip()
    replacements = {
        'lg electronics france': 'lg',
        'lg electronics': 'lg',
        'lg': 'lg',
        'bosch': 'bosch',
        'siemens': 'siemens',
        'beko': 'beko',
        'brandt': 'brandt',
        'samsung': 'samsung',
        'whirlpool': 'whirlpool',
        'miele': 'miele',
        'electrolux': 'electrolux',
        'haier': 'haier',
        'gaggenau': 'gaggenau',
    }
    for key, val in replacements.items():
        if key in b:
            return val
    # fallback keep first token
    return b.split()[0] if b else b


def vendor_brand_config(norm_brand: str) -> Dict[str, List[str]]:
    # Each brand lists accepted domains and search URLs (with {q})
    configs: Dict[str, Dict[str, List[str]]] = {
        'bosch': {
            'domains': ['bosch-home.fr'],
            'search': [
                'https://www.bosch-home.fr/recherche?search={q}',
                'https://www.bosch-home.fr/liste-des-produits?search={q}',
            ],
        },
        'siemens': {
            'domains': ['siemens-home.bsh-group.com'],
            'search': [
                'https://www.siemens-home.bsh-group.com/fr/search?searchword={q}',
            ],
        },
        'beko': {
            'domains': ['beko.com'],
            'search': [
                'https://www.beko.com/fr-fr/recherche?q={q}',
            ],
        },
        'samsung': {
            'domains': ['samsung.com'],
            'search': [
                'https://www.samsung.com/fr/search/?searchword={q}',
            ],
        },
        'lg': {
            'domains': ['lg.com'],
            'search': [
                'https://www.lg.com/fr/search/all?q={q}',
            ],
        },
        'brandt': {
            'domains': ['brandt.fr'],
            'search': [
                'https://www.brandt.fr/recherche?search={q}',
            ],
        },
        'whirlpool': {
            'domains': ['whirlpool.fr'],
            'search': [
                'https://www.whirlpool.fr/searchresult?Ntt={q}',
            ],
        },
        'miele': {
            'domains': ['miele.fr'],
            'search': [
                'https://www.miele.fr/electromenager/recherche-385.htm?search={q}',
            ],
        },
        'electrolux': {
            'domains': ['electrolux.fr'],
            'search': [
                'https://www.electrolux.fr/search/?q={q}',
            ],
        },
        'haier': {
            'domains': ['haier.com'],
            'search': [
                'https://www.haier.com/fr/search/?q={q}',
            ],
        },
        'gaggenau': {
            'domains': ['gaggenau.com'],
            'search': [
                'https://www.gaggenau.com/fr/search?q={q}',
            ],
        },
    }
    return configs.get(norm_brand, {'domains': [], 'search': []})


def extract_first_link_to_domains(html: str, domains: List[str], query_tokens: List[str]) -> Optional[str]:
    # Find first href linking to one of the allowed domains and containing at least one token
    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>', html, flags=re.IGNORECASE)
    for href in links:
        if any(d in href for d in domains):
            if any(t.lower() in href.lower() for t in query_tokens):
                return href
    # Also search for data-href
    links = re.findall(r'data-href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    for href in links:
        if any(d in href for d in domains) and any(t.lower() in href.lower() for t in query_tokens):
            return href
    return None


def tokenize_model(model: str) -> List[str]:
    # Keep alphanum tokens of length >=3 and any long digit sequences
    tokens = re.findall(r'[A-Za-z0-9]{3,}', model)
    # Prefer unique tokens
    uniq: List[str] = []
    for t in tokens:
        lt = t.lower()
        if lt not in uniq:
            uniq.append(lt)
    return uniq[:6]


def extract_og_image(html: str) -> Optional[str]:
    m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


async def vendor_lookup_image(session: aiohttp.ClientSession, brand: str, model: str) -> Optional[Tuple[str, str]]:
    norm = normalize_brand_name(brand)
    cfg = vendor_brand_config(norm)
    if not cfg['search']:
        return None
    # For LG, searching only by the model reference yields better results than brand + model
    if norm == 'lg':
        q = (model or brand or '').strip()
        tokens = tokenize_model(model or '')
    else:
        q = f"{brand} {model}".strip()
        tokens = tokenize_model(model or brand)
    for search_url in cfg['search']:
        url = search_url.format(q=aiohttp.helpers.quote(q, safe=''))
        html = await fetch_text(session, url)
        if not html:
            continue
        product_link = extract_first_link_to_domains(html, cfg['domains'], tokens)
        if not product_link:
            continue
        # Follow product page and extract image
        if product_link.startswith('/'):
            # Prepend domain if relative
            product_link = f"https://{cfg['domains'][0]}{product_link}"
        prod_html = await fetch_text(session, product_link)
        if not prod_html:
            continue
        img = extract_og_image(prod_html)
        if img:
            return img, product_link
    return None


RETAILER_SOURCES: List[Dict[str, List[str]]] = [
    {
        'domains': ['boulanger.com'],
        'search': [
            # Force the "resultats?tr=" pattern (works best for product queries)
            'https://www.boulanger.com/resultats?tr={q}',
        ],
    },
    {
        'domains': ['darty.com'],
        'search': [
            'https://www.darty.com/nav/recherche?q={q}',
        ],
    },
    {
        'domains': ['but.fr'],
        'search': [
            'https://www.but.fr/search/?text={q}',
            'https://www.but.fr/recherche/?text={q}',
        ],
    },
    {
        'domains': ['cdiscount.com'],
        'search': [
            'https://www.cdiscount.com/search/10/{q}.html',
        ],
    },
    {
        'domains': ['manomano.fr'],
        'search': [
            'https://www.manomano.fr/s/{q}',
        ],
    },
]


async def retailer_lookup_image(session: aiohttp.ClientSession, brand: str, model: str) -> Optional[Tuple[str, str]]:
    q = f"{brand} {model}".strip()
    tokens = tokenize_model(model or brand)
    for source in RETAILER_SOURCES:
        for search_url in source['search']:
            url = search_url.format(q=aiohttp.helpers.quote(q, safe=''))
            html = await fetch_text(session, url)
            if not html:
                continue
            link = extract_first_link_to_domains(html, source['domains'], tokens)
            if not link:
                continue
            if link.startswith('/'):
                link = f"https://{source['domains'][0]}{link}"
            prod_html = await fetch_text(session, link)
            if not prod_html:
                continue
            # Validate page matches washing machine and model tokens
            if not (_looks_like_washing_machine_text(prod_html) and _model_tokens_match(prod_html, model)):
                continue
            img = extract_og_image(prod_html)
            if img:
                return img, link
    return None


async def upsert_local_image_path(conn, lock: asyncio.Lock, machine_id: int, rel_path: str) -> None:
    async with lock:
        conn.execute("UPDATE washing_machines SET local_image_path = ? WHERE id = ?", [rel_path, machine_id])
        conn.commit()


def _looks_like_washing_machine_text(html: str) -> bool:
    text = html.lower()
    keywords = [
        "lave-linge", "machine à laver", "washing machine", "lave linge",
        "frontale", "hublot", "top", "essorage", "tour/min", "kg",
        "capacité", "lessive", "linge"
    ]
    bad = [
        "cordon d'alimentation", "cordon", "câble", "cable", "prise", "power cord",
        "interrupteur", "adaptateur", "multiprise", "rallonge"
    ]
    score = sum(1 for k in keywords if k in text) - sum(1 for b in bad if b in text)
    return score >= 2


def _model_tokens_match(text: str, model: str) -> bool:
    if not model:
        return True
    toks = re.findall(r"[A-Za-z0-9]{3,}", model)
    if not toks:
        return True
    found = 0
    low = text.lower()
    for t in toks[:4]:
        if t.lower() in low:
            found += 1
    return found >= max(1, len(toks[:4]) // 2)


async def download_for_machine(session: aiohttp.ClientSession, db_conn, lock: asyncio.Lock, machine: dict, lookup: Optional[AmazonProductLookup], allow_lookup: bool, prefer_vendor: bool, prefer_retailers: bool) -> None:
    machine_id = machine['id']
    brand = machine.get('nom_metteur_sur_le_marche') or ''
    model = machine.get('nom_modele') or machine.get('id_unique') or ''

    # Determine source URL
    img_url = machine.get('amazon_image_url')

    # Optional: try vendor first if requested
    if allow_lookup and prefer_vendor:
        try:
            found = await vendor_lookup_image(session, brand, model)
            if found:
                img_url, product_link = found
                async with lock:
                    db_conn.execute(
                        "UPDATE washing_machines SET amazon_image_url = ?, amazon_product_url = COALESCE(amazon_product_url, ?) WHERE id = ?",
                        [img_url, product_link, machine_id]
                    )
                    db_conn.commit()
        except Exception as e:
            logger.warning(f"Vendor-first lookup failed for {brand} {model}: {e}")
        # If vendor did not yield a good image, optionally try retailers next
        if (not img_url or not is_good_amazon_image(img_url)) and prefer_retailers:
            try:
                found = await retailer_lookup_image(session, brand, model)
                if found:
                    img_url, product_link = found
                    # Validate page content to ensure actual washing machine
                    prod_html = await fetch_text(session, product_link)
                    if prod_html and _looks_like_washing_machine_text(prod_html) and _model_tokens_match(prod_html, model):
                        async with lock:
                            db_conn.execute(
                                "UPDATE washing_machines SET amazon_image_url = ?, amazon_product_url = COALESCE(amazon_product_url, ?) WHERE id = ?",
                                [img_url, product_link, machine_id]
                            )
                            db_conn.commit()
                    else:
                        # discard if not matching
                        img_url = None
            except Exception as e:
                logger.warning(f"Retailer-first lookup failed for {brand} {model}: {e}")

    # Optional Amazon lookup if missing
    if (not img_url or not is_good_amazon_image(img_url)) and allow_lookup and lookup:
        try:
            product = await lookup.search_product(brand, model)
            if product and product.get('image_url'):
                img_url = product['image_url']
                # Also persist amazon info if useful
                async with lock:
                    db_conn.execute(
                    "UPDATE washing_machines SET amazon_asin = COALESCE(amazon_asin, ?), amazon_product_url = COALESCE(amazon_product_url, ?), amazon_image_url = COALESCE(amazon_image_url, ?) WHERE id = ?",
                    [product.get('asin'), product.get('product_url'), product.get('image_url'), machine_id]
                    )
                    db_conn.commit()
        except Exception as e:
            logger.warning(f"Lookup failed for {brand} {model}: {e}")

    # Try vendor site lookup if still no good image and not already tried first
    if not is_good_amazon_image(img_url) and allow_lookup and not prefer_vendor:
        try:
            found = await vendor_lookup_image(session, brand, model)
            if found:
                img_url, product_link = found
                async with lock:
                    db_conn.execute(
                        "UPDATE washing_machines SET amazon_image_url = COALESCE(amazon_image_url, ?), amazon_product_url = COALESCE(amazon_product_url, ?) WHERE id = ?",
                        [img_url, product_link, machine_id]
                    )
                    db_conn.commit()
        except Exception as e:
            logger.warning(f"Vendor lookup failed for {brand} {model}: {e}")

    # Retailer lookup as last resort if still no good image
    if not is_good_amazon_image(img_url) and allow_lookup and not prefer_vendor and prefer_retailers:
        try:
            found = await retailer_lookup_image(session, brand, model)
            if found:
                img_url, product_link = found
                prod_html = await fetch_text(session, product_link)
                if prod_html and _looks_like_washing_machine_text(prod_html) and _model_tokens_match(prod_html, model):
                    async with lock:
                        db_conn.execute(
                            "UPDATE washing_machines SET amazon_image_url = COALESCE(amazon_image_url, ?), amazon_product_url = COALESCE(amazon_product_url, ?) WHERE id = ?",
                            [img_url, product_link, machine_id]
                        )
                        db_conn.commit()
                else:
                    img_url = None
        except Exception as e:
            logger.warning(f"Retailer lookup failed for {brand} {model}: {e}")

    # Try to refine with product detail page if we have a product URL/ASIN (Amazon)
    if not is_good_amazon_image(img_url):
        product_url = machine.get('amazon_product_url')
        asin = machine.get('amazon_asin')
        if not product_url and asin:
            product_url = f"https://www.amazon.fr/dp/{asin}"
        if product_url:
            html = await fetch_text(session, product_url)
            if html and _looks_like_washing_machine_text(html) and _model_tokens_match(html, model):
                better = extract_image_from_amazon_html(html)
                if is_good_amazon_image(better):
                    img_url = better
                    async with lock:
                        db_conn.execute(
                            "UPDATE washing_machines SET amazon_image_url = ? WHERE id = ?",
                            [img_url, machine_id]
                        )
                        db_conn.commit()
            else:
                # Do not trust this page if it doesn't look like the correct product category
                img_url = None

    if not img_url:
        logger.info(f"No image URL for machine {machine_id} ({brand} {model})")
        return

    # Download
    data = await fetch_bytes(session, img_url)
    if not data:
        return

    # Validate image payload: basic format, dimensions, and simple heuristic
    is_valid = True
    try:
        with Image.open(BytesIO(data)) as im:
            width, height = im.size
            # Basic filters: minimum size and aspect ratio constraints (portrait-ish, but not extreme)
            if width < 200 or height < 200:
                is_valid = False
            aspect = width / float(height)
            if aspect < 0.4 or aspect > 1.2:
                # Many product images are near-portrait; reject extreme banners/panoramas
                is_valid = False
            # Reject transparent icons/logos by checking alpha coverage share if present
            if is_valid and im.mode in ("RGBA", "LA"):
                alpha = im.split()[-1]
                # Compute fraction of mostly-transparent pixels
                transparent = sum(1 for p in alpha.getdata() if p < 16)
                if transparent / float(width * height) > 0.50:
                    is_valid = False
    except Exception:
        is_valid = False

    if not is_valid:
        logger.info(f"Rejected image for machine {machine_id} due to validation rules: {img_url}")
        return

    # Save to public folder
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    ext = '.jpg'
    out_path = PUBLIC_DIR / f"{machine_id}{ext}"
    with open(out_path, 'wb') as f:
        f.write(data)
    rel = f"/machines/{machine_id}{ext}"
    await upsert_local_image_path(db_conn, lock, machine_id, rel)
    logger.info(f"Saved image for machine {machine_id} -> {rel}")


async def main_async(limit: int = 200, allow_lookup: bool = False, refresh_bad: bool = False, rebuild_missing: bool = False, force_update: bool = False, prefer_vendor: bool = False, prefer_retailers: bool = False):
    # Single read-write connection for all operations
    conn = get_connection(readonly=False)
    conn.execute("ALTER TABLE washing_machines ADD COLUMN IF NOT EXISTS local_image_path TEXT")
    conn.commit()

    # Optional destructive reset: remove all local images and clear DB paths
    remove_all = os.environ.get('RESET_ALL_IMAGES', '0') == '1'
    if remove_all:
        try:
            # Clear DB references
            conn.execute("UPDATE washing_machines SET local_image_path = NULL")
            conn.commit()
            # Delete files under PUBLIC_DIR
            if PUBLIC_DIR.exists():
                for p in list(PUBLIC_DIR.glob('*.jpg')):
                    try:
                        p.unlink()
                    except Exception:
                        pass
            logger.info("All local images and references removed. Starting fresh ingestion.")
        except Exception as e:
            logger.warning(f"Failed to reset images: {e}")

    # Build filter: need image OR want to refresh when current image seems bad
    refresh_flag = 1 if refresh_bad else 0
    # Optional narrowing by brand/model
    base_sql = (
        "SELECT id, nom_metteur_sur_le_marche, nom_modele, id_unique, "
        "amazon_image_url, amazon_product_url, amazon_asin, local_image_path "
        "FROM washing_machines"
    )
    where = []
    params: List = []
    brand_filter = os.environ.get('IMAGE_FILTER_BRAND')
    model_filter = os.environ.get('IMAGE_FILTER_MODEL')
    if brand_filter:
        where.append("LOWER(nom_metteur_sur_le_marche) LIKE ?")
        params.append(f"%{brand_filter.lower()}%")
    if model_filter:
        where.append("LOWER(nom_modele) LIKE ?")
        params.append(f"%{model_filter.lower()}%")
    if where:
        base_sql += " WHERE " + " AND ".join(where)
    base_sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(base_sql, params).fetchall()
    cols = [d[0] for d in conn.description]
    machines_raw = [dict(zip(cols, r)) for r in rows]
    machines: list[dict] = []
    if force_update:
        machines = machines_raw
    else:
        for m in machines_raw:
            lip = m.get('local_image_path') or ''
            target = None
            if lip.startswith('/'):
                target = (PUBLIC_DIR.parent / lip.lstrip('/')).resolve()
            # decide if needs work
            need = False
            if not lip:
                need = True
            elif rebuild_missing and target is not None and not target.exists():
                need = True
            elif refresh_bad and (m.get('amazon_image_url') is None or not is_good_amazon_image(m.get('amazon_image_url'))):
                need = True
            if need:
                machines.append(m)

    if not machines:
        logger.info("No machines needing images.")
        return

    logger.info(f"Processing {len(machines)} machines...")

    lock = asyncio.Lock()
    # global network concurrency limiter
    global NET_SEMAPHORE
    try:
        max_conc = int(os.environ.get('MAX_CONCURRENT_FETCHES', '6'))
    except ValueError:
        max_conc = 6
    NET_SEMAPHORE = asyncio.Semaphore(max(1, max_conc))
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        lookup_ctx = AmazonProductLookup() if allow_lookup else None
        if lookup_ctx:
            await lookup_ctx.__aenter__()
        try:
            tasks = [download_for_machine(session, conn, lock, m, lookup_ctx, allow_lookup, prefer_vendor, prefer_retailers) for m in machines]
            await asyncio.gather(*tasks)
        finally:
            if lookup_ctx:
                await lookup_ctx.__aexit__(None, None, None)
        # Keep connection open until all tasks finished; then close
        conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Download washing machine images to local public assets")
    parser.add_argument('--limit', type=int, default=200, help='Max machines to process')
    parser.add_argument('--brand', type=str, default=None, help='Only process a specific brand (case-insensitive contains match)')
    parser.add_argument('--model', type=str, default=None, help='Only process models matching this substring (case-insensitive)')
    parser.add_argument('--allow-lookup', action='store_true', help='If set, perform Amazon search to find an image when missing')
    parser.add_argument('--refresh-bad', action='store_true', help='Re-fetch and replace images when current amazon_image_url looks like a placeholder/logo')
    parser.add_argument('--rebuild-missing', action='store_true', help='Rebuild local images when DB has a path but the file is missing in public dir')
    parser.add_argument('--force-update', action='store_true', help='Force processing for all selected machines regardless of existing local images or URL quality')
    parser.add_argument('--prefer-vendor', action='store_true', help='Try vendor websites first to fetch images before Amazon')
    parser.add_argument('--prefer-retailers', action='store_true', help='Also try retailer websites (e.g., Boulanger, BUT) as image sources')
    args = parser.parse_args()

    # Allow narrowing by brand/model in SQL for efficiency
    # We keep the prior logic (force/refresh/rebuild) after selecting rows
    def run_with_filters():
        return asyncio.run(main_async(limit=args.limit, allow_lookup=args.allow_lookup, refresh_bad=args.refresh_bad, rebuild_missing=args.rebuild_missing, force_update=args.force_update, prefer_vendor=args.prefer_vendor, prefer_retailers=args.prefer_retailers))

    # Quick path: if no filters just run
    if not args.brand and not args.model:
        return run_with_filters()

    # Otherwise: temporarily set env filters for SQL selection by narrowing the LIMIT query
    # Simpler approach: bump limit high and filter in-memory before processing
    os.environ.setdefault('IMAGE_FILTER_LIMIT', str(max(args.limit, 5000)))
    return run_with_filters()


if __name__ == '__main__':
    main()


