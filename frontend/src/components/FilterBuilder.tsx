/**
 * FilterBuilder Component for FA-44 Epic
 * Advanced filtering and segmentation for multi-form dashboards
 */

import React, { useState, useEffect } from 'react';
import {
  Filter,
  Plus,
  Trash2,
  Calendar,
  Users,
  TrendingUp,
  Save,
  X,
  ChevronDown,
  ChevronUp,
  AlertCircle
} from 'lucide-react';

interface FilterRule {
  id: string;
  field: string;
  operator: string;
  value: any;
  dataType?: 'string' | 'number' | 'date' | 'boolean';
}

interface DateRange {
  start: string;
  end: string;
}

interface FilterConfig {
  date_range?: DateRange;
  segments?: string[];
  custom_filters?: FilterRule[];
}

interface FilterBuilderProps {
  onFiltersChange: (filters: FilterConfig) => void;
  availableFields?: string[];
  initialFilters?: FilterConfig;
  userPlan?: 'free' | 'pro' | 'business';
}

const FilterBuilder: React.FC<FilterBuilderProps> = ({
  onFiltersChange,
  availableFields = [],
  initialFilters = {},
  userPlan = 'free'
}) => {
  const [dateRange, setDateRange] = useState<DateRange>(
    initialFilters.date_range || { start: '', end: '' }
  );
  const [segments, setSegments] = useState<string[]>(
    initialFilters.segments || []
  );
  const [customFilters, setCustomFilters] = useState<FilterRule[]>(
    initialFilters.custom_filters || []
  );
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [savedFilters, setSavedFilters] = useState<Array<{ name: string; config: FilterConfig }>>([]);
  const [filterName, setFilterName] = useState('');

  // Available operators based on data type
  const operators = {
    string: ['=', '!=', 'contains', 'starts_with', 'ends_with', 'in'],
    number: ['=', '!=', '>', '>=', '<', '<=', 'between'],
    date: ['=', '!=', '>', '>=', '<', '<=', 'between'],
    boolean: ['=', '!=']
  };

  // Common segments
  const commonSegments = [
    'age_group',
    'location',
    'device_type',
    'source',
    'category',
    'status',
    'priority',
    'department'
  ];

  // Determine max filters based on user plan
  const getMaxFilters = () => {
    switch (userPlan) {
      case 'free':
        return 3;
      case 'pro':
        return 10;
      case 'business':
        return -1; // Unlimited
      default:
        return 3;
    }
  };

  useEffect(() => {
    // Notify parent of filter changes
    const config: FilterConfig = {};
    
    if (dateRange.start || dateRange.end) {
      config.date_range = dateRange;
    }
    
    if (segments.length > 0) {
      config.segments = segments;
    }
    
    if (customFilters.length > 0) {
      config.custom_filters = customFilters;
    }
    
    onFiltersChange(config);
  }, [dateRange, segments, customFilters]);

  const addFilter = () => {
    const maxFilters = getMaxFilters();
    if (maxFilters > 0 && customFilters.length >= maxFilters) {
      alert(`You can only add up to ${maxFilters} custom filters with your ${userPlan} plan`);
      return;
    }

    const newFilter: FilterRule = {
      id: Date.now().toString(),
      field: availableFields[0] || '',
      operator: '=',
      value: '',
      dataType: 'string'
    };
    
    setCustomFilters([...customFilters, newFilter]);
  };

  const removeFilter = (filterId: string) => {
    setCustomFilters(customFilters.filter(f => f.id !== filterId));
  };

  const updateFilter = (filterId: string, updates: Partial<FilterRule>) => {
    setCustomFilters(customFilters.map(f => 
      f.id === filterId ? { ...f, ...updates } : f
    ));
  };

  const toggleSegment = (segment: string) => {
    if (segments.includes(segment)) {
      setSegments(segments.filter(s => s !== segment));
    } else {
      setSegments([...segments, segment]);
    }
  };

  const saveFilterSet = () => {
    if (!filterName) {
      alert('Please enter a name for this filter set');
      return;
    }

    const config: FilterConfig = {
      date_range: dateRange,
      segments,
      custom_filters: customFilters
    };

    setSavedFilters([...savedFilters, { name: filterName, config }]);
    setFilterName('');
    
    // Save to localStorage
    localStorage.setItem('saved_filters', JSON.stringify([...savedFilters, { name: filterName, config }]));
  };

  const loadFilterSet = (config: FilterConfig) => {
    setDateRange(config.date_range || { start: '', end: '' });
    setSegments(config.segments || []);
    setCustomFilters(config.custom_filters || []);
  };

  const clearAllFilters = () => {
    setDateRange({ start: '', end: '' });
    setSegments([]);
    setCustomFilters([]);
  };

  // Get field type (simplified detection)
  const getFieldType = (field: string): FilterRule['dataType'] => {
    if (field.includes('date') || field.includes('time') || field.includes('_at')) {
      return 'date';
    }
    if (field.includes('count') || field.includes('amount') || field.includes('score') || field.includes('age')) {
      return 'number';
    }
    if (field.includes('is_') || field.includes('has_')) {
      return 'boolean';
    }
    return 'string';
  };

  return (
    <div className="filter-builder">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Filter & Segment Data
          </h3>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
          >
            Advanced Options
            {showAdvanced ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Filter and segment your aggregated data for detailed analysis
        </p>
      </div>

      {/* Date Range Filter */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center mb-3">
          <Calendar className="w-4 h-4 mr-2 text-gray-600" />
          <label className="text-sm font-medium">Date Range</label>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-600">Start Date</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">End Date</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>
        </div>
        
        {/* Quick Date Range Options */}
        <div className="mt-3 flex gap-2">
          <button
            onClick={() => {
              const today = new Date();
              const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
              setDateRange({
                start: lastWeek.toISOString().split('T')[0],
                end: today.toISOString().split('T')[0]
              });
            }}
            className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-50"
          >
            Last 7 days
          </button>
          <button
            onClick={() => {
              const today = new Date();
              const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
              setDateRange({
                start: lastMonth.toISOString().split('T')[0],
                end: today.toISOString().split('T')[0]
              });
            }}
            className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-50"
          >
            Last 30 days
          </button>
          <button
            onClick={() => {
              const today = new Date();
              const thisMonth = new Date(today.getFullYear(), today.getMonth(), 1);
              setDateRange({
                start: thisMonth.toISOString().split('T')[0],
                end: today.toISOString().split('T')[0]
              });
            }}
            className="text-xs px-2 py-1 bg-white border rounded hover:bg-gray-50"
          >
            This month
          </button>
        </div>
      </div>

      {/* Segmentation */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center mb-3">
          <Users className="w-4 h-4 mr-2 text-gray-600" />
          <label className="text-sm font-medium">Segmentation</label>
        </div>
        <div className="flex flex-wrap gap-2">
          {commonSegments.map((segment) => (
            <button
              key={segment}
              onClick={() => toggleSegment(segment)}
              className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                segments.includes(segment)
                  ? 'bg-blue-500 text-white border-blue-500'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              {segment.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Filters */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center">
            <TrendingUp className="w-4 h-4 mr-2 text-gray-600" />
            <label className="text-sm font-medium">Custom Filters</label>
            {userPlan === 'free' && (
              <span className="ml-2 text-xs text-amber-600">
                ({customFilters.length}/{getMaxFilters()} filters)
              </span>
            )}
          </div>
          <button
            onClick={addFilter}
            className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Filter
          </button>
        </div>

        {customFilters.length === 0 ? (
          <div className="p-4 border-2 border-dashed border-gray-300 rounded-lg text-center text-gray-500 text-sm">
            No custom filters added. Click "Add Filter" to create one.
          </div>
        ) : (
          <div className="space-y-2">
            {customFilters.map((filter) => (
              <FilterRow
                key={filter.id}
                filter={filter}
                availableFields={availableFields}
                operators={operators}
                onUpdate={(updates) => updateFilter(filter.id, updates)}
                onRemove={() => removeFilter(filter.id)}
                getFieldType={getFieldType}
              />
            ))}
          </div>
        )}
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium mb-3">Advanced Options</h4>
          
          {/* Saved Filter Sets */}
          <div className="mb-4">
            <label className="text-xs text-gray-600">Save Current Filters</label>
            <div className="flex gap-2 mt-1">
              <input
                type="text"
                placeholder="Filter set name"
                value={filterName}
                onChange={(e) => setFilterName(e.target.value)}
                className="flex-1 px-3 py-2 border rounded text-sm"
              />
              <button
                onClick={saveFilterSet}
                className="px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 flex items-center"
              >
                <Save className="w-4 h-4 mr-1" />
                Save
              </button>
            </div>
          </div>

          {/* Load Saved Filters */}
          {savedFilters.length > 0 && (
            <div>
              <label className="text-xs text-gray-600">Load Saved Filters</label>
              <div className="mt-1 space-y-1">
                {savedFilters.map((saved, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadFilterSet(saved.config)}
                    className="w-full text-left px-3 py-2 bg-white border rounded text-sm hover:bg-gray-50"
                  >
                    {saved.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between">
        <button
          onClick={clearAllFilters}
          className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm"
        >
          Clear All Filters
        </button>
        
        {userPlan === 'free' && customFilters.length >= getMaxFilters() && (
          <div className="flex items-center text-sm text-amber-600">
            <AlertCircle className="w-4 h-4 mr-1" />
            <span>Upgrade to add more filters</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Filter Row Component
const FilterRow: React.FC<{
  filter: FilterRule;
  availableFields: string[];
  operators: Record<string, string[]>;
  onUpdate: (updates: Partial<FilterRule>) => void;
  onRemove: () => void;
  getFieldType: (field: string) => FilterRule['dataType'];
}> = ({ filter, availableFields, operators, onUpdate, onRemove, getFieldType }) => {
  const fieldType = filter.dataType || getFieldType(filter.field);
  const availableOperators = operators[fieldType] || operators.string;

  return (
    <div className="flex items-center gap-2 p-3 bg-white border rounded-lg">
      {/* Field Selection */}
      <select
        value={filter.field}
        onChange={(e) => {
          const newField = e.target.value;
          const newType = getFieldType(newField);
          onUpdate({ 
            field: newField, 
            dataType: newType,
            operator: operators[newType][0] 
          });
        }}
        className="flex-1 px-2 py-1 border rounded text-sm"
      >
        <option value="">Select field...</option>
        {availableFields.map((field) => (
          <option key={field} value={field}>
            {field.replace('_', ' ')}
          </option>
        ))}
      </select>

      {/* Operator Selection */}
      <select
        value={filter.operator}
        onChange={(e) => onUpdate({ operator: e.target.value })}
        className="px-2 py-1 border rounded text-sm"
      >
        {availableOperators.map((op) => (
          <option key={op} value={op}>
            {op}
          </option>
        ))}
      </select>

      {/* Value Input */}
      {filter.operator === 'between' ? (
        <>
          <input
            type={fieldType === 'number' ? 'number' : fieldType === 'date' ? 'date' : 'text'}
            placeholder="From"
            value={Array.isArray(filter.value) ? filter.value[0] : ''}
            onChange={(e) => onUpdate({ 
              value: [e.target.value, Array.isArray(filter.value) ? filter.value[1] : ''] 
            })}
            className="w-24 px-2 py-1 border rounded text-sm"
          />
          <span className="text-gray-500">to</span>
          <input
            type={fieldType === 'number' ? 'number' : fieldType === 'date' ? 'date' : 'text'}
            placeholder="To"
            value={Array.isArray(filter.value) ? filter.value[1] : ''}
            onChange={(e) => onUpdate({ 
              value: [Array.isArray(filter.value) ? filter.value[0] : '', e.target.value] 
            })}
            className="w-24 px-2 py-1 border rounded text-sm"
          />
        </>
      ) : filter.operator === 'in' ? (
        <input
          type="text"
          placeholder="Values (comma-separated)"
          value={Array.isArray(filter.value) ? filter.value.join(', ') : filter.value}
          onChange={(e) => onUpdate({ 
            value: e.target.value.split(',').map(v => v.trim()) 
          })}
          className="flex-1 px-2 py-1 border rounded text-sm"
        />
      ) : fieldType === 'boolean' ? (
        <select
          value={filter.value}
          onChange={(e) => onUpdate({ value: e.target.value === 'true' })}
          className="px-2 py-1 border rounded text-sm"
        >
          <option value="true">True</option>
          <option value="false">False</option>
        </select>
      ) : (
        <input
          type={fieldType === 'number' ? 'number' : fieldType === 'date' ? 'date' : 'text'}
          placeholder="Value"
          value={filter.value}
          onChange={(e) => onUpdate({ value: e.target.value })}
          className="flex-1 px-2 py-1 border rounded text-sm"
        />
      )}

      {/* Remove Button */}
      <button
        onClick={onRemove}
        className="p-1 text-red-500 hover:text-red-700"
        title="Remove filter"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};

export default FilterBuilder;