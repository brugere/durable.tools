// frontend/app/page.tsx
export const dynamic = "force-dynamic";   // add this

import { Suspense } from "react";
import SearchBox from "@/components/SearchBox";
import MachineResults from "@/components/MachineResults";

export default function Home({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  return (
    <main className="max-w-5xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        Find the most repairable washing machines
      </h1>
      <SearchBox defaultValue={searchParams.q} />
      <Suspense fallback={<p>Loading...</p>}>
        <MachineResults query={searchParams.q} />
      </Suspense>
    </main>
  );
}
