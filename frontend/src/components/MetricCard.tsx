import React, { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeColor?: string;
  children?: ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, changeColor = 'text-green-500', children }) => {
  return (
    <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
      <p className="text-[#101418] text-base font-medium leading-normal">{title}</p>
      <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">{value}</p>
      {change && <p className={`text-base font-medium leading-normal ${changeColor}`}>{change}</p>}
      {children}
    </div>
  );
};

export default MetricCard; 