"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SearchBox({ defaultValue = "" }: { defaultValue?: string }) {
  const router = useRouter();
  const [q, setQ] = useState(defaultValue);

  return (
    <div className="w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (q.trim()) {
            router.push(`/?q=${encodeURIComponent(q.trim())}`);
          }
        }}
        className="relative"
      >
        <div className="relative">
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Rechercher un lave-linge par marque, modèle ou critère..."
            className="w-full px-6 py-4 text-lg border-2 border-blue-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-200 transition-all duration-200 placeholder-gray-400 bg-white shadow-sm"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors duration-200 shadow-md"
          >
            Rechercher
          </button>
        </div>
      </form>
      
      {/* Quick Search Suggestions with Colors */}
      <div className="mt-6 flex flex-wrap gap-3 justify-center">
        <button
          onClick={() => router.push('/?q=plus réparable')}
          className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-blue-200"
        >
          Plus réparable
        </button>
        <button
          onClick={() => router.push('/?q=Samsung')}
          className="bg-green-100 hover:bg-green-200 text-green-800 px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-green-200"
        >
          Samsung
        </button>
        <button
          onClick={() => router.push('/?q=LG')}
          className="bg-purple-100 hover:bg-purple-200 text-purple-800 px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-purple-200"
        >
          LG
        </button>
        <button
          onClick={() => router.push('/?q=2025')}
          className="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-yellow-200"
        >
          Modèles 2025
        </button>
        <button
          onClick={() => router.push('/?q=plus fiable')}
          className="bg-red-100 hover:bg-red-200 text-red-800 px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-red-200"
        >
          Plus fiable
        </button>
      </div>
    </div>
  );
}

