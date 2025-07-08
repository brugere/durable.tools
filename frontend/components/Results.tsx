import Link from "next/link";
import { fetchMachines } from "@/lib/api";

export default async function Results({ q = "" }: { q?: string }) {
  const machines = await fetchMachines({ q, limit: 25 });

  if (machines.length === 0) {
    return <p className="text-gray-600">No machines found.</p>;
  }

  return (
    <ul>
      {machines.map((m: any) => (
        <li key={m.id} className="py-2 border-b">
          <Link href={`/machines/${m.id}`} className="font-medium">
            {m.brand} {m.model_name}
          </Link>
          <span className="ml-2 text-sm text-gray-600">
            Repair score {m.current_score}
          </span>
        </li>
      ))}
    </ul>
  );
}

