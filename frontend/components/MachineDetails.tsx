"use client";

import { fetchMachineDetails } from "@/lib/api";
import { useState, useEffect } from "react";
import { buildAmazonAffiliateSearchUrl } from "@/lib/affiliate";
import { useRouter } from "next/navigation";
import ScoreRadarChart from "./ScoreRadarChart";
import SimilarMachines from "./SimilarMachines";

interface MachineDetails {
  id: number;
  id_unique: string;
  nom_modele: string;
  nom_metteur_sur_le_marche: string;
  date_calcul: string;
  note_reparabilite: number;
  note_fiabilite: number;
  note_id: number;
  categorie_produit: string;
  url_tableau_detail_notation?: string;
  
  // Detailed scores
  note_A_c1?: number;
  note_A_c2?: number;
  note_A_c3?: number;
  note_A_c4?: number;
  note_B_c1?: number;
  note_B_c2?: number;
  note_B_c3?: number;
  
  // Documentation
  accessibilite_compteur_usage?: string;
  lien_documentation_professionnels?: string;
  lien_documentation_particuliers?: string;
  
  // Spare parts data
  nom_piece_1_liste_2?: string;
  nom_piece_2_liste_2?: string;
  nom_piece_3_liste_2?: string;
  nom_piece_4_liste_2?: string;
  nom_piece_5_liste_2?: string;
  etape_demontage_piece_1_liste_2?: string;
  etape_demontage_piece_2_liste_2?: string;
  etape_demontage_piece_3_liste_2?: string;
  etape_demontage_piece_4_liste_2?: string;
  etape_demontage_piece_5_liste_2?: string;
}

interface MachineDetailsProps {
  machineId: number;
}

// Helper function to get score color
function getScoreColor(score: number) {
  // Scale from red to green with 8.5 as middle point
  if (score >= 9.0) return "text-green-600 bg-green-50";      // Excellent (9.0-10.0)
  if (score >= 8.5) return "text-green-500 bg-green-50";      // Very good (8.5-8.9)
  if (score >= 7.5) return "text-green-400 bg-green-50";      // Good (7.5-8.4)
  if (score >= 6.5) return "text-yellow-500 bg-yellow-50";    // Average (6.5-7.4)
  if (score >= 5.5) return "text-yellow-600 bg-yellow-50";    // Below average (5.5-6.4)
  if (score >= 4.5) return "text-orange-500 bg-orange-50";    // Poor (4.5-5.4)
  if (score >= 3.5) return "text-orange-600 bg-orange-50";    // Very poor (3.5-4.4)
  return "text-red-600 bg-red-50";                            // Very bad (0.0-3.4)
}

// Helper function to get score level
function getScoreLevel(score: number) {
  if (score >= 8.0) return "Excellent";
  if (score >= 6.0) return "Bon";
  if (score >= 4.0) return "Moyen";
  return "Faible";
}

// Build an Amazon affiliate search link for brand + model
function getAffiliateLink(brand: string, model: string) {
  const url = buildAmazonAffiliateSearchUrl({ brand, model, locale: "fr" });
  return { name: "Amazon", url, icon: "🛒" } as const;
}

export default function MachineDetails({ machineId }: MachineDetailsProps) {
  const [machine, setMachine] = useState<MachineDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const loadMachineDetails = async () => {
      try {
        const data = await fetchMachineDetails(machineId);
        setMachine(data);
      } catch (e: any) {
        setError(e.message || String(e));
      } finally {
        setLoading(false);
      }
    };

    loadMachineDetails();
  }, [machineId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des détails...</p>
        </div>
      </div>
    );
  }

  if (error || !machine) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-sm p-8 text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Erreur de chargement
          </h2>
          <p className="text-gray-600 mb-4">
            Impossible de charger les détails de cette machine
          </p>
          <button
            onClick={() => router.back()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Retour
          </button>
        </div>
      </div>
    );
  }

  const retailer = getAffiliateLink(machine.nom_metteur_sur_le_marche, machine.nom_modele);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <button
              onClick={() => router.back()}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <span className="mr-2">←</span>
              Retour aux résultats
            </button>
            <div className="text-sm text-gray-500">
              Détails du produit
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Main Product Info */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Product Image & Basic Info */}
            <div className="lg:col-span-1">
              <div className="bg-gray-100 rounded-lg p-8 text-center mb-6">
                <div className="text-8xl mb-4">🏠</div>
                <div className="text-gray-500">Lave-linge</div>
              </div>
              
              <div className="space-y-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  {machine.nom_modele}
                </h1>
                <p className="text-lg text-gray-600">
                  {machine.nom_metteur_sur_le_marche}
                </p>
                <p className="text-sm text-gray-500">
                  Référence: {machine.id_unique}
                </p>
                <p className="text-sm text-gray-500">
                  Date d'évaluation: {new Date(machine.date_calcul).toLocaleDateString('fr-FR')}
                </p>
              </div>
            </div>

            {/* Scores Overview */}
            <div className="lg:col-span-2">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Indices de durabilité
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Repairability Score */}
                <div className={`rounded-lg p-6 ${getScoreColor(machine.note_reparabilite || 0)}`}>
                  <div className="text-center">
                    <div className="text-4xl font-bold mb-2">
                      {machine.note_reparabilite?.toFixed(1) || 'N/A'}/10
                    </div>
                    <div className="text-sm font-medium mb-1">
                      Réparabilité
                    </div>
                    <div className="text-xs opacity-75">
                      {getScoreLevel(machine.note_reparabilite || 0)}
                    </div>
                  </div>
                </div>

                {/* Reliability Score */}
                <div className={`rounded-lg p-6 ${getScoreColor(machine.note_fiabilite || 0)}`}>
                  <div className="text-center">
                    <div className="text-4xl font-bold mb-2">
                      {machine.note_fiabilite?.toFixed(1) || 'N/A'}/10
                    </div>
                    <div className="text-sm font-medium mb-1">
                      Fiabilité
                    </div>
                    <div className="text-xs opacity-75">
                      {getScoreLevel(machine.note_fiabilite || 0)}
                    </div>
                  </div>
                </div>

                {/* Global Score */}
                <div className={`rounded-lg p-6 ${getScoreColor(machine.note_id || 0)}`}>
                  <div className="text-center">
                    <div className="text-4xl font-bold mb-2">
                      {machine.note_id?.toFixed(1) || 'N/A'}/10
                    </div>
                    <div className="text-sm font-medium mb-1">
                      Note globale
                    </div>
                    <div className="text-xs opacity-75">
                      {getScoreLevel(machine.note_id || 0)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-6 flex flex-col sm:flex-row gap-4">
                <a
                  href={retailer.url}
                  target="_blank"
                  rel="noopener noreferrer sponsored"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-6 rounded-lg text-center transition-colors flex items-center justify-center"
                >
                  <span className="mr-2">{retailer.icon}</span>
                  Acheter sur {retailer.name}
                </a>
                
                {machine.url_tableau_detail_notation && (
                  <a
                    href={machine.url_tableau_detail_notation}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg text-center transition-colors"
                  >
                    📊 Voir le rapport complet
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Scores */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Détail des scores
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Category A Scores */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Catégorie A - Critères de réparabilité
              </h3>
              <div className="space-y-3">
                {machine.note_A_c1 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">C1 - Démontabilité</span>
                    <span className="font-semibold">{machine.note_A_c1.toFixed(1)}/10</span>
                  </div>
                )}
                {machine.note_A_c2 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">C2 - Disponibilité des pièces</span>
                    <span className="font-semibold">{machine.note_A_c2.toFixed(1)}/10</span>
                  </div>
                )}
                {machine.note_A_c3 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">C3 - Prix des pièces</span>
                    <span className="font-semibold">{machine.note_A_c3.toFixed(1)}/10</span>
                  </div>
                )}
                {machine.note_A_c4 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">C4 - Documentation</span>
                    <span className="font-semibold">{machine.note_A_c4.toFixed(1)}/10</span>
                  </div>
                )}
              </div>
            </div>

            {/* Category B Scores */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Catégorie B - Critères de fiabilité
              </h3>
              <div className="space-y-3">
                {machine.note_B_c1 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">C1 - Robustesse</span>
                    <span className="font-semibold">{machine.note_B_c1.toFixed(1)}/10</span>
                  </div>
                )}
                {machine.note_B_c2 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">C2 - Fiabilité</span>
                    <span className="font-semibold">{machine.note_B_c2.toFixed(1)}/10</span>
                  </div>
                )}
                {machine.note_B_c3 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">C3 - Durabilité</span>
                    <span className="font-semibold">{machine.note_B_c3.toFixed(1)}/10</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Score Visualization */}
        <div className="mb-8">
          <ScoreRadarChart 
            scores={{
              repairability: machine.note_reparabilite || 0,
              reliability: machine.note_fiabilite || 0,
              global: machine.note_id || 0,
              demontability: machine.note_A_c1,
              partsAvailability: machine.note_A_c2,
              partsPrice: machine.note_A_c3,
              documentation: machine.note_A_c4
            }}
          />
        </div>

        {/* Documentation & Accessibility */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Documentation et accessibilité
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Documentation Links */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Documentation
              </h3>
              <div className="space-y-3">
                {machine.lien_documentation_professionnels && (
                  <a
                    href={machine.lien_documentation_professionnels}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                  >
                    <div className="flex items-center">
                      <span className="text-blue-600 mr-2">🔧</span>
                      <span className="text-blue-900 font-medium">Documentation professionnelle</span>
                    </div>
                  </a>
                )}
                
                {machine.lien_documentation_particuliers && (
                  <a
                    href={machine.lien_documentation_particuliers}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
                  >
                    <div className="flex items-center">
                      <span className="text-green-600 mr-2">👤</span>
                      <span className="text-green-900 font-medium">Documentation particuliers</span>
                    </div>
                  </a>
                )}
              </div>
            </div>

            {/* Accessibility */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Accessibilité
              </h3>
              <div className="space-y-3">
                {machine.accessibilite_compteur_usage && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <span className="text-gray-600 mr-2">📊</span>
                      <span className="text-gray-900">Compteur d'usage: {machine.accessibilite_compteur_usage}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Critical Parts */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Pièces critiques pour la réparation
          </h2>
          
          <div className="space-y-6">
            {machine.nom_piece_1_liste_2 && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-yellow-800 font-medium mb-2">Pièce 1: {machine.nom_piece_1_liste_2}</div>
                    {machine.etape_demontage_piece_1_liste_2 && (
                      <div className="text-sm text-yellow-700">
                        <span className="font-medium">Étapes de démontage:</span> {machine.etape_demontage_piece_1_liste_2}
                      </div>
                    )}
                  </div>
                  <div className="text-yellow-600 text-2xl ml-4">🔧</div>
                </div>
              </div>
            )}
            
            {machine.nom_piece_2_liste_2 && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-yellow-800 font-medium mb-2">Pièce 2: {machine.nom_piece_2_liste_2}</div>
                    {machine.etape_demontage_piece_2_liste_2 && (
                      <div className="text-sm text-yellow-700">
                        <span className="font-medium">Étapes de démontage:</span> {machine.etape_demontage_piece_2_liste_2}
                      </div>
                    )}
                  </div>
                  <div className="text-yellow-600 text-2xl ml-4">🔧</div>
                </div>
              </div>
            )}
            
            {machine.nom_piece_3_liste_2 && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-yellow-800 font-medium mb-2">Pièce 3: {machine.nom_piece_3_liste_2}</div>
                    {machine.etape_demontage_piece_3_liste_2 && (
                      <div className="text-sm text-yellow-700">
                        <span className="font-medium">Étapes de démontage:</span> {machine.etape_demontage_piece_3_liste_2}
                      </div>
                    )}
                  </div>
                  <div className="text-yellow-600 text-2xl ml-4">🔧</div>
                </div>
              </div>
            )}
            
            {machine.nom_piece_4_liste_2 && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-yellow-800 font-medium mb-2">Pièce 4: {machine.nom_piece_4_liste_2}</div>
                    {machine.etape_demontage_piece_4_liste_2 && (
                      <div className="text-sm text-yellow-700">
                        <span className="font-medium">Étapes de démontage:</span> {machine.etape_demontage_piece_4_liste_2}
                      </div>
                    )}
                  </div>
                  <div className="text-yellow-600 text-2xl ml-4">🔧</div>
                </div>
              </div>
            )}
            
            {machine.nom_piece_5_liste_2 && (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-yellow-800 font-medium mb-2">Pièce 5: {machine.nom_piece_5_liste_2}</div>
                    {machine.etape_demontage_piece_5_liste_2 && (
                      <div className="text-sm text-yellow-700">
                        <span className="font-medium">Étapes de démontage:</span> {machine.etape_demontage_piece_5_liste_2}
                      </div>
                    )}
                  </div>
                  <div className="text-yellow-600 text-2xl ml-4">🔧</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Environmental Impact */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Impact environnemental
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl mb-2">🌱</div>
              <div className="font-medium text-green-900 mb-1">Durabilité</div>
              <div className="text-sm text-green-700">
                Machine conçue pour durer
              </div>
            </div>
            
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-3xl mb-2">♻️</div>
              <div className="font-medium text-blue-900 mb-1">Réparabilité</div>
              <div className="text-sm text-blue-700">
                Facile à réparer et maintenir
              </div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-3xl mb-2">🌍</div>
              <div className="font-medium text-purple-900 mb-1">Économie circulaire</div>
              <div className="text-sm text-purple-700">
                Réduction des déchets
              </div>
            </div>
          </div>
        </div>
        
        {/* Similar Machines */}
        <div className="mb-8">
          <SimilarMachines 
            currentMachine={{
              id: machine.id,
              nom_metteur_sur_le_marche: machine.nom_metteur_sur_le_marche,
              note_reparabilite: machine.note_reparabilite || 0
            }}
          />
        </div>
      </div>
    </div>
  );
} 