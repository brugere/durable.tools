// Amazon affiliate link helpers

export type AmazonLocale =
  | "fr"
  | "com"
  | "co.uk"
  | "de"
  | "it"
  | "es"
  | "ca"
  | "com.au";

const MARKETPLACE_HOST_BY_LOCALE: Record<AmazonLocale, string> = {
  fr: "www.amazon.fr",
  com: "www.amazon.com",
  "co.uk": "www.amazon.co.uk",
  de: "www.amazon.de",
  it: "www.amazon.it",
  es: "www.amazon.es",
  ca: "www.amazon.ca",
  "com.au": "www.amazon.com.au",
};

export function buildAmazonAffiliateSearchUrl({
  brand,
  model,
  tag = "lebrugere-21",
  locale = "fr",
}: {
  brand: string;
  model?: string | null;
  tag?: string;
  locale?: AmazonLocale;
}): string {
  const host = MARKETPLACE_HOST_BY_LOCALE[locale] || MARKETPLACE_HOST_BY_LOCALE.fr;
  const searchQuery = `${brand} ${model || ""}`.trim();
  const encodedQuery = encodeURIComponent(searchQuery);
  return `https://${host}/s?k=${encodedQuery}&tag=${tag}`;
}

export function buildAmazonAffiliateProductUrl({
  asin,
  tag = "lebrugere-21",
  locale = "fr",
}: {
  asin: string;
  tag?: string;
  locale?: AmazonLocale;
}): string {
  const host = MARKETPLACE_HOST_BY_LOCALE[locale] || MARKETPLACE_HOST_BY_LOCALE.fr;
  return `https://${host}/dp/${asin}?tag=${tag}`;
}

export function getBestAffiliateLink({
  brand,
  model,
  asin,
  amazonProductUrl,
  tag = "lebrugere-21",
  locale = "fr",
}: {
  brand: string;
  model?: string | null;
  asin?: string | null;
  amazonProductUrl?: string | null;
  tag?: string;
  locale?: AmazonLocale;
}): { url: string; type: "product" | "search"; isDirect: boolean } {
  // If we have a direct Amazon product URL, use it
  if (amazonProductUrl) {
    return {
      url: amazonProductUrl,
      type: "product",
      isDirect: true
    };
  }
  
  // If we have an ASIN, build a direct product link
  if (asin) {
    return {
      url: buildAmazonAffiliateProductUrl({ asin, tag, locale }),
      type: "product", 
      isDirect: true
    };
  }
  
  // Fallback to search URL
  return {
    url: buildAmazonAffiliateSearchUrl({ brand, model, tag, locale }),
    type: "search",
    isDirect: false
  };
}


