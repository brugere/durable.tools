"use client";

import { fetchMachines } from "@/lib/api";
import { useState, useEffect } from "react";
import Link from "next/link";

interface Machine {
  id?: number | null;
  nom_modele?: string | null;
  nom_metteur_sur_le_marche: string;
  note_reparabilite?: number | null;
  note_fiabilite?: number | null;
  note_id?: number | null;
}

interface SimilarMachinesProps {
  currentMachine: {
    id?: number | null;
    nom_metteur_sur_le_marche: string;
    note_reparabilite?: number | null;
  };
}

// Helper function to get score color
function getScoreColor(score: number | null | undefined) {
  if (!score) return "text-gray-400";
  if (score >= 8.0) return "text-green-600";
  if (score >= 6.0) return "text-blue-600";
  if (score >= 4.0) return "text-yellow-600";
  return "text-red-600";
}

export default function SimilarMachines({ currentMachine }: SimilarMachinesProps) {
  const [similarMachines, setSimilarMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSimilarMachines = async () => {
      try {
        // Search for machines from the same brand with similar repairability scores
        const data = await fetchMachines({
          brand: currentMachine.nom_metteur_sur_le_marche,
          limit: 5
        });
        
        // Filter out the current machine and get top 4 similar ones
        const filtered = data.machines
          .filter((machine: Machine) => machine.id !== currentMachine.id)
          .slice(0, 4);
        
        setSimilarMachines(filtered);
      } catch (error) {
        console.error("Failed to load similar machines:", error);
      } finally {
        setLoading(false);
      }
    };

    loadSimilarMachines();
  }, [currentMachine]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Machines similaires
        </h2>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  if (similarMachines.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Machines similaires
        </h2>
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-2">🔍</div>
          <p className="text-gray-600">Aucune machine similaire trouvée</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">
        Machines similaires de {currentMachine.nom_metteur_sur_le_marche}
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {similarMachines.map((machine) => (
          machine.id ? (
            <Link
              key={machine.id}
              href={`/machine/${machine.id}`}
              className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200"
            >
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 text-sm mb-1">
                  {machine.nom_modele}
                </h3>
                <p className="text-xs text-gray-500">
                  {machine.nom_metteur_sur_le_marche}
                </p>
              </div>
              <div className="text-right">
                <div className={`text-lg font-bold ${getScoreColor(machine.note_reparabilite)}`}>
                  {machine.note_reparabilite?.toFixed(1) || 'N/A'}
                </div>
                <div className="text-xs text-gray-500">Réparabilité</div>
              </div>
            </div>
            
            <div className="flex justify-between text-xs text-gray-600">
              <span>Fiabilité: {machine.note_fiabilite?.toFixed(1) || 'N/A'}</span>
              <span>Global: {machine.note_id?.toFixed(1) || 'N/A'}</span>
            </div>
          </Link>
          ) : null
        ))}
      </div>
      
      <div className="mt-6 text-center">
        <Link
          href={`/?q=${encodeURIComponent(currentMachine.nom_metteur_sur_le_marche)}`}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Voir tous les modèles {currentMachine.nom_metteur_sur_le_marche} →
        </Link>
      </div>
    </div>
  );
} 