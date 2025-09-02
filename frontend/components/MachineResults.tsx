"use client";

import { fetchMachines } from "@/lib/api";
import { useState, useEffect, useMemo, useCallback } from "react";
import { getBestAffiliateLink } from "@/lib/affiliate";

interface Machine {
  id?: number | null;
  nom_modele?: string | null;
  nom_metteur_sur_le_marche: string;
  date_calcul?: string | null;
  note_reparabilite?: number | null;
  note_fiabilite?: number | null;
  note_id?: number | null;
  categorie_produit?: string | null;
  url_tableau_detail_notation?: string | null;
  id_unique?: string | null;
  // Amazon product data
  amazon_asin?: string | null;
  amazon_product_url?: string | null;
  amazon_image_url?: string | null;
  amazon_price_eur?: number | null;
  amazon_product_title?: string | null;
  // Local image
  local_image_path?: string | null;
}

interface SearchResults {
  machines: Machine[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

interface MachineResultsProps {
  searchParams: { [key: string]: any };
}

// Memoized helper functions for better performance
const getScoreColor = (score: number) => {
  if (score >= 9.0) return "text-green-600";
  if (score >= 8.5) return "text-green-500";
  if (score >= 7.5) return "text-green-400";
  if (score >= 6.5) return "text-yellow-500";
  if (score >= 5.5) return "text-yellow-600";
  if (score >= 4.5) return "text-orange-500";
  if (score >= 3.5) return "text-orange-600";
  return "text-red-600";
};

const getCategoryColor = (index: number) => {
  const colors = [
    "text-purple-600",
    "text-blue-600", 
    "text-red-600",
    "text-orange-600",
    "text-green-600",
    "text-indigo-600"
  ];
  return colors[index % colors.length];
};

// Build the best available Amazon affiliate link
const getAffiliateLink = (machine: Machine) => {
  const linkData = getBestAffiliateLink({
    brand: machine.nom_metteur_sur_le_marche,
    model: machine.nom_modele ?? machine.id_unique ?? "",
    asin: machine.amazon_asin,
    amazonProductUrl: machine.amazon_product_url,
    locale: "fr"
  });
  
  return { 
    name: linkData.isDirect ? "Acheter sur Amazon" : "Rechercher sur Amazon",
    url: linkData.url, 
    icon: linkData.isDirect ? "🛒" : "🔍",
    isDirect: linkData.isDirect,
    price: machine.amazon_price_eur
  } as const;
};

// Memoized machine card component
const MachineCard = ({ machine, index }: { machine: Machine; index: number }) => {
  const retailer = useMemo(
    () => getAffiliateLink(machine),
    [machine]
  );

  const modelDisplay = machine.nom_modele ?? machine.id_unique ?? "Modèle inconnu";
  const reference = machine.nom_modele && machine.nom_modele.trim() ? machine.nom_modele.split(" ").slice(-1)[0] : (machine.id_unique ?? "N/A");
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Image */}
      <div className="p-3 bg-gray-50 flex items-center justify-center h-36">
        {(machine.local_image_path || machine.amazon_image_url) && (
          <img
            src={machine.local_image_path || machine.amazon_image_url || ''}
            alt={machine.amazon_product_title || modelDisplay}
            className="max-w-full max-h-full object-contain"
            onError={(e) => {
              const img = e.currentTarget as HTMLImageElement;
              img.style.display = 'none';
              (img.nextElementSibling as HTMLDivElement | null)?.classList.remove('hidden');
            }}
            onLoad={(e) => {
              const img = e.currentTarget as HTMLImageElement;
              const src = img.currentSrc || img.src || '';
              const looksPlaceholder = /sprite|logo|placeholder|noimage|\/images\/g\//i.test(src);
              const tooSmall = img.naturalWidth < 160 || img.naturalHeight < 160;
              if (looksPlaceholder || tooSmall) {
                img.style.display = 'none';
                (img.nextElementSibling as HTMLDivElement | null)?.classList.remove('hidden');
              }
            }}
          />
        )}
        {/* Brand fallback shown when product image errors or is deemed wrong */}
        <div className={`hidden text-center`}
          aria-hidden="true"
        >
          <div className="mx-auto w-14 h-14 rounded-full bg-white shadow flex items-center justify-center border border-gray-200">
            <span className="text-xs font-bold text-gray-700 uppercase tracking-wide">
              {machine.nom_metteur_sur_le_marche?.slice(0, 8) || 'Marque'}
            </span>
          </div>
          <div className="text-[11px] text-gray-500 mt-1">{modelDisplay}</div>
        </div>
        {!machine.local_image_path && !machine.amazon_image_url && (
          <div className="text-center">
            <div className="text-3xl mb-1">🧺</div>
            <div className="text-[11px] text-gray-500">Lave-linge</div>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="p-4 space-y-2">
        <div className="font-semibold text-gray-900 text-sm line-clamp-2">
          {machine.nom_metteur_sur_le_marche} {modelDisplay}
        </div>

        {/* Attributes as compact table */}
        <table className="w-full text-[12px]">
          <tbody className="divide-y divide-gray-100">
            {typeof machine.note_id === 'number' && (
              <tr>
                <td className="py-1 pr-3 text-gray-500">Durab.</td>
                <td className="py-1 text-right font-semibold">
                  <span className={`${getScoreColor(machine.note_id)} inline-block`}>
                    {(machine.note_id).toFixed(1)}
                  </span>
                </td>
              </tr>
            )}
            {typeof machine.note_reparabilite === 'number' && (
              <tr>
                <td className="py-1 pr-3 text-gray-500">Répar.</td>
                <td className="py-1 text-right font-semibold">
                  <span className={`${getScoreColor(machine.note_reparabilite)} inline-block`}>
                    {(machine.note_reparabilite).toFixed(1)}
                  </span>
                </td>
              </tr>
            )}
            {typeof machine.note_fiabilite === 'number' && (
              <tr>
                <td className="py-1 pr-3 text-gray-500">Fiab.</td>
                <td className="py-1 text-right font-semibold">
                  <span className={`${getScoreColor(machine.note_fiabilite)} inline-block`}>
                    {(machine.note_fiabilite).toFixed(1)}
                  </span>
                </td>
              </tr>
            )}
            {machine.date_calcul && (
              <tr>
                <td className="py-1 pr-3 text-gray-500">Ann.</td>
                <td className="py-1 text-right font-semibold">{String(machine.date_calcul).slice(0,4)}</td>
              </tr>
            )}
            {reference && (
              <tr>
                <td className="py-1 pr-3 text-gray-500">Réf.</td>
                <td className="py-1 text-right font-medium text-gray-700">{reference}</td>
              </tr>
            )}
          </tbody>
        </table>

        {/* Price (if any) */}
        {retailer.price && (
          <div className="text-[15px] font-bold text-green-600">{retailer.price.toFixed(2)} €</div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-1">
          <a
            href={retailer.url}
            target="_blank"
            rel="sponsored"
            className="inline-flex items-center justify-center rounded-md bg-[#1773cf] hover:bg-[#1565c0] text-white text-xs font-semibold py-1.5 px-3 transition-colors"
          >
            Acheter
          </a>
          <a
            href={`/machine/${machine.id}`}
            className="inline-flex items-center justify-center rounded-md border border-gray-200 text-gray-800 hover:bg-gray-50 text-xs font-semibold py-1.5 px-3"
          >
            Voir les détails
          </a>
        </div>
      </div>
    </div>
  );
};

export default function MachineResults({ searchParams }: MachineResultsProps) {
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Memoized search parameters
  const finalParams = useMemo(() => {
    const urlParams: any = { ...searchParams };
    const q: string | undefined = typeof urlParams.q === 'string' ? urlParams.q : Array.isArray(urlParams.q) ? urlParams.q[0] : undefined;

    if (!q) {
      // No free-text query; rely on explicit params from URL (brand, sort_by, etc.)
      return Object.keys(urlParams).length ? urlParams : null;
    }

    const params: any = { limit: 20 };
    const queryLower = q.toLowerCase();

    if (queryLower.includes("réparable") || queryLower.includes("repairability")) {
      params.sort_by = "note_reparabilite";
      params.sort_order = "DESC";
      params.min_repairability = 7.0;
    } else if (queryLower.includes("fiable") || queryLower.includes("reliability")) {
      params.sort_by = "note_fiabilite";
      params.sort_order = "DESC";
      params.min_reliability = 6.0;
    } else if (queryLower.includes("durable") || queryLower.includes("durability")) {
      params.sort_by = "note_id";
      params.sort_order = "DESC";
    } else if (queryLower.includes("excellent") || queryLower.includes("meilleur")) {
      params.min_repairability = 8.0;
      params.min_reliability = 7.0;
      params.sort_by = "note_id";
      params.sort_order = "DESC";
      params.limit = 15;
    } else if (queryLower.includes("bon marché") || queryLower.includes("économique")) {
      params.max_repairability = 6.0;
      params.max_reliability = 6.0;
      params.sort_by = "note_id";
      params.sort_order = "DESC";
      params.limit = 15;
    } else if (queryLower.includes("2025") || queryLower.includes("2024")) {
      const yearMatch = q.match(/\b(20\d{2})\b/);
      if (yearMatch) params.year = parseInt(yearMatch[1]);
      params.sort_by = "date_calcul";
      params.sort_order = "DESC";
    } else if (queryLower.includes("hublot") || queryLower.includes("top") || queryLower.includes("front") || queryLower.includes("charge")) {
      params.q = q;
    } else {
      params.q = q;
    }

    return params;
  }, [searchParams]);

  // Memoized search function
  const searchMachines = useCallback(async () => {
    if (!finalParams) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchMachines(finalParams);
      setResults(data);
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }, [finalParams]);

  useEffect(() => {
    if (!finalParams) {
      setResults(null);
      return;
    }
    searchMachines();
  }, [finalParams, searchMachines]);

  if (!finalParams) {
    return null;
  }

  if (loading) {
    return (
              <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1773cf] mx-auto"></div>
          <p className="mt-4 text-[#637588]">Recherche en cours...</p>
        </div>
              <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1773cf] mx-auto"></div>
          <p className="mt-4 text-[#637588]">Recherche en cours...</p>
        </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600 font-medium">Erreur lors de la recherche</p>
        <p className="text-red-500 text-sm mt-2">{error}</p>
      </div>
    );
  }

  if (!results || results.machines.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-[#637588] text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-[#111418] mb-2">
        <div className="text-[#637588] text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-[#111418] mb-2">
          Aucun lave-linge trouvé
        </h3>
        {finalParams.q && (
          <p className="text-[#637588] mb-4">Aucun résultat pour "{finalParams.q}"</p>
        )}
        <p className="text-sm text-[#637588]">
          Essayez avec d'autres termes de recherche
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold text-[#111418]">
            <h2 className="text-2xl font-bold text-[#111418]">
              Résultats de recherche
            </h2>
            <p className="text-[#637588]">
            <p className="text-[#637588]">
              {results.total} lave-linge{results.total !== 1 ? 's' : ''} trouvé{results.total !== 1 ? 's' : ''}
              {results.total > results.machines.length && (
                <span className="text-sm text-[#637588] ml-2">
                <span className="text-sm text-[#637588] ml-2">
                  (affichage de {results.machines.length} sur {results.total})
                </span>
              )}
            </p>
            {/* Show active filter */}
            <div className="mt-2 space-x-2">
              {finalParams.q && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#1773cf] text-white">
                  🔍 {finalParams.q}
                </span>
              )}
              {finalParams.brand && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#0ea5e9] text-white">
                  🏷️ Marque: {finalParams.brand}
                </span>
              )}
              {finalParams.sort_by === 'price_per_durability' && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[#16a34a] text-white">
                  💶 Meilleur prix/durabilité
                </span>
              )}
            </div>
          </div>
          <div className="text-sm text-[#637588]">
            {finalParams.sort_by === 'note_reparabilite' && 'Trié par réparabilité'}
            {finalParams.sort_by === 'note_fiabilite' && 'Trié par fiabilité'}
            {finalParams.sort_by === 'note_id' && 'Trié par durabilité'}
            {finalParams.sort_by === 'date_calcul' && 'Trié par date'}
            {finalParams.sort_by === 'id' && 'Trié par ID'}
            {finalParams.sort_by === 'price_per_durability' && 'Trié par meilleur rapport prix/durabilité'}
            {!finalParams.sort_by && 'Trié par pertinence'}
          </div>
        </div>
      </div>

      {/* Product Cards Grid - Repairability Index Style */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {results.machines.map((machine, index) => (
          <MachineCard key={machine.id} machine={machine} index={index} />
        ))}
      </div>

      {/* Load More */}
      {results.has_more && (
        <div className="text-center py-6">
          <p className="text-sm text-[#637588] mb-4">
          <p className="text-sm text-[#637588] mb-4">
            Plus de résultats disponibles. Affinez votre recherche pour voir plus de modèles.
          </p>
        </div>
      )}
    </div>
  );
} 