'use client';

import React from 'react';

const InsuranceFirmDashboard = () => {
  return (
    <>
      <div className="flex flex-wrap justify-between gap-3 p-4">
        <div className="flex min-w-72 flex-col gap-3">
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight">Dashboard</p>
          <p className="text-[#5c738a] text-sm font-normal leading-normal">Overview of key metrics and performance indicators</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-4 p-4">
        <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
          <p className="text-[#101418] text-base font-medium leading-normal">New Policies</p>
          <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">1,250</p>
          <p className="text-[#078838] text-base font-medium leading-normal">+15%</p>
        </div>
        <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
          <p className="text-[#101418] text-base font-medium leading-normal">Outstanding Premiums</p>
          <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">$750,000</p>
          <p className="text-[#e73908] text-base font-medium leading-normal">-5%</p>
        </div>
        <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
          <p className="text-[#101418] text-base font-medium leading-normal">Broker Performance</p>
          <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">Top Broker: Ethan Carter</p>
          <p className="text-[#078838] text-base font-medium leading-normal">+10%</p>
        </div>
        <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-[#eaedf1]">
          <p className="text-[#101418] text-base font-medium leading-normal">Claims Processed</p>
          <p className="text-[#101418] tracking-light text-2xl font-bold leading-tight">320</p>
          <p className="text-[#078838] text-base font-medium leading-normal">+8%</p>
        </div>
      </div>
      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">Broker Information</h2>
      <div className="px-4 py-3 @container">
        <div className="flex overflow-hidden rounded-xl border border-[#d4dbe2] bg-gray-50">
          <table className="flex-1">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Broker Name</th>
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Policies Sold</th>
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Commission Earned</th>
                <th className="px-4 py-3 text-left text-[#101418] w-[400px] text-sm font-medium leading-normal">Client Satisfaction</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Ethan Carter</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">350</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$35,000</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-sm font-normal leading-normal">
                  <div className="flex items-center gap-3">
                    <div className="w-[88px] overflow-hidden rounded-sm bg-[#d4dbe2]"><div className="h-1 rounded-full bg-[#3f7fbf]" style={{width: '96.5909%'}}></div></div>
                    <p className="text-[#101418] text-sm font-medium leading-normal">85</p>
                  </div>
                </td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Isabella Rossi</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">280</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$28,000</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-sm font-normal leading-normal">
                  <div className="flex items-center gap-3">
                    <div className="w-[88px] overflow-hidden rounded-sm bg-[#d4dbe2]"><div className="h-1 rounded-full bg-[#3f7fbf]" style={{width: '100%'}}></div></div>
                    <p className="text-[#101418] text-sm font-medium leading-normal">92</p>
                  </div>
                </td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Ryan Kim</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">220</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$22,000</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-sm font-normal leading-normal">
                  <div className="flex items-center gap-3">
                    <div className="w-[88px] overflow-hidden rounded-sm bg-[#d4dbe2]"><div className="h-1 rounded-full bg-[#3f7fbf]" style={{width: '88.6364%'}}></div></div>
                    <p className="text-[#101418] text-sm font-medium leading-normal">78</p>
                  </div>
                </td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Sophia Zhang</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">180</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$18,000</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-sm font-normal leading-normal">
                  <div className="flex items-center gap-3">
                    <div className="w-[88px] overflow-hidden rounded-sm bg-[#d4dbe2]"><div className="h-1 rounded-full bg-[#3f7fbf]" style={{width: '100%'}}></div></div>
                    <p className="text-[#101418] text-sm font-medium leading-normal">88</p>
                  </div>
                </td>
              </tr>
              <tr className="border-t border-t-[#d4dbe2]">
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#101418] text-sm font-normal leading-normal">Liam Davis</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">150</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-[#5c738a] text-sm font-normal leading-normal">$15,000</td>
                <td className="h-[72px] px-4 py-2 w-[400px] text-sm font-normal leading-normal">
                  <div className="flex items-center gap-3">
                    <div className="w-[88px] overflow-hidden rounded-sm bg-[#d4dbe2]"><div className="h-1 rounded-full bg-[#3f7fbf]" style={{width: '90.9091%'}}></div></div>
                    <p className="text-[#101418] text-sm font-medium leading-normal">80</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
      <h2 className="text-[#101418] text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">Claims Data</h2>
      <div className="flex flex-wrap gap-4 px-4 py-6">
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
          <p className="text-[#101418] text-base font-medium leading-normal">Claims Processed by Type</p>
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight truncate">150</p>
          <div className="flex gap-1">
            <p className="text-[#5c738a] text-base font-normal leading-normal">Last Quarter</p>
            <p className="text-[#078838] text-base font-medium leading-normal">+10%</p>
          </div>
          <div className="grid min-h-[180px] grid-flow-col gap-6 grid-rows-[1fr_auto] items-end justify-items-center px-3">
            <div className="border-[#5c738a] bg-[#eaedf1] border-t-2 w-full" style={{height: '50%'}}></div>
            <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Auto</p>
            <div className="border-[#5c738a] bg-[#eaedf1] border-t-2 w-full" style={{height: '80%'}}></div>
            <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Home</p>
            <div className="border-[#5c738a] bg-[#eaedf1] border-t-2 w-full" style={{height: '10%'}}></div>
            <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Health</p>
            <div className="border-[#5c738a] bg-[#eaedf1] border-t-2 w-full" style={{height: '50%'}}></div>
            <p className="text-[#5c738a] text-[13px] font-bold leading-normal tracking-[0.015em]">Life</p>
          </div>
        </div>
        <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-[#d4dbe2] p-6">
          <p className="text-[#101418] text-base font-medium leading-normal">Claims Payout Over Time</p>
          <p className="text-[#101418] tracking-light text-[32px] font-bold leading-tight truncate">$2.5M</p>
          <div className="flex gap-1">
            <p className="text-[#5c738a] text-base font-normal leading-normal">Last Year</p>
            <p className="text-[#078838] text-base font-medium leading-normal">+5%</p>
          </div>
          <div className="flex min-h-[180px] flex-1 flex-col gap-8 py-4">
            <svg width="100%" height="148" viewBox="-3 0 478 150" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
              <path
                d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25V149H326.769H0V109Z"
                fill="url(#paint0_linear_1131_5935_insurance)"
              ></path>
              <path
                d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25"
                stroke="#5c738a"
                strokeWidth="3"
                strokeLinecap="round"
              ></path>
              <defs>
                <linearGradient id="paint0_linear_1131_5935_insurance" x1="236" y1="1" x2="236" y2="149" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#eaedf1"></stop>
                  <stop offset="1" stopColor="#eaedf1" stopOpacity="0"></stop>
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
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default InsuranceFirmDashboard; 