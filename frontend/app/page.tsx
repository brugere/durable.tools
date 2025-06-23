import { Suspense } from "react";
import SearchBox from "@/components/SearchBox";
import Results from "@/components/Results";

export default function Home() {
  return (
    <main className="max-w-5xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        Find the most repairable machines
      </h1>
      <SearchBox />
      <Suspense fallback={<p>Loading...</p>}>
        {/* server component fetching /v1/search */}
        <Results />
      </Suspense>
    </main>
  );
}
