'use client';

import React from 'react';
import { convertUSDToNaira } from '@/utils/currency';

const BrokerDashboard = () => {
  return (
    <div className="gap-1 px-6 flex flex-1 justify-center py-5 bg-bg-primary">
      <div className="layout-content-container flex flex-col w-80">
        <div className="flex h-full min-h-[700px] flex-col justify-between bg-bg-primary p-4">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col">
              <h1 className="text-text-primary text-xl font-bold leading-normal">Acme Co</h1>
              <p className="text-text-secondary text-sm font-normal leading-normal">Broker Team</p>
            </div>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-bg-secondary text-text-primary">
                <div className="text-current">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                    <path d="M224,115.55V208a16,16,0,0,1-16,16H168a16,16,0,0,1-16-16V168a8,8,0,0,0-8-8H112a8,8,0,0,0-8,8v40a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V115.55a16,16,0,0,1,5.17-11.78l80-75.48.11-.11a16,16,0,0,1,21.53,0,1.14,1.14,0,0,0,.11.11l80,75.48A16,16,0,0,1,224,115.55Z"></path>
                  </svg>
                </div>
                <p className="text-current text-sm font-medium leading-normal">Dashboard</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-text-secondary hover:bg-bg-secondary rounded-lg transition-colors">
                <div className="text-current">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                    <path d="M117.25,157.92a60,60,0,1,0-66.5,0A95.83,95.83,0,0,0,3.53,195.63a8,8,0,1,0,13.4,8.74,80,80,0,0,1,134.14,0,8,8,0,0,0,13.4-8.74A95.83,95.83,0,0,0,117.25,157.92ZM40,108a44,44,0,1,1,44,44A44.05,44.05,0,0,1,40,108Zm210.14,98.7a8,8,0,0,1-11.07-2.33A79.83,79.83,0,0,0,172,168a8,8,0,0,1,0-16,44,44,0,1,0-16.34-84.87,8,8,0,1,1-5.94-14.85,60,60,0,0,1,55.53,105.64,95.83,95.83,0,0,1,47.22,37.71A8,8,0,0,1,250.14,206.7Z"></path>
                  </svg>
                </div>
                <p className="text-current text-sm font-medium leading-normal">Clients</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-text-secondary hover:bg-bg-secondary rounded-lg transition-colors">
                <div className="text-current">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                    <path d="M213.66,82.34l-56-56A8,8,0,0,0,152,24H56A16,16,0,0,0,40,40V216a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V88A8,8,0,0,0,213.66,82.34ZM160,51.31,188.69,80H160ZM200,216H56V40h88V88a8,8,0,0,0,8,8h48V216Z"></path>
                  </svg>
                </div>
                <p className="text-current text-sm font-medium leading-normal">Policies</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-text-secondary hover:bg-bg-secondary rounded-lg transition-colors">
                <div className="text-current">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                    <path d="M152,120H136V56h8a32,32,0,0,1,32,32,8,8,0,0,0,16,0,48.05,48.05,0,0,0-48-48h-8V24a8,8,0,0,0-16,0V40h-8a48,48,0,0,0,0,96h8v64H104a32,32,0,0,1-32-32,8,8,0,0,0-16,0,48.05,48.05,0,0,0,48,48h16v16a8,8,0,0,0,16,0V216h16a48,48,0,0,0,0-96Zm-40,0a32,32,0,0,1,0-64h8v64Zm40,80H136V136h16a32,32,0,0,1,0,64Z"></path>
                  </svg>
                </div>
                <p className="text-current text-sm font-medium leading-normal">Commissions</p>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-text-secondary hover:bg-bg-secondary rounded-lg transition-colors">
                <div className="text-current">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                    <path d="M140,180a12,12,0,1,1-12-12A12,12,0,0,1,140,180ZM128,72c-22.06,0-40,16.15-40,36v4a8,8,0,0,0,16,0v-4c0-11,10.77-20,24-20s24,9,24,20-10.77,20-24,20a8,8,0,0,0-8,8v8a8,8,0,0,0,16,0v-.72c18.24-3.35,32-17.9,32-35.28C168,88.15,150.06,72,128,72Zm104,56A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"></path>
                  </svg>
                </div>
                <p className="text-current text-sm font-medium leading-normal">Support</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="layout-content-container flex flex-col max-w-[960px] flex-1">
        <div className="flex flex-wrap justify-between gap-3 p-4">
          <div className="flex min-w-72 flex-col gap-3">
            <p className="text-text-primary tracking-light text-[28px] font-bold leading-tight">Broker Dashboard</p>
            <p className="text-text-secondary text-sm font-normal leading-normal">Overview of your performance and client portfolio</p>
          </div>
        </div>
        
        {/* Metrics Cards */}
        <div className="flex flex-wrap gap-4 p-4">
          <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-bg-secondary">
            <p className="text-text-secondary text-base font-medium leading-normal">Total Sales</p>
            <p className="text-text-primary tracking-light text-2xl font-bold leading-tight">{convertUSDToNaira(250000)}</p>
            <p className="text-accent-green text-base font-medium leading-normal">+10%</p>
          </div>
          <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-bg-secondary">
            <p className="text-text-secondary text-base font-medium leading-normal">Client Retention Rate</p>
            <p className="text-text-primary tracking-light text-2xl font-bold leading-tight">95%</p>
            <p className="text-accent-red text-base font-medium leading-normal">-2%</p>
          </div>
          <div className="flex min-w-[158px] flex-1 flex-col gap-2 rounded-xl p-6 bg-bg-secondary">
            <p className="text-text-secondary text-base font-medium leading-normal">Average Commission</p>
            <p className="text-text-primary tracking-light text-2xl font-bold leading-tight">{convertUSDToNaira(5000)}</p>
            <p className="text-accent-green text-base font-medium leading-normal">+5%</p>
          </div>
        </div>

        {/* Sales Performance Section */}
        <h2 className="text-text-primary text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">Sales Performance</h2>
        <div className="flex flex-wrap gap-4 px-4 py-6">
          {/* Sales Over Time Chart */}
          <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-border-color p-6 bg-bg-secondary">
            <p className="text-text-secondary text-base font-medium leading-normal">Sales Over Time</p>
            <p className="text-text-primary tracking-light text-[32px] font-bold leading-tight truncate">{convertUSDToNaira(250000)}</p>
            <div className="flex gap-1">
              <p className="text-text-secondary text-base font-normal leading-normal">Last 12 Months</p>
              <p className="text-accent-green text-base font-medium leading-normal">+10%</p>
            </div>
            <div className="flex min-h-[180px] flex-1 flex-col gap-8 py-4">
              <svg width="100%" height="148" viewBox="-3 0 478 150" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
                <path
                  d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25V149H326.769H0V109Z"
                  fill="url(#paint0_linear_1131_5935)"
                />
                <path
                  d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25"
                  stroke="currentColor"
                  className="text-accent-orange"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="paint0_linear_1131_5935" x1="236" y1="1" x2="236" y2="149" gradientUnits="userSpaceOnUse">
                    <stop stopColor="var(--bg-secondary)" stopOpacity="0.1" />
                    <stop offset="1" stopColor="var(--bg-secondary)" stopOpacity="0" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="flex justify-around">
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Jan</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Feb</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Mar</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Apr</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">May</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Jun</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Jul</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Aug</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Sep</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Oct</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Nov</p>
                <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Dec</p>
              </div>
            </div>
          </div>

          {/* Sales by Product Chart */}
          <div className="flex min-w-72 flex-1 flex-col gap-2 rounded-xl border border-border-color p-6 bg-bg-secondary">
            <p className="text-text-secondary text-base font-medium leading-normal">Sales by Product</p>
            <p className="text-text-primary tracking-light text-[32px] font-bold leading-tight truncate">{convertUSDToNaira(100000)}</p>
            <div className="flex gap-1">
              <p className="text-text-secondary text-base font-normal leading-normal">This Year</p>
              <p className="text-accent-green text-base font-medium leading-normal">+5%</p>
            </div>
            <div className="grid min-h-[180px] grid-flow-col gap-6 grid-rows-[1fr_auto] items-end justify-items-center px-3">
              <div className="border-accent-orange bg-bg-secondary border-t-2 w-full" style={{height: '20%'}} />
              <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Product A</p>
              <div className="border-accent-orange bg-bg-secondary border-t-2 w-full" style={{height: '60%'}} />
              <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Product B</p>
              <div className="border-accent-orange bg-bg-secondary border-t-2 w-full" style={{height: '80%'}} />
              <p className="text-text-secondary text-[13px] font-bold leading-normal tracking-[0.015em]">Product C</p>
            </div>
          </div>
        </div>

        {/* Client Portfolio Section */}
        <h2 className="text-text-primary text-xl font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5">Client Portfolio</h2>
        <div className="px-4 py-3 @container">
          <div className="flex overflow-hidden rounded-xl border border-border-color bg-bg-secondary">
            <table className="flex-1">
              <thead>
                <tr className="border-b border-border-color">
                  <th className="px-4 py-3 text-left text-text-secondary w-[400px] text-sm font-medium leading-normal">Client Name</th>
                  <th className="px-4 py-3 text-left text-text-secondary w-[400px] text-sm font-medium leading-normal">Policy Type</th>
                  <th className="px-4 py-3 text-left text-text-secondary w-60 text-sm font-medium leading-normal">Policy Status</th>
                  <th className="px-4 py-3 text-left text-text-secondary w-[400px] text-sm font-medium leading-normal">Premium Amount</th>
                  <th className="px-4 py-3 text-left text-text-secondary w-[400px] text-sm font-medium leading-normal">Next Payment Date</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-t-border-color">
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-primary text-sm font-normal leading-normal">Lucas Bennett</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">Auto Insurance</td>
                  <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                    <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-accent-green text-text-primary text-sm font-medium leading-normal w-full">
                      <span className="truncate">Active</span>
                    </button>
                  </td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">{convertUSDToNaira(1200)}</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">2024-08-15</td>
                </tr>
                <tr className="border-t border-t-border-color">
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-primary text-sm font-normal leading-normal">Sophia Carter</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">Home Insurance</td>
                  <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                    <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-accent-green text-text-primary text-sm font-medium leading-normal w-full">
                      <span className="truncate">Active</span>
                    </button>
                  </td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">{convertUSDToNaira(1500)}</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">2024-09-01</td>
                </tr>
                <tr className="border-t border-t-border-color">
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-primary text-sm font-normal leading-normal">Owen Davis</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">Life Insurance</td>
                  <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                    <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-accent-orange text-text-primary text-sm font-medium leading-normal w-full">
                      <span className="truncate">Pending</span>
                    </button>
                  </td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">{convertUSDToNaira(2000)}</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">2024-07-20</td>
                </tr>
                <tr className="border-t border-t-border-color">
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-primary text-sm font-normal leading-normal">Chloe Foster</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">Health Insurance</td>
                  <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                    <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-accent-green text-text-primary text-sm font-medium leading-normal w-full">
                      <span className="truncate">Active</span>
                    </button>
                  </td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">{convertUSDToNaira(1800)}</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">2024-08-05</td>
                </tr>
                <tr className="border-t border-t-border-color">
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-primary text-sm font-normal leading-normal">Jackson Harper</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">Business Insurance</td>
                  <td className="h-[72px] px-4 py-2 w-60 text-sm font-normal leading-normal">
                    <button className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-8 px-4 bg-accent-green text-text-primary text-sm font-medium leading-normal w-full">
                      <span className="truncate">Active</span>
                    </button>
                  </td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">{convertUSDToNaira(2500)}</td>
                  <td className="h-[72px] px-4 py-2 w-[400px] text-text-secondary text-sm font-normal leading-normal">2024-09-10</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BrokerDashboard; 