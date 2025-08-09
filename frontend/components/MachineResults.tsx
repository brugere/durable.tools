"use client";

import { fetchMachines } from "@/lib/api";
import { useState, useEffect, useMemo, useCallback } from "react";
import { buildAmazonAffiliateSearchUrl } from "@/lib/affiliate";

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
}

interface SearchResults {
  machines: Machine[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

interface MachineResultsProps {
  query?: string;
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

// Build an Amazon affiliate search link for brand + model
const getAffiliateLink = (brand: string, model?: string | null) => {
  const url = buildAmazonAffiliateSearchUrl({ brand, model, locale: "fr" });
  return { name: "Amazon", url, icon: "🛒" } as const;
};

// Memoized machine card component
const MachineCard = ({ machine, index }: { machine: Machine; index: number }) => {
  const retailer = useMemo(
    () => getAffiliateLink(machine.nom_metteur_sur_le_marche, machine.nom_modele ?? machine.id_unique ?? ""),
    [machine.nom_metteur_sur_le_marche, machine.nom_modele, machine.id_unique]
  );

  const modelDisplay = machine.nom_modele ?? machine.id_unique ?? "Modèle inconnu";
  const reference = machine.nom_modele && machine.nom_modele.trim() ? machine.nom_modele.split(" ").slice(-1)[0] : (machine.id_unique ?? "N/A");
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Top Section - Score Display */}
      <div className="bg-gray-50 p-4 text-center border-b border-gray-200">
        <div className="flex items-center justify-center mb-2">
          <span className="text-green-600 text-2xl mr-2">⚙️🔧</span>
        </div>
        <div className={`text-3xl font-bold ${getScoreColor((machine.note_reparabilite ?? 0))}`}>
          {(machine.note_reparabilite ?? 0).toFixed(1)}/10
        </div>
        <div className="text-sm text-gray-600 font-medium">
          INDICE DE RÉPARABILITÉ
        </div>
      </div>

      {/* Middle Section - Product Image Placeholder */}
      <div className="p-4 bg-gray-100 flex items-center justify-center h-32">
        <div className="text-center">
          <div className="text-4xl mb-2">🏠</div>
          <div className="text-xs text-gray-500">Lave-linge</div>
        </div>
      </div>

      {/* Bottom Section - Product Details */}
      <div className="p-4">
        <div className="text-xs font-medium mb-2 text-gray-700">
          INDICE DE RÉPARABILITÉ LAVE LINGE HUBLOT
        </div>
        <div className="font-bold text-gray-900 mb-3 text-sm">
          {modelDisplay}
        </div>
        
        {/* Product Info Table */}
        <div className="space-y-1 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">Marque:</span>
            <span className="font-medium">{machine.nom_metteur_sur_le_marche}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Référence:</span>
            <span className="font-medium">{reference}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Date:</span>
            <span className="font-medium">
              {machine.date_calcul ? new Date(machine.date_calcul).toLocaleDateString('fr-FR') : 'N/A'}
            </span>
          </div>
        </div>

        {/* Additional Scores */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="text-center">
              <div className={`font-bold ${getScoreColor((machine.note_fiabilite ?? 0))}`}>
                {(machine.note_fiabilite ?? 0).toFixed(1) || 'N/A'}
              </div>
              <div className="text-gray-500">Fiabilité</div>
            </div>
            <div className="text-center">
              <div className={`font-bold ${getScoreColor((machine.note_id ?? 0))}`}>
                {(machine.note_id ?? 0).toFixed(1) || 'N/A'}
              </div>
              <div className="text-gray-500">Note globale</div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-3 space-y-2">
          {/* Buy Button */}
          <a
            href={retailer.url}
            target="_blank"
            rel="noopener noreferrer sponsored"
            className="w-full bg-green-600 hover:bg-green-700 text-white text-xs font-medium py-2 px-3 rounded block text-center transition-colors duration-200 flex items-center justify-center"
          >
            <span className="mr-1">{retailer.icon}</span>
            Acheter sur {retailer.name}
          </a>
          
          {/* Report Button */}
          {machine.url_tableau_detail_notation && (
            <a
              href={machine.url_tableau_detail_notation}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium py-2 px-3 rounded block text-center transition-colors duration-200"
            >
              Voir le rapport
            </a>
          )}
          
          {/* Details Button */}
          {machine.id && (
            <a
              href={`/machine/${machine.id}`}
              className="w-full bg-gray-600 hover:bg-gray-700 text-white text-xs font-medium py-2 px-3 rounded block text-center transition-colors duration-200"
            >
              📋 Voir les détails
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

export default function MachineResults({ query }: MachineResultsProps) {
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Memoized search parameters
  const searchParams = useMemo(() => {
    if (!query) return null;
    
    const params: any = {};
    const queryLower = query.toLowerCase();
    
    // Enhanced search logic
    if (queryLower.includes("réparable") || queryLower.includes("repairability")) {
      params.sort_by = "note_reparabilite";
      params.sort_order = "DESC";
      params.min_repairability = 7.0;
      params.limit = 20;
    } else if (queryLower.includes("fiable") || queryLower.includes("reliability")) {
      params.sort_by = "note_fiabilite";
      params.sort_order = "DESC";
      params.min_reliability = 6.0;
      params.limit = 20;
    } else if (queryLower.includes("durable") || queryLower.includes("durability")) {
      params.sort_by = "note_id";
      params.sort_order = "DESC";
      params.limit = 20;
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
      const yearMatch = query.match(/\b(20\d{2})\b/);
      if (yearMatch) {
        params.year = parseInt(yearMatch[1]);
      }
      params.sort_by = "date_calcul";
      params.sort_order = "DESC";
      params.limit = 20;
    } else if (queryLower.includes("samsung") || queryLower.includes("lg") || 
               queryLower.includes("bosch") || queryLower.includes("whirlpool") ||
               queryLower.includes("electrolux") || queryLower.includes("candy")) {
      params.brand = query;
      params.limit = 20;
    } else if (queryLower.includes("hublot") || queryLower.includes("top") ||
               queryLower.includes("front") || queryLower.includes("charge")) {
      params.q = query;
      params.limit = 20;
    } else {
      params.q = query;
      params.limit = 20;
    }
    
    return params;
  }, [query]);

  // Memoized search function
  const searchMachines = useCallback(async () => {
    if (!searchParams) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchMachines(searchParams);
      setResults(data);
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  useEffect(() => {
    if (!query) {
      setResults(null);
      return;
    }

    searchMachines();
  }, [query, searchMachines]);

  if (!query) {
    return null;
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Recherche en cours...</p>
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
        <div className="text-gray-400 text-6xl mb-4">🔍</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Aucun lave-linge trouvé
        </h3>
        <p className="text-gray-600 mb-4">
          Aucun résultat pour "{query}"
        </p>
        <p className="text-sm text-gray-500">
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
            <h2 className="text-2xl font-bold text-gray-900">
              Résultats de recherche
            </h2>
            <p className="text-gray-600">
              {results.total} lave-linge{results.total !== 1 ? 's' : ''} trouvé{results.total !== 1 ? 's' : ''}
              {results.total > results.machines.length && (
                <span className="text-sm text-gray-500 ml-2">
                  (affichage de {results.machines.length} sur {results.total})
                </span>
              )}
            </p>
            {/* Show active filter */}
            {query && (
              <div className="mt-2">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  🔍 Filtre actif: "{query}"
                </span>
              </div>
            )}
          </div>
          <div className="text-sm text-gray-500">
            {query?.toLowerCase().includes('réparable') && 'Trié par réparabilité'}
            {query?.toLowerCase().includes('fiable') && 'Trié par fiabilité'}
            {query?.toLowerCase().includes('excellent') && 'Trié par score global'}
            {query?.toLowerCase().includes('durable') && 'Trié par durabilité'}
            {!query?.toLowerCase().includes('réparable') && !query?.toLowerCase().includes('fiable') && 
             !query?.toLowerCase().includes('excellent') && !query?.toLowerCase().includes('durable') && 
             'Trié par pertinence'}
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
          <p className="text-sm text-gray-600 mb-4">
            Plus de résultats disponibles. Affinez votre recherche pour voir plus de modèles.
          </p>
        </div>
      )}
    </div>
  );
} 