"use client";

import { fetchMachines } from "@/lib/api";
import { useState, useEffect } from "react";

interface Machine {
  id: number;
  nom_modele: string;
  nom_metteur_sur_le_marche: string;
  date_calcul: string;
  note_reparabilite: number;
  note_fiabilite: number;
  note_id: number;
  categorie_produit: string;
  url_tableau_detail_notation?: string;
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

// Helper function to get score color
function getScoreColor(score: number) {
  if (score >= 8.0) return "text-green-600";
  if (score >= 6.0) return "text-blue-600";
  if (score >= 4.0) return "text-yellow-600";
  return "text-red-600";
}

// Helper function to get category color
function getCategoryColor(index: number) {
  const colors = [
    "text-purple-600",
    "text-blue-600", 
    "text-red-600",
    "text-orange-600",
    "text-green-600",
    "text-indigo-600"
  ];
  return colors[index % colors.length];
}

// Helper function to generate purchase URLs based on brand and model
function getPurchaseUrl(brand: string, model: string): string {
  const brandLower = brand.toLowerCase();
  const modelLower = model.toLowerCase();
  
  // Common French retailers
  const retailers = [
    {
      name: "Boulanger",
      url: "https://www.boulanger.com/recherche?q=",
      icon: "🛒"
    },
    {
      name: "Darty",
      url: "https://www.darty.com/nav/recherche?text=",
      icon: "🏪"
    },
    {
      name: "Amazon",
      url: "https://www.amazon.fr/s?k=",
      icon: "📦"
    },
    {
      name: "LDLC",
      url: "https://www.ldlc.com/recherche/",
      icon: "💻"
    }
  ];

  // Generate search query
  const searchQuery = encodeURIComponent(`${brand} ${model} lave-linge`);
  
  // Return the first retailer (Boulanger) as default
  return `${retailers[0].url}${searchQuery}`;
}

// Helper function to get retailer info
function getRetailerInfo(brand: string, model: string) {
  const brandLower = brand.toLowerCase();
  const modelLower = model.toLowerCase();
  
  // Brand-specific retailers with correct search URLs
  if (brandLower.includes("samsung")) {
    return {
      name: "Samsung Store",
      url: `https://www.samsung.com/fr/search/?searchvalue=${encodeURIComponent(model)}`,
      icon: "📱"
    };
  }
  
  if (brandLower.includes("lg")) {
    return {
      name: "LG Store", 
      url: `https://www.lg.com/fr/search?search=${encodeURIComponent(model)}`,
      icon: "📺"
    };
  }
  
  if (brandLower.includes("bosch") || brandLower.includes("siemens")) {
    return {
      name: "Bosch Home",
      url: `https://www.bosch-home.fr/fr/search?search=${encodeURIComponent(model)}`,
      icon: "🏠"
    };
  }
  
  if (brandLower.includes("whirlpool") || brandLower.includes("hotpoint")) {
    return {
      name: "Whirlpool Store",
      url: `https://www.whirlpool.fr/search?q=${encodeURIComponent(model)}`,
      icon: "⚡"
    };
  }
  
  if (brandLower.includes("electrolux") || brandLower.includes("aeg")) {
    return {
      name: "Electrolux Store",
      url: `https://www.electrolux.fr/search?q=${encodeURIComponent(model)}`,
      icon: "🔌"
    };
  }
  
  if (brandLower.includes("candy") || brandLower.includes("hoover")) {
    return {
      name: "Candy Store",
      url: `https://www.candy.fr/search?q=${encodeURIComponent(model)}`,
      icon: "🍬"
    };
  }
  
  // Major French retailers as fallback
  const retailers = [
    {
      name: "Boulanger",
      url: `https://www.boulanger.com/recherche?q=${encodeURIComponent(model)}`,
      icon: "🛒"
    },
    {
      name: "Darty",
      url: `https://www.darty.com/nav/recherche?text=${encodeURIComponent(model)}`,
      icon: "🏪"
    },
    {
      name: "Amazon",
      url: `https://www.amazon.fr/s?k=${encodeURIComponent(model)}`,
      icon: "📦"
    },
    {
      name: "LDLC",
      url: `https://www.ldlc.com/recherche/${encodeURIComponent(model)}/`,
      icon: "💻"
    },
    {
      name: "Rue du Commerce",
      url: `https://www.rueducommerce.fr/recherche?q=${encodeURIComponent(model)}`,
      icon: "🛍️"
    }
  ];
  
  // Return Boulanger as default
  return retailers[0];
}

export default function MachineResults({ query }: MachineResultsProps) {
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query) {
      setResults(null);
      return;
    }

    const searchMachines = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const params: any = { q: query };
        
        // Check for year in query (e.g., "2025")
        const yearMatch = query.match(/\b(20\d{2})\b/);
        if (yearMatch) {
          params.year = parseInt(yearMatch[1]);
        }
        
        // Check for repairability keywords
        if (query.toLowerCase().includes("réparable") || query.toLowerCase().includes("repairability")) {
          params.sort_by = "note_reparabilite";
          params.sort_order = "DESC";
          params.min_repairability = 7.0;
        }
        
        // Check for reliability keywords
        if (query.toLowerCase().includes("fiable") || query.toLowerCase().includes("reliability")) {
          params.sort_by = "note_fiabilite";
          params.sort_order = "DESC";
        }
        
        const data = await fetchMachines(params);
        setResults(data);
      } catch (e: any) {
        setError(e.message || String(e));
      } finally {
        setLoading(false);
      }
    };

    searchMachines();
  }, [query]);

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
          </div>
          <div className="text-sm text-gray-500">
            Trié par pertinence
          </div>
        </div>
      </div>

      {/* Product Cards Grid - Repairability Index Style */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {results.machines.map((machine, index) => {
          const retailer = getRetailerInfo(machine.nom_metteur_sur_le_marche, machine.nom_modele);
          
          return (
            <div key={machine.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              {/* Top Section - Score Display */}
              <div className="bg-gray-50 p-4 text-center border-b border-gray-200">
                <div className="flex items-center justify-center mb-2">
                  <span className="text-green-600 text-2xl mr-2">⚙️🔧</span>
                </div>
                <div className={`text-3xl font-bold ${getScoreColor(machine.note_reparabilite || 0)}`}>
                  {machine.note_reparabilite?.toFixed(1) || 'N/A'}/10
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
                <div className={`text-xs font-medium mb-2 ${getCategoryColor(index)}`}>
                  INDICE DE RÉPARABILITÉ LAVE LINGE HUBLOT
                </div>
                <div className="font-bold text-gray-900 mb-3 text-sm">
                  {machine.nom_modele}
                </div>
                
                {/* Product Info Table */}
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Marque:</span>
                    <span className="font-medium">{machine.nom_metteur_sur_le_marche}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Référence:</span>
                    <span className="font-medium">{machine.nom_modele.split(' ').slice(-1)[0]}</span>
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
                      <div className="font-bold text-blue-600">
                        {machine.note_fiabilite?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-gray-500">Fiabilité</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-purple-600">
                        {machine.note_id?.toFixed(1) || 'N/A'}
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
                    rel="noopener noreferrer"
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
                </div>
              </div>
            </div>
          );
        })}
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