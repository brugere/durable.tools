const BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://backend:8000";

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
  const url = new URL(`${BASE}/v1/machines`);
  Object.entries(params).forEach(
    ([k, v]) => v != null && url.searchParams.set(k, String(v))
  );
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("API error");
  return res.json();
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
  const url = new URL(`${BASE}/v1/dataset/${datasetId}`);
  url.searchParams.set("limit", String(limit));
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("API error");
  return res.json();
}

export async function fetchAllDatasets(limit: number = 100): Promise<any[]> {
  const url = new URL(`${BASE}/v1/datasets`);
  url.searchParams.set("limit", String(limit));
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("API error");
  return res.json();
}

export async function fetchMachineDetails(machineId: number): Promise<any> {
  const url = new URL(`${BASE}/v1/machines/${machineId}`);
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("API error");
  return res.json();
}

export async function fetchBrands(): Promise<string[]> {
  const url = new URL(`${BASE}/v1/brands`);
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("API error");
  const data = await res.json();
  return data.brands || [];
}

export async function fetchStatistics(): Promise<any> {
  const url = new URL(`${BASE}/v1/statistics`);
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("API error");
  return res.json();
}


