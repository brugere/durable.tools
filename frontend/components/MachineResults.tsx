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
        // Parse the query to extract search parameters
        const params: any = { q: query };
        
        // Check for year in query (e.g., "2025")
        const yearMatch = query.match(/\b(20\d{2})\b/);
        if (yearMatch) {
          params.year = parseInt(yearMatch[1]);
        }
        
        // Check for repairability keywords
        if (query.toLowerCase().includes("repairable") || query.toLowerCase().includes("repairability")) {
          params.sort_by = "note_reparabilite";
          params.sort_order = "DESC";
          params.min_repairability = 7.0; // Only show machines with good repairability
        }
        
        // Check for reliability keywords
        if (query.toLowerCase().includes("reliable") || query.toLowerCase().includes("reliability")) {
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
    return (
      <div className="text-center text-gray-500 mt-8">
        <p>Enter a search query to find washing machines</p>
        <p className="text-sm mt-2">
          Examples: "Samsung", "most repairable", "2025", "LG reliable"
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center mt-8">
        <p>Searching for washing machines...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 mt-8">
        <p>Error: {error}</p>
      </div>
    );
  }

  if (!results || results.machines.length === 0) {
    return (
      <div className="text-center text-gray-500 mt-8">
        <p>No washing machines found for "{query}"</p>
        <p className="text-sm mt-2">Try a different search term</p>
      </div>
    );
  }

  return (
    <div className="mt-8">
      <div className="mb-4">
        <h2 className="text-xl font-bold">
          Found {results.total} washing machine{results.total !== 1 ? 's' : ''}
        </h2>
        {results.total > results.machines.length && (
          <p className="text-sm text-gray-600">
            Showing {results.machines.length} of {results.total} results
          </p>
        )}
      </div>

      <div className="grid gap-4">
        {results.machines.map((machine) => (
          <div key={machine.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{machine.nom_modele}</h3>
                <p className="text-gray-600">{machine.nom_metteur_sur_le_marche}</p>
                {machine.date_calcul && (
                  <p className="text-sm text-gray-500">
                    Date: {new Date(machine.date_calcul).toLocaleDateString()}
                  </p>
                )}
              </div>
              
              <div className="text-right">
                <div className="flex gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Repairability</p>
                    <p className="font-bold text-green-600">
                      {machine.note_reparabilite?.toFixed(1) || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Reliability</p>
                    <p className="font-bold text-blue-600">
                      {machine.note_fiabilite?.toFixed(1) || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Overall</p>
                    <p className="font-bold text-purple-600">
                      {machine.note_id?.toFixed(1) || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            {machine.url_tableau_detail_notation && (
              <div className="mt-3">
                <a
                  href={machine.url_tableau_detail_notation}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  View detailed report →
                </a>
              </div>
            )}
          </div>
        ))}
      </div>

      {results.has_more && (
        <div className="text-center mt-6">
          <p className="text-sm text-gray-600">
            More results available. Try refining your search.
          </p>
        </div>
      )}
    </div>
  );
} 