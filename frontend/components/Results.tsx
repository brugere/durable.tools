import { fetchDatasetSummary } from "@/lib/api";

export default async function Results() {
  // Hardcoded datasetId for now
  const datasetId = "684983b11152ff8e46707a5f";
  let summary;
  try {
    summary = await fetchDatasetSummary(datasetId, 25);
  } catch (e) {
    return <p className="text-red-600">Failed to load dataset: {String(e)}</p>;
  }

  if (!summary.head || summary.head.length === 0) {
    return <p className="text-gray-600">No data found in dataset.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border text-sm">
        <thead>
          <tr>
            {summary.columns.map((col) => (
              <th key={col} className="border px-2 py-1 bg-gray-100 text-left">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {summary.head.map((row, i) => (
            <tr key={i}>
              {summary.columns.map((col) => (
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

