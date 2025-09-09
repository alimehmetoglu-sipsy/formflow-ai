/**
 * Lead Score Widget Component for FA-45
 * Displays lead score as a visual gauge with color coding
 */

import React from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Zap, 
  AlertCircle,
  Info
} from 'lucide-react';

interface LeadScoreProps {
  score: number;
  category: 'hot' | 'warm' | 'cold';
  showDetails?: boolean;
  scoreFactors?: {
    budget?: { value: number; weight: number };
    timeline?: { value: number; weight: number };
    authority?: { value: number; weight: number };
    need?: { value: number; weight: number };
    company_size?: { value: number; weight: number };
  };
  aiAdjustment?: number;
  buyingSignals?: string[];
}

const LeadScoreWidget: React.FC<LeadScoreProps> = ({
  score,
  category,
  showDetails = false,
  scoreFactors,
  aiAdjustment = 0,
  buyingSignals = []
}) => {
  // Determine color based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#ef4444'; // red-500 for hot
    if (score >= 60) return '#f59e0b'; // amber-500 for warm
    return '#3b82f6'; // blue-500 for cold
  };

  const getCategoryIcon = () => {
    switch (category) {
      case 'hot':
        return <Zap className="w-5 h-5 text-red-500" />;
      case 'warm':
        return <TrendingUp className="w-5 h-5 text-amber-500" />;
      default:
        return <TrendingDown className="w-5 h-5 text-blue-500" />;
    }
  };

  const getCategoryLabel = () => {
    switch (category) {
      case 'hot':
        return 'HOT LEAD 🔥';
      case 'warm':
        return 'WARM LEAD ⚡';
      default:
        return 'COLD LEAD ❄️';
    }
  };

  // Calculate gauge rotation
  const rotation = (score / 100) * 180 - 90;

  return (
    <div className="lead-score-widget bg-white rounded-lg shadow-lg p-6">
      {/* Main Score Display */}
      <div className="text-center mb-6">
        <div className="relative inline-block">
          {/* Gauge Background */}
          <svg width="200" height="120" viewBox="0 0 200 120">
            {/* Background arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
              strokeLinecap="round"
            />
            
            {/* Score arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke={getScoreColor(score)}
              strokeWidth="20"
              strokeLinecap="round"
              strokeDasharray={`${(score / 100) * 251.3} 251.3`}
              style={{
                transition: 'stroke-dasharray 0.5s ease-in-out'
              }}
            />
            
            {/* Score needle */}
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="30"
              stroke="#1f2937"
              strokeWidth="2"
              transform={`rotate(${rotation} 100 100)`}
              style={{
                transition: 'transform 0.5s ease-in-out'
              }}
            />
            
            {/* Center circle */}
            <circle cx="100" cy="100" r="5" fill="#1f2937" />
          </svg>
          
          {/* Score Text */}
          <div className="absolute inset-0 flex items-center justify-center mt-8">
            <div>
              <div className="text-4xl font-bold text-gray-900">{score}</div>
              <div className="text-sm text-gray-500">out of 100</div>
            </div>
          </div>
        </div>

        {/* Category Label */}
        <div className="mt-4 flex items-center justify-center space-x-2">
          {getCategoryIcon()}
          <span className="text-lg font-semibold text-gray-800">
            {getCategoryLabel()}
          </span>
        </div>
      </div>

      {/* Score Details */}
      {showDetails && scoreFactors && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <Info className="w-4 h-4 mr-1" />
            Score Breakdown
          </h4>
          
          <div className="space-y-2">
            {Object.entries(scoreFactors).map(([factor, details]) => (
              <div key={factor} className="flex items-center justify-between text-sm">
                <span className="text-gray-600 capitalize">
                  {factor.replace('_', ' ')}:
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-gray-900 font-medium">
                    {details.value} pts
                  </span>
                  <span className="text-gray-400">
                    ({Math.round(details.weight * 100)}%)
                  </span>
                </div>
              </div>
            ))}
            
            {aiAdjustment > 0 && (
              <div className="flex items-center justify-between text-sm pt-2 border-t">
                <span className="text-gray-600 flex items-center">
                  <Zap className="w-3 h-3 mr-1" />
                  AI Boost:
                </span>
                <span className="text-green-600 font-medium">
                  +{aiAdjustment} pts
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Buying Signals */}
      {buyingSignals.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            Buying Signals Detected
          </h4>
          <div className="flex flex-wrap gap-2">
            {buyingSignals.map((signal, index) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full"
              >
                {signal.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mt-4 pt-4 border-t flex justify-between">
        <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
          View Full Analysis
        </button>
        <button className="text-sm text-green-600 hover:text-green-800 font-medium">
          Contact Lead
        </button>
      </div>
    </div>
  );
};

export default LeadScoreWidget;