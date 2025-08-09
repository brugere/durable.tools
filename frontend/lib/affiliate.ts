// Simple helpers to build Amazon affiliate links

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
  const keywords = [brand, model || ""].filter(Boolean).join(" ").trim();
  const url = new URL(`https://${host}/s`);
  url.searchParams.set("k", keywords);
  url.searchParams.set("tag", tag);
  return url.toString();
}

export function buildAmazonAffiliateDetailUrlFromAsin({
  asin,
  tag = "lebrugere-21",
  locale = "fr",
}: {
  asin: string;
  tag?: string;
  locale?: AmazonLocale;
}): string {
  const host = MARKETPLACE_HOST_BY_LOCALE[locale] || MARKETPLACE_HOST_BY_LOCALE.fr;
  const url = new URL(`https://${host}/dp/${asin}`);
  url.searchParams.set("tag", tag);
  return url.toString();
}


