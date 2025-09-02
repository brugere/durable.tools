// frontend/app/page.tsx

import dynamic from "next/dynamic";
import { Suspense } from "react";
// Landing page no longer shows an inline SearchBox; the only SearchBox is in the header

// Lazy-load the client MachineResults to reduce initial JS and TBT
const MachineResults = dynamic(() => import("@/components/MachineResults"), {
  loading: () => (
    <div className="text-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1773cf] mx-auto"></div>
      <p className="mt-4 text-[#637588]">Recherche en cours...</p>
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1773cf] mx-auto"></div>
      <p className="mt-4 text-[#637588]">Recherche en cours...</p>
    </div>
  ),
  ssr: false,
});

export default function Home({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  return (
    <div className="relative flex size-full min-h-screen flex-col bg-white group/design-root overflow-x-hidden">
      <div className="layout-container flex h-full grow flex-col">
        <div className="px-40 flex flex-1 justify-center py-5">
          <div className="layout-content-container flex flex-col max-w-[960px] flex-1 fade-in">
            <div className="@container">
              <div className="@[480px]:p-4">
                <div
                  className="flex min-h-[480px] flex-col gap-6 bg-cover bg-center bg-no-repeat @[480px]:gap-8 @[480px]:rounded-lg items-start justify-end px-4 pb-10 @[480px]:px-10 relative overflow-hidden slide-up"
                  style={{
                    backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.5) 100%), url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                >
                  {/* Subtle animated overlay */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-900/20 to-purple-900/20 animate-pulse"></div>
                  
                  <div className="flex flex-col gap-2 text-left relative z-10">
                    <h1
                      className="text-white text-4xl font-black leading-tight tracking-[-0.033em] @[480px]:text-5xl @[480px]:font-black @[480px]:leading-tight @[480px]:tracking-[-0.033em] drop-shadow-lg"
                    >
                      Lave-linge Durables pour Investisseurs Immobiliers
                    </h1>
                    <h2 className="text-white text-sm font-normal leading-normal @[480px]:text-base @[480px]:font-normal @[480px]:leading-normal drop-shadow-md max-w-2xl">
                      Maximisez la valeur de votre propriété avec nos lave-linge durables et efficaces, conçus pour les immeubles multi-logements.
                    </h2>
                  </div>
                  <button
                    className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 @[480px]:h-12 @[480px]:px-5 bg-[#1773cf] hover:bg-[#1565c0] text-white text-sm font-bold leading-normal tracking-[0.015em] @[480px]:text-base @[480px]:font-bold @[480px]:leading-normal @[480px]:tracking-[0.015em] transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-95 relative z-10 hover-lift"
                  >
                    <span className="truncate">Explorer les Produits</span>
                  </button>
                </div>
              </div>
            </div>
            
            <h2 className="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5 slide-up">Lave-linge en Vedette</h2>
            
            {/* Search box removed from body */}
            
            <div className="grid grid-cols-[repeat(auto-fit,minmax(158px,1fr))] gap-3 p-4 slide-up">
              <div className="flex flex-col gap-3 pb-3 group cursor-pointer transition-transform duration-200 hover:scale-105">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg shadow-sm group-hover:shadow-md transition-shadow duration-200"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                ></div>
                <div className="space-y-1">
                  <p className="text-[#111418] text-base font-medium leading-normal">Samsung WW90T534DAW</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Haute efficacité, 9kg, classe A+++</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex text-yellow-400">
                      <span>★★★★★</span>
                    </div>
                    <span className="text-xs text-[#637588]">4.8/5</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-3 pb-3 group cursor-pointer transition-transform duration-200 hover:scale-105">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg shadow-sm group-hover:shadow-md transition-shadow duration-200"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1582735689369-4fe89db7114c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80")'
                  }}
                ></div>
                <div className="space-y-1">
                  <p className="text-[#111418] text-base font-medium leading-normal">LG F4V510WSE</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Design compact, 10.5kg, intelligent</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex text-yellow-400">
                      <span>★★★★☆</span>
                    </div>
                    <span className="text-xs text-[#637588]">4.6/5</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-3 pb-3 group cursor-pointer transition-transform duration-200 hover:scale-105">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg shadow-sm group-hover:shadow-md transition-shadow duration-200"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1581578731548-c64695cc6952?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2074&q=80")'
                  }}
                ></div>
                <div className="space-y-1">
                  <p className="text-[#111418] text-base font-medium leading-normal">Bosch WAT28440FF</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Robuste, 8kg, classe A+++</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex text-yellow-400">
                      <span>★★★★★</span>
                    </div>
                    <span className="text-xs text-[#637588]">4.9/5</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-3 pb-3 group cursor-pointer transition-transform duration-200 hover:scale-105">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg shadow-sm group-hover:shadow-md transition-shadow duration-200"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                ></div>
                <div className="space-y-1">
                  <p className="text-[#111418] text-base font-medium leading-normal">Whirlpool FSCR12440</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Économique, 12kg, fiable</p>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex text-yellow-400">
                      <span>★★★★☆</span>
                    </div>
                    <span className="text-xs text-[#637588]">4.4/5</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Quick action buttons removed for lean UI */}
            
            {/* Results Section */}
            {(searchParams.q || searchParams.brand || searchParams.model || searchParams.sort_by || searchParams.min_repairability || searchParams.min_reliability) && (
              <section className="mb-12">
                <Suspense fallback={null}>
                  <MachineResults searchParams={searchParams} />
                </Suspense>
              </section>
            )}
          </div>
        </div>
      </div>
        </div>
      </div>
    </div>
  );
}
