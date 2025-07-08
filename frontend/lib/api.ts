const BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://backend:8000";

export async function fetchMachines(params: {
  q?: string;
  category?: string;
  min_score?: number;
  limit?: number;
}) {
  const url = new URL("http://backend:8000/v1/machines");
  Object.entries(params).forEach(
    ([k, v]) => v != null && url.searchParams.set(k, String(v))
  );
  const res = await fetch(url.toString(), { next: { revalidate: 60 } });
  if (!res.ok) throw new Error("API error");
  return res.json();
}

