'use client';

import React from 'react';
import { formatNaira } from '@/utils/currency';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'increase' | 'decrease';
  isCurrency?: boolean;
  isLoading?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType,
  isCurrency = false,
  isLoading = false
}) => {
  if (isLoading) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 animate-pulse">
        <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
        <div className="h-8 bg-gray-700 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-gray-700 rounded w-1/3"></div>
      </div>
    );
  }

  const formatValue = (val: string | number) => {
    if (isCurrency && typeof val === 'number') {
      return formatNaira(val);
    }
    return val.toString();
  };

  const getChangeIcon = () => {
    if (!change || !changeType) return null;
    
    if (changeType === 'increase') {
      return (
        <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7m0 0H7" />
        </svg>
      );
    } else {
      return (
        <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10m0 0h10" />
        </svg>
      );
    }
  };

  const getChangeColor = () => {
    if (!changeType) return 'text-gray-400';
    return changeType === 'increase' ? 'text-green-400' : 'text-red-400';
  };

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-orange-500 transition-colors duration-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-400 mb-1">{title}</p>
          <p className="text-2xl font-bold text-white mb-2">{formatValue(value)}</p>
          
          {change !== undefined && changeType && (
            <div className="flex items-center space-x-1">
              {getChangeIcon()}
              <span className={`text-sm font-medium ${getChangeColor()}`}>
                {Math.abs(change)}%
              </span>
              <span className="text-sm text-gray-500">vs last month</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricCard; 