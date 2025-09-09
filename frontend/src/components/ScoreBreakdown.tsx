/**
 * Score Breakdown Component for FA-45
 * Shows detailed breakdown of lead score calculation
 */

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  Calculator,
  TrendingUp,
  Clock,
  User,
  Target,
  Building
} from 'lucide-react';

interface ScoreBreakdownProps {
  scoreFactors: {
    budget: { value: number; weight: number; contribution: number };
    timeline: { value: number; weight: number; contribution: number };
    authority: { value: number; weight: number; contribution: number };
    need: { value: number; weight: number; contribution: number };
    company_size: { value: number; weight: number; contribution: number };
  };
  aiAdjustment?: number;
  totalScore: number;
  insights?: {
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
  };
}

const ScoreBreakdown: React.FC<ScoreBreakdownProps> = ({
  scoreFactors,
  aiAdjustment = 0,
  totalScore,
  insights
}) => {
  // Prepare data for bar chart
  const barChartData = Object.entries(scoreFactors).map(([key, value]) => ({
    name: key.replace('_', ' ').charAt(0).toUpperCase() + key.replace('_', ' ').slice(1),
    score: value.value,
    weight: value.weight * 100,
    contribution: value.contribution
  }));

  if (aiAdjustment > 0) {
    barChartData.push({
      name: 'AI Boost',
      score: aiAdjustment,
      weight: 0,
      contribution: aiAdjustment
    });
  }

  // Prepare data for pie chart
  const pieChartData = Object.entries(scoreFactors).map(([key, value]) => ({
    name: key.replace('_', ' ').charAt(0).toUpperCase() + key.replace('_', ' ').slice(1),
    value: value.contribution
  }));

  // Colors for pie chart
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  // Get icon for factor
  const getFactorIcon = (factor: string) => {
    switch (factor.toLowerCase()) {
      case 'budget':
        return <TrendingUp className="w-4 h-4" />;
      case 'timeline':
        return <Clock className="w-4 h-4" />;
      case 'authority':
        return <User className="w-4 h-4" />;
      case 'need':
        return <Target className="w-4 h-4" />;
      case 'company_size':
        return <Building className="w-4 h-4" />;
      default:
        return <Calculator className="w-4 h-4" />;
    }
  };

  return (
    <div className="score-breakdown bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Calculator className="w-5 h-5 mr-2" />
        Lead Score Analysis
      </h3>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {Object.entries(scoreFactors).map(([factor, details], index) => (
          <div
            key={factor}
            className="bg-gray-50 rounded-lg p-3 border border-gray-200"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-gray-600">
                {getFactorIcon(factor)}
              </span>
              <span className="text-lg font-bold text-gray-900">
                {details.value}
              </span>
            </div>
            <div className="text-xs text-gray-500 capitalize">
              {factor.replace('_', ' ')}
            </div>
            <div className="text-xs text-gray-400">
              {Math.round(details.weight * 100)}% weight
            </div>
          </div>
        ))}
      </div>

      {/* Bar Chart */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Score Distribution</h4>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={barChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Legend />
            <Bar dataKey="score" fill="#3b82f6" name="Points" />
            <Bar dataKey="contribution" fill="#10b981" name="Weighted Contribution" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Pie Chart */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Contribution Breakdown</h4>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={pieChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Insights Section */}
      {insights && (
        <div className="space-y-4">
          {/* Strengths */}
          {insights.strengths.length > 0 && (
            <div className="bg-green-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-green-800 mb-2">
                ✅ Strengths
              </h4>
              <ul className="space-y-1">
                {insights.strengths.map((strength, index) => (
                  <li key={index} className="text-sm text-green-700 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Weaknesses */}
          {insights.weaknesses.length > 0 && (
            <div className="bg-amber-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-amber-800 mb-2">
                ⚠️ Areas for Improvement
              </h4>
              <ul className="space-y-1">
                {insights.weaknesses.map((weakness, index) => (
                  <li key={index} className="text-sm text-amber-700 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{weakness}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {insights.recommendations.length > 0 && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-800 mb-2">
                💡 Recommendations
              </h4>
              <ul className="space-y-1">
                {insights.recommendations.map((rec, index) => (
                  <li key={index} className="text-sm text-blue-700 flex items-start">
                    <span className="mr-2">{index + 1}.</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Total Score */}
      <div className="mt-6 pt-4 border-t">
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold text-gray-700">Total Score</span>
          <div className="flex items-center space-x-2">
            <span className="text-3xl font-bold text-gray-900">{totalScore}</span>
            <span className="text-gray-500">/ 100</span>
          </div>
        </div>
        {aiAdjustment > 0 && (
          <div className="text-sm text-green-600 mt-1 text-right">
            Includes +{aiAdjustment} AI boost
          </div>
        )}
      </div>
    </div>
  );
};

export default ScoreBreakdown;