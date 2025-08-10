// Determine API base URL based on environment
const IS_BROWSER = typeof window !== 'undefined';

// For local development, use the backend port directly
// For production, use relative paths (proxied by Nginx)
function getBaseUrl(): string {
  if (!IS_BROWSER) {
    return 'http://backend:8000'; // Server-side rendering (inside Docker network)
  }
  
  // Check if we're in local development (localhost:3000)
  if (window.location.hostname === 'localhost' && window.location.port === '3000') {
    return 'http://localhost:8000'; // Local development - direct backend access
  }
  
  return ''; // Production - relative paths (proxied by Nginx)
}

function makeUrl(path: string): string {
  const base = getBaseUrl();
  return base ? `${base}${path}` : path;
}

// Cache for API responses
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Request deduplication
const pendingRequests = new Map<string, Promise<any>>();

function getCacheKey(endpoint: string, params: Record<string, any>): string {
  const sortedParams = Object.keys(params)
    .sort()
    .map(key => `${key}=${params[key]}`)
    .join('&');
  return `${endpoint}?${sortedParams}`;
}

async function cachedFetch(url: string | URL, options: RequestInit = {}) {
  const urlString = typeof url === 'string' ? url : url.toString();
  const cacheKey = urlString;
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }

  // Check if there's already a pending request for this URL
  if (pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey)!;
  }

  const headers: Record<string, string> = {
    'Accept': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };
  // Avoid setting Content-Type for GET requests to prevent unnecessary preflights
  if (options.method && options.method.toUpperCase() !== 'GET') {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  }

  const requestPromise = fetch(urlString, {
    ...options,
    headers,
  }).then(async (res) => {
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const data = await res.json();
    
    // Cache the successful response
    cache.set(cacheKey, { data, timestamp: Date.now() });
    pendingRequests.delete(cacheKey);
    
    return data;
  }).catch((error) => {
    pendingRequests.delete(cacheKey);
    throw error;
  });

  pendingRequests.set(cacheKey, requestPromise);
  return requestPromise;
}

export async function fetchMachines(params: {
  q?: string;
  brand?: string;
  model?: string;
  min_repairability?: number;
  max_repairability?: number;
  min_reliability?: number;
  max_reliability?: number;
  year?: number;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: string;
}) {
  const url = new URL(makeUrl('/v1/machines'), IS_BROWSER ? window.location.origin : 'http://backend:8000');
  Object.entries(params).forEach(([k, v]) => {
    if (v != null) url.searchParams.set(k, String(v));
  });
  return cachedFetch(url.toString());
}

// New: Fetch dataset summary from backend
type DatasetSummary = {
  columns: string[];
  head: Record<string, any>[];
  shape: [number, number];
  describe_numeric: Record<string, any>;
  null_counts: Record<string, number>;
  distinct_counts: Record<string, number>;
};

export async function fetchDatasetSummary(datasetId: string = "684983b11152ff8e46707a5f", limit: number = 25): Promise<DatasetSummary> {
  const url = new URL(makeUrl(`/v1/dataset/${datasetId}`), IS_BROWSER ? window.location.origin : 'http://backend:8000');
  url.searchParams.set("limit", String(limit));
  return cachedFetch(url.toString());
}

export async function fetchAllDatasets(limit: number = 100): Promise<any[]> {
  const url = new URL(makeUrl('/v1/datasets'), IS_BROWSER ? window.location.origin : 'http://backend:8000');
  url.searchParams.set("limit", String(limit));
  return cachedFetch(url.toString());
}

export async function fetchMachineDetails(machineId: number): Promise<any> {
  const url = new URL(makeUrl(`/v1/machines/${machineId}`), IS_BROWSER ? window.location.origin : 'http://backend:8000');
  return cachedFetch(url.toString());
}

export async function fetchBrands(): Promise<string[]> {
  const url = new URL(makeUrl('/v1/brands'), IS_BROWSER ? window.location.origin : 'http://backend:8000');
  const data = await cachedFetch(url.toString());
  return data.brands || [];
}

export async function fetchStatistics(): Promise<any> {
  const url = new URL(makeUrl('/v1/statistics'), IS_BROWSER ? window.location.origin : 'http://backend:8000');
  return cachedFetch(url.toString());
}

// Clear cache function for development
export function clearCache() {
  cache.clear();
  pendingRequests.clear();
}


