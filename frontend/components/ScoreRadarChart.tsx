interface ScoreRadarChartProps {
  scores: {
    repairability: number;
    reliability: number;
    global: number;
    demontability?: number;
    partsAvailability?: number;
    partsPrice?: number;
    documentation?: number;
  };
}

// Helper function to get score color for progress bars
function getScoreBarColor(score: number) {
  // Scale from red to green with 8.5 as middle point
  if (score >= 9.0) return "bg-green-600";      // Excellent (9.0-10.0)
  if (score >= 8.5) return "bg-green-500";      // Very good (8.5-8.9)
  if (score >= 7.5) return "bg-green-400";      // Good (7.5-8.4)
  if (score >= 6.5) return "bg-yellow-500";     // Average (6.5-7.4)
  if (score >= 5.5) return "bg-yellow-600";     // Below average (5.5-6.4)
  if (score >= 4.5) return "bg-orange-500";     // Poor (4.5-5.4)
  if (score >= 3.5) return "bg-orange-600";     // Very poor (3.5-4.4)
  return "bg-red-600";                           // Very bad (0.0-3.4)
}

export default function ScoreRadarChart({ scores }: ScoreRadarChartProps) {
  const maxScore = 10;
  
  // Calculate percentages for visualization
  const getPercentage = (score: number) => (score / maxScore) * 100;
  
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Visualisation des scores
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Main Scores */}
        <div>
          <h4 className="text-md font-medium text-gray-700 mb-3">Scores principaux</h4>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Réparabilité</span>
                <span className="font-medium">{scores.repairability.toFixed(1)}/10</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`${getScoreBarColor(scores.repairability)} h-2 rounded-full transition-all duration-300`}
                  style={{ width: `${getPercentage(scores.repairability)}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Fiabilité</span>
                <span className="font-medium">{scores.reliability.toFixed(1)}/10</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`${getScoreBarColor(scores.reliability)} h-2 rounded-full transition-all duration-300`}
                  style={{ width: `${getPercentage(scores.reliability)}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Note globale</span>
                <span className="font-medium">{scores.global.toFixed(1)}/10</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`${getScoreBarColor(scores.global)} h-2 rounded-full transition-all duration-300`}
                  style={{ width: `${getPercentage(scores.global)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Detailed Scores */}
        <div>
          <h4 className="text-md font-medium text-gray-700 mb-3">Scores détaillés</h4>
          <div className="space-y-3">
            {scores.demontability && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Démontabilité</span>
                  <span className="font-medium">{scores.demontability.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`${getScoreBarColor(scores.demontability)} h-2 rounded-full transition-all duration-300`}
                    style={{ width: `${getPercentage(scores.demontability)}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {scores.partsAvailability && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Disponibilité pièces</span>
                  <span className="font-medium">{scores.partsAvailability.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`${getScoreBarColor(scores.partsAvailability)} h-2 rounded-full transition-all duration-300`}
                    style={{ width: `${getPercentage(scores.partsAvailability)}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {scores.partsPrice && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Prix des pièces</span>
                  <span className="font-medium">{scores.partsPrice.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`${getScoreBarColor(scores.partsPrice)} h-2 rounded-full transition-all duration-300`}
                    style={{ width: `${getPercentage(scores.partsPrice)}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {scores.documentation && (
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Documentation</span>
                  <span className="font-medium">{scores.documentation.toFixed(1)}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`${getScoreBarColor(scores.documentation)} h-2 rounded-full transition-all duration-300`}
                    style={{ width: `${getPercentage(scores.documentation)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Score Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-600 rounded mr-2"></div>
            <span>Excellent (9.0-10.0)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
            <span>Très bon (8.5-8.9)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-400 rounded mr-2"></div>
            <span>Bon (7.5-8.4)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-500 rounded mr-2"></div>
            <span>Moyen (6.5-7.4)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-600 rounded mr-2"></div>
            <span>En dessous (5.5-6.4)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-orange-500 rounded mr-2"></div>
            <span>Faible (4.5-5.4)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-orange-600 rounded mr-2"></div>
            <span>Très faible (3.5-4.4)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-600 rounded mr-2"></div>
            <span>Très mauvais (0.0-3.4)</span>
          </div>
        </div>
      </div>
    </div>
  );
} 