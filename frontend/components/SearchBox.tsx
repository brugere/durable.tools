"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SearchBox({ defaultValue = "" }: { defaultValue?: string }) {
  const router = useRouter();
  const [q, setQ] = useState(defaultValue);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        router.push(`/?q=${encodeURIComponent(q)}`);
      }}
      className="mb-6"
    >
      <input
        type="text"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search washing machines by brand, model, or repairability…"
        className="w-full border p-2 rounded"
      />
      <div className="mt-2 text-sm text-gray-600">
        Try: "most repairable machine of 2025", "Samsung", "LG", etc.
      </div>
    </form>
  );
}

