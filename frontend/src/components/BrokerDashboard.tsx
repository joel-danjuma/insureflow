'use client';

import React from 'react';
import { convertUSDToNaira } from '@/utils/currency';

const BrokerDashboard = () => {
  return (
    <>
      <div className="flex flex-wrap justify-between gap-3 p-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight">Broker Dashboard</p>
          <p className="text-[#5c738a] text-sm font-normal leading-normal">Overview of your performance and client portfolio</p>
        </div>
      </div>
      
      {/* Metrics Cards */}
      <div className="flex flex-wrap gap-4 p-4">
        <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
          <p className="text-[#101418] text-base font-medium leading-normal">Total Sales</p>
          <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">$250,000</p>
          <p className="text-[#078838] text-base font-medium leading-normal">+10%</p>
        </div>
        <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
          <p className="text-[#101418] text-base font-medium leading-normal">Client Retention Rate</p>
          <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">95%</p>
          <p className="text-[#e73908] text-base font-medium leading-normal">-2%</p>
        </div>
        <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
          <p className="text-[#101418] text-base font-medium leading-normal">Average Commission</p>
          <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">$5,000</p>
          <p className="text-[#078838] text-base font-medium leading-normal">+5%</p>
        </div>
      </div>

      {/* Sales Performance Section */}
      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">Sales Performance</h2>
      <div className="flex flex-wrap gap-4 px-4 py-6">
        {/* Sales Over Time Chart */}
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
          <p className="text-[#101418] text-base font-medium leading-normal">Sales Over Time</p>
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight truncate">$250,000</p>
          <div className="flex gap-1">
            <p className="text-[#5c738a] text-base font-normal leading-normal">Last 12 Months</p>
            <p className="text-[#078838] text-base font-medium leading-normal">+10%</p>
          </div>
          <div className="flex min-h-[180px] flex-1 flex-col gap-8 py-4">
            <svg width="100%" height="148" viewBox="-3 0 478 150" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
              <path
                d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25V149H326.769H0V109Z"
                fill="url(#paint0_linear_1131_5935)"
              />
              <path
                d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25"
                stroke="#5c738a"
                strokeWidth="3"
                strokeLinecap="round"
              />
              <defs>
                <linearGradient id="paint0_linear_1131_5935" x1="236" y1="1" x2="236" y2="149" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#eaedf1" />
                  <stop offset="1" stopColor="#eaedf1" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
            <div className="flex justify-around">
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Jan</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Feb</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Mar</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Apr</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">May</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Jun</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Jul</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Aug</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Sep</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Oct</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Nov</p>
              <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Dec</p>
            </div>
          </div>
        </div>

        {/* Sales by Product Chart */}
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
          <p className="text-[#101418] text-base font-medium leading-normal">Sales by Product</p>
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight truncate">$100,000</p>
          <div className="flex gap-1">
            <p className="text-[#5c738a] text-base font-normal leading-normal">This Year</p>
            <p className="text-[#078838] text-base font-medium leading-normal">+5%</p>
          </div>
          <div className="grid min-h-[180px] grid-flow-col gap-6 grid-rows-[1fr_auto] items-end justify-items-center px-3">
            <div className="border-[#5c738a] bg-[#eaedf1] border-t-2 w-full" style={{height: '20%'}} />
            <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Product A</p>
            <div className="border-[#5c738a] bg-[#eaedf1] border-t-2 w-full" style={{height: '60%'}} />
            <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Product B</p>
            <div className="border-[#5c738a] bg-[#eaedf1] border-t-2 w-full" style={{height: '80%'}} />
            <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Product C</p>
          </div>
        </div>
      </div>

      {/* Client Portfolio Section */}
      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">Client Portfolio</h2>
      <div className="px-4 py-3">
        <div className="flex overflow-hidden rounded-xl border border-[#d4dbe2] bg-gray-50">
          <table className="flex-1">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Client Name</th>
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Policy Type</th>
                <th className="px-4 py-3 text-left text-[#101418] w-60 text-sm font-medium leading-normal">Policy Status</th>
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Premium Amount</th>
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Next Payment Date</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Lucas Bennett</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">Auto Insurance</td>
                <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                  <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-[#eaedf1] text-[#101418] text-sm font-medium leading-normal w-full">
                    <span className="truncate">Active</span>
                  </button>
                </td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$1,200</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">2024-08-15</td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Sophia Carter</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">Home Insurance</td>
                <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                  <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-[#eaedf1] text-[#101418] text-sm font-medium leading-normal w-full">
                    <span className="truncate">Active</span>
                  </button>
                </td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$1,500</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">2024-09-01</td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Owen Davis</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">Life Insurance</td>
                <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                  <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-[#eaedf1] text-[#101418] text-sm font-medium leading-normal w-full">
                    <span className="truncate">Pending</span>
                  </button>
                </td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$2,000</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">2024-07-20</td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Chloe Foster</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">Health Insurance</td>
                <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                  <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-[#eaedf1] text-[#101418] text-sm font-medium leading-normal w-full">
                    <span className="truncate">Active</span>
                  </button>
                </td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$1,800</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">2024-08-05</td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Jackson Harper</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">Business Insurance</td>
                <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                  <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-[#eaedf1] text-[#101418] text-sm font-medium leading-normal w-full">
                    <span className="truncate">Active</span>
                  </button>
                </td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$2,500</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">2024-09-10</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
};

export default BrokerDashboard; 