"use client";
import { fetchDatasetSummary, fetchAllDatasets } from "@/lib/api";
import { useState } from "react";

export default function Results() {
  // Debug print for API URL
  console.log("API URL (process.env.NEXT_PUBLIC_API_URL):", process.env.NEXT_PUBLIC_API_URL);
  // Hardcoded datasetId for now
  const datasetId = "684983b11152ff8e46707a5f";
  const [datasets, setDatasets] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFetchDatasets() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAllDatasets(25);
      setDatasets(data);
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  // SSR fallback for summary table (existing code)
  // This is only shown if datasets is null
  // (keeps original SSR behavior for now)
  // You may want to refactor to fully client-side if needed
  // ... existing code ...

  // If datasets are loaded, show them
  if (datasets) {
    // Handle the case where datasets is an object with a 'datasets' key
    const datasetsArray = Array.isArray(datasets) ? datasets : datasets.datasets || [];
    
    return (
      <div>
        <button
          className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          onClick={() => setDatasets(null)}
        >
          Hide datasets
        </button>
        <h2 className="text-xl font-bold mb-2">Datasets from data.gouv.fr</h2>
        {datasetsArray.length === 0 ? (
          <p className="text-gray-600">No datasets found.</p>
        ) : (
          <ul className="list-disc pl-6">
            {datasetsArray.map((ds: any) => (
              <li key={ds.id} className="mb-1">
                <span className="font-semibold">{ds.title || ds.id}</span>
                {ds.organization && ds.organization.name ? (
                  <span className="ml-2 text-gray-500">({ds.organization.name})</span>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <div>
      <button
        className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        onClick={handleFetchDatasets}
        disabled={loading}
      >
        {loading ? "Loading datasets..." : "Fetch all datasets"}
      </button>
      {error && <div className="text-red-600 mb-2">{error}</div>}
      {/* Existing summary table below */}
      <SummaryTable datasetId={datasetId} />
    </div>
  );
}

// Extracted summary table as a subcomponent for clarity
import { useEffect, useState as useClientState } from "react";
function SummaryTable({ datasetId }: { datasetId: string }) {
  const [summary, setSummary] = useClientState<any | null>(null);
  const [error, setError] = useClientState<string | null>(null);
  useEffect(() => {
    fetchDatasetSummary(datasetId, 25)
      .then(setSummary)
      .catch((e) => setError(e.message || String(e)));
  }, [datasetId]);
  if (error) return <p className="text-red-600">Failed to load dataset: {error}</p>;
  if (!summary) return <p>Loading dataset summary...</p>;
  if (!summary.head || summary.head.length === 0) {
    return <p className="text-gray-600">No data found in dataset.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border text-sm">
        <thead>
          <tr>
            {summary.columns.map((col: string) => (
              <th key={col} className="border px-2 py-1 bg-gray-100 text-left">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {summary.head.map((row: any, i: number) => (
            <tr key={i}>
              {summary.columns.map((col: string) => (
                <td key={col} className="border px-2 py-1">{row[col]?.toString() ?? ""}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-2 text-xs text-gray-500">
        Showing {summary.head.length} of {summary.shape[0]} rows. Columns: {summary.shape[1]}
      </div>
    </div>
  );
}

