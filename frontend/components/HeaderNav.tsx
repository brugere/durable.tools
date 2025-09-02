"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import SearchBox from "@/components/SearchBox";
import { fetchBrands } from "@/lib/api";

export default function HeaderNav() {
  const router = useRouter();
  const [brands, setBrands] = useState<string[]>([]);
  const [openMenu, setOpenMenu] = useState<null | "brand" | "perf">(null);

  useEffect(() => {
    let mounted = true;
    fetchBrands().then((b) => {
      if (mounted) setBrands(b);
    }).catch(() => {});
    return () => { mounted = false };
  }, []);

  function goHome() {
    router.push("/");
  }

  function selectBrand(brand: string) {
    setOpenMenu(null);
    router.push(`/?brand=${encodeURIComponent(brand)}&sort_by=id&sort_order=DESC`);
  }

  function selectPerformance(kind: "repairable" | "durable" | "value") {
    setOpenMenu(null);
    if (kind === "repairable") {
      router.push(`/?sort_by=note_reparabilite&sort_order=DESC&min_repairability=7`);
    } else if (kind === "durable") {
      router.push(`/?sort_by=note_id&sort_order=DESC`);
    } else {
      router.push(`/?sort_by=price_per_durability&sort_order=ASC`);
    }
  }

  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#f0f2f4] px-10 py-3 fade-in relative">
      <div className="flex items-center gap-8">
        <button onClick={goHome} className="flex items-center gap-4 text-[#111418] hover:text-[#1773cf] transition-colors duration-200">
          <div className="size-4">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M42.4379 44C42.4379 44 36.0744 33.9038 41.1692 24C46.8624 12.9336 42.2078 4 42.2078 4L7.01134 4C7.01134 4 11.6577 12.932 5.96912 23.9969C0.876273 33.9029 7.27094 44 7.27094 44L42.4379 44Z" fill="currentColor"></path>
            </svg>
          </div>
          <h2 className="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em]">Laundry Solutions</h2>
        </button>

        <nav className="flex items-center gap-6">
          <Link href="/" className="text-[#111418] text-sm font-medium leading-normal hover:text-[#1773cf] transition-colors duration-200">
            Accueil
          </Link>

          <div className="relative">
            <button onClick={() => setOpenMenu(openMenu === 'brand' ? null : 'brand')} className="text-[#111418] text-sm font-medium leading-normal hover:text-[#1773cf] transition-colors duration-200">
              Par marque ▾
            </button>
            {openMenu === 'brand' && (
              <div className="absolute z-20 mt-2 w-56 max-h-80 overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg">
                {brands.map((b) => (
                  <button key={b} onClick={() => selectBrand(b)} className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50">
                    {b}
                  </button>
                ))}
                {brands.length === 0 && (
                  <div className="px-4 py-2 text-sm text-gray-500">Chargement…</div>
                )}
              </div>
            )}
          </div>

          <div className="relative">
            <button onClick={() => setOpenMenu(openMenu === 'perf' ? null : 'perf')} className="text-[#111418] text-sm font-medium leading-normal hover:text-[#1773cf] transition-colors duration-200">
              Par performance ▾
            </button>
            {openMenu === 'perf' && (
              <div className="absolute z-20 mt-2 w-64 rounded-lg border border-gray-200 bg-white shadow-lg">
                <button onClick={() => selectPerformance('repairable')} className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50">🔧 Plus réparable</button>
                <button onClick={() => selectPerformance('durable')} className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50">🌱 Plus durable</button>
                <button onClick={() => selectPerformance('value')} className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50">💶 Meilleur prix/durabilité</button>
              </div>
            )}
          </div>
        </nav>
      </div>

      <div className="flex flex-1 justify-end gap-8">
        <div className="min-w-40 max-w-md w-full">
          <SearchBox />
        </div>
      </div>
    </header>
  );
}


