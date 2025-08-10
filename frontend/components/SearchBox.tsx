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
          <div className="flex w-full flex-1 items-stretch rounded-lg h-12">
            <div
              className="text-[#637588] flex border-none bg-[#f0f2f4] items-center justify-center pl-4 rounded-l-lg border-r-0"
              data-icon="MagnifyingGlass"
              data-size="24px"
              data-weight="regular"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                <path
                  d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"
                ></path>
              </svg>
            </div>
            <input
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Rechercher par modèle, capacité ou fonctionnalités"
              className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#111418] focus:outline-0 focus:ring-0 border-none bg-[#f0f2f4] focus:border-none h-full placeholder:text-[#637588] px-4 rounded-l-none border-l-0 pl-2 text-base font-normal leading-normal"
            />
          </div>
        </div>
      </form>
      
      {/* Enhanced Quick Search Suggestions */}
      <div className="mt-6">
        <div className="text-center mb-4">
          <p className="text-sm text-[#637588] mb-2">Filtres populaires :</p>
        </div>
        
        {/* Primary Filters */}
        <div className="flex flex-wrap gap-3 justify-center mb-4">
          <button
            onClick={() => router.push('/?q=plus réparable')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            🔧 Plus réparable
          </button>
          <button
            onClick={() => router.push('/?q=plus fiable')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            ⭐ Plus fiable
          </button>
          <button
            onClick={() => router.push('/?q=excellent')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            🏆 Excellent
          </button>
          <button
            onClick={() => router.push('/?q=durable')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            🌱 Durable
          </button>
        </div>
        
        {/* Brand Filters */}
        <div className="flex flex-wrap gap-3 justify-center mb-4">
          <button
            onClick={() => router.push('/?q=Samsung')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            📱 Samsung
          </button>
          <button
            onClick={() => router.push('/?q=LG')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            📺 LG
          </button>
          <button
            onClick={() => router.push('/?q=Bosch')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            🏠 Bosch
          </button>
          <button
            onClick={() => router.push('/?q=Whirlpool')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            ⚡ Whirlpool
          </button>
        </div>
        
        {/* Year and Type Filters */}
        <div className="flex flex-wrap gap-3 justify-center">
          <button
            onClick={() => router.push('/?q=2025')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            📅 Modèles 2025
          </button>
          <button
            onClick={() => router.push('/?q=hublot')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            🔄 Hublot
          </button>
          <button
            onClick={() => router.push('/?q=top')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            📦 Top
          </button>
          <button
            onClick={() => router.push('/?q=bon marché')}
            className="bg-[#f0f2f4] hover:bg-[#e4e7eb] text-[#111418] px-4 py-2 rounded-lg font-medium transition-colors duration-200 border border-[#f0f2f4]"
          >
            💰 Bon marché
          </button>
        </div>
      </div>
    </div>
  );
}

