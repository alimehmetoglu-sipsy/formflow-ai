/**
 * Competitor Insights Component for FA-46
 * Displays competitive analysis when competitors are mentioned
 */

import React, { useState } from 'react';
import {
  Shield,
  TrendingUp,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Target,
  DollarSign,
  Zap,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface Competitor {
  name: string;
  mentioned: boolean;
  advantages?: string[];
  disadvantages?: string[];
  positioning?: string;
  winRate?: number;
}

interface CompetitorInsightsProps {
  competitors: Competitor[];
}

const CompetitorInsights: React.FC<CompetitorInsightsProps> = ({ competitors }) => {
  const [expandedCompetitor, setExpandedCompetitor] = useState<number | null>(0);

  if (!competitors || competitors.length === 0) {
    return null;
  }

  const getCompetitorLogo = (name: string) => {
    // In a real app, you'd have actual logos
    const colors: { [key: string]: string } = {
      'salesforce': 'bg-blue-500',
      'hubspot': 'bg-orange-500',
      'excel': 'bg-green-500',
      'manual': 'bg-gray-500',
      'custom': 'bg-purple-500'
    };
    
    const color = colors[name.toLowerCase()] || 'bg-gray-400';
    
    return (
      <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center text-white font-bold`}>
        {name.charAt(0).toUpperCase()}
      </div>
    );
  };

  return (
    <div className="competitor-insights">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Shield className="w-5 h-5 mr-2 text-purple-500" />
          Competitive Intelligence
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Competitors detected in form responses
        </p>
      </div>

      <div className="space-y-3">
        {competitors.map((competitor, index) => {
          const isExpanded = expandedCompetitor === index;
          
          return (
            <div
              key={index}
              className="border rounded-lg bg-white overflow-hidden"
            >
              {/* Competitor Header */}
              <button
                onClick={() => setExpandedCompetitor(isExpanded ? null : index)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center">
                  {getCompetitorLogo(competitor.name)}
                  <div className="ml-3 text-left">
                    <p className="font-semibold text-gray-900 capitalize">
                      {competitor.name}
                    </p>
                    {competitor.mentioned && (
                      <span className="text-xs text-amber-600">
                        Mentioned by lead
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  {competitor.winRate && (
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {competitor.winRate}%
                      </p>
                      <p className="text-xs text-gray-500">Win Rate</p>
                    </div>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </button>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t">
                  {/* Our Advantages */}
                  {competitor.advantages && competitor.advantages.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Our Advantages
                      </h4>
                      <ul className="space-y-1">
                        {competitor.advantages.map((advantage, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="text-green-500 mr-2 mt-0.5">✓</span>
                            <span className="text-sm text-gray-700">{advantage}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Their Advantages */}
                  {competitor.disadvantages && competitor.disadvantages.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-semibold text-red-700 mb-2 flex items-center">
                        <XCircle className="w-4 h-4 mr-1" />
                        Their Strengths
                      </h4>
                      <ul className="space-y-1">
                        {competitor.disadvantages.map((disadvantage, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="text-red-500 mr-2 mt-0.5">•</span>
                            <span className="text-sm text-gray-700">{disadvantage}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Positioning Strategy */}
                  {competitor.positioning && (
                    <div className="mt-4 p-3 bg-blue-50 rounded">
                      <h4 className="text-sm font-semibold text-blue-700 mb-1 flex items-center">
                        <Target className="w-4 h-4 mr-1" />
                        Positioning Strategy
                      </h4>
                      <p className="text-sm text-blue-600">
                        {competitor.positioning}
                      </p>
                    </div>
                  )}

                  {/* Quick Battle Card */}
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="flex items-center text-gray-600 mb-1">
                        <DollarSign className="w-4 h-4 mr-1" />
                        <span className="text-xs font-medium">Price Comparison</span>
                      </div>
                      <p className="text-sm text-gray-900">
                        50-70% more cost-effective
                      </p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <div className="flex items-center text-gray-600 mb-1">
                        <Zap className="w-4 h-4 mr-1" />
                        <span className="text-xs font-medium">Setup Time</span>
                      </div>
                      <p className="text-sm text-gray-900">
                        5 minutes vs 2+ weeks
                      </p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="mt-4 flex space-x-3">
                    <button className="flex-1 px-3 py-2 bg-purple-600 text-white rounded text-sm font-medium hover:bg-purple-700">
                      View Full Battle Card
                    </button>
                    <button className="flex-1 px-3 py-2 border border-gray-300 text-gray-700 rounded text-sm font-medium hover:bg-gray-50">
                      Copy Positioning
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-4 p-4 bg-amber-50 rounded-lg">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 mr-2" />
          <div>
            <p className="text-sm font-semibold text-amber-800">
              Competitive Situation
            </p>
            <p className="text-sm text-amber-700 mt-1">
              Lead is evaluating {competitors.length} competitor{competitors.length > 1 ? 's' : ''}. 
              Focus on differentiation and unique value proposition.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitorInsights;