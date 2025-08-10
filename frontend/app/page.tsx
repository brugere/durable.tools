// frontend/app/page.tsx

import dynamic from "next/dynamic";
import { Suspense } from "react";
import SearchBox from "@/components/SearchBox";

// Lazy-load the client MachineResults to reduce initial JS and TBT
const MachineResults = dynamic(() => import("@/components/MachineResults"), {
  loading: () => (
    <div className="text-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1773cf] mx-auto"></div>
      <p className="mt-4 text-[#637588]">Recherche en cours...</p>
    </div>
  ),
  ssr: false,
});

export default function Home({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  return (
    <div className="relative flex size-full min-h-screen flex-col bg-white group/design-root overflow-x-hidden">
      <div className="layout-container flex h-full grow flex-col">
        <div className="px-40 flex flex-1 justify-center py-5">
          <div className="layout-content-container flex flex-col max-w-[960px] flex-1">
            <div className="@container">
              <div className="@[480px]:p-4">
                <div
                  className="flex min-h-[480px] flex-col gap-6 bg-cover bg-center bg-no-repeat @[480px]:gap-8 @[480px]:rounded-lg items-start justify-end px-4 pb-10 @[480px]:px-10"
                  style={{
                    backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.4) 100%), url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                >
                  <div className="flex flex-col gap-2 text-left">
                    <h1
                      className="text-white text-4xl font-black leading-tight tracking-[-0.033em] @[480px]:text-5xl @[480px]:font-black @[480px]:leading-tight @[480px]:tracking-[-0.033em]"
                    >
                      Lave-linge Durables pour Investisseurs Immobiliers
                    </h1>
                    <h2 className="text-white text-sm font-normal leading-normal @[480px]:text-base @[480px]:font-normal @[480px]:leading-normal">
                      Maximisez la valeur de votre propriété avec nos lave-linge durables et efficaces, conçus pour les immeubles multi-logements.
                    </h2>
                  </div>
                  <button
                    className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 @[480px]:h-12 @[480px]:px-5 bg-[#1773cf] text-white text-sm font-bold leading-normal tracking-[0.015em] @[480px]:text-base @[480px]:font-bold @[480px]:leading-normal @[480px]:tracking-[0.015em]"
                  >
                    <span className="truncate">Explorer les Produits</span>
                  </button>
                </div>
              </div>
            </div>
            
            <h2 className="text-[#111418] text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">Lave-linge en Vedette</h2>
            
            <div className="px-4 py-3">
              <SearchBox defaultValue={searchParams.q} />
            </div>
            
            <div className="grid grid-cols-[repeat(auto-fit,minmax(158px,1fr))] gap-3 p-4">
              <div className="flex flex-col gap-3 pb-3">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                ></div>
                <div>
                  <p className="text-[#111418] text-base font-medium leading-normal">Samsung WW90T534DAW</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Haute efficacité, 9kg, classe A+++</p>
                </div>
              </div>
              <div className="flex flex-col gap-3 pb-3">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                ></div>
                <div>
                  <p className="text-[#111418] text-base font-medium leading-normal">LG F4V510WSE</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Design compact, 10.5kg, intelligent</p>
                </div>
              </div>
              <div className="flex flex-col gap-3 pb-3">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                ></div>
                <div>
                  <p className="text-[#111418] text-base font-medium leading-normal">Bosch WAT28440FF</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Robuste, 8kg, classe A+++</p>
                </div>
              </div>
              <div className="flex flex-col gap-3 pb-3">
                <div
                  className="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-lg"
                  style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2069&q=80")'
                  }}
                ></div>
                <div>
                  <p className="text-[#111418] text-base font-medium leading-normal">Whirlpool FSCR12440</p>
                  <p className="text-[#637588] text-sm font-normal leading-normal">Économique, 12kg, fiable</p>
                </div>
              </div>
            </div>
            
            <div className="flex justify-center">
              <div className="flex flex-1 gap-3 flex-wrap px-4 py-3 max-w-[480px] justify-center">
                <button
                  className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#1773cf] text-white text-sm font-bold leading-normal tracking-[0.015em] grow"
                >
                  <span className="truncate">Voir Tous les Produits</span>
                </button>
                <button
                  className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#f0f2f4] text-[#111418] text-sm font-bold leading-normal tracking-[0.015em] grow"
                >
                  <span className="truncate">Contacter les Ventes</span>
                </button>
              </div>
            </div>
            
            {/* Results Section */}
            {searchParams.q && (
              <section className="mb-12">
                <Suspense fallback={null}>
                  <MachineResults query={searchParams.q} />
                </Suspense>
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
