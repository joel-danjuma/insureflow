'use client';

import React, { useState, useEffect, useRef } from 'react';
import api from '@/services/api';
import { formatNaira } from '@/utils/currency';

interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  data?: any;
}

const TabButton = ({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
      active
        ? 'bg-gray-700 text-white border-b-2 border-orange-500'
        : 'text-gray-400 hover:bg-gray-700/50'
    }`}
  >
    {children}
  </button>
);

const InputField = ({ label, value, onChange, placeholder, type = 'text' }: { label: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; placeholder: string; type?: string }) => (
  <div>
    <label className="block text-xs text-gray-400 mb-1">{label}</label>
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="w-full bg-gray-900 text-white px-3 py-2 rounded border border-gray-600 focus:border-orange-500 focus:outline-none"
    />
  </div>
);

const PaymentTestingPanel = () => {
  const [activeTab, setActiveTab] = useState<'create' | 'fund' | 'transfer'>('create');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Form state
  const [createUserId, setCreateUserId] = useState('');
  const [fundAccountNumber, setFundAccountNumber] = useState('');
  const [fundAmount, setFundAmount] = useState('');
  const [transferFrom, setTransferFrom] = useState('');
  const [transferTo, setTransferTo] = useState('');
  const [transferAmount, setTransferAmount] = useState('');

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const addLog = (message: string, level: 'info' | 'success' | 'warning' | 'error' = 'info', data?: any) => {
    const newLog: LogEntry = {
      id: `log-${Date.now()}-${Math.random()}`,
      timestamp: new Date().toLocaleTimeString(), message, level, data
    };
    setLogs(prev => [...prev, newLog]);
  };

  const handleCreateVA = async () => {
    setIsLoading(true);
    addLog(`🚀 Creating VA for User ID: ${createUserId}...`, 'info');
    try {
      const response = await api.post('/testing/test-create-va', { user_id: parseInt(createUserId) });
      addLog('✅ VA Creation Successful!', 'success', response.data);
      // Auto-fill fund account number for convenience
      setFundAccountNumber(response.data.virtual_account.account_number);
    } catch (error: any) {
      addLog(`❌ VA Creation Failed: ${error.response?.data?.detail || error.message}`, 'error');
    }
    setIsLoading(false);
  };

  const handleFundVA = async () => {
    setIsLoading(true);
    addLog(`🚀 Funding VA ${fundAccountNumber} with ₦${fundAmount}...`, 'info');
    try {
      const response = await api.post('/testing/test-fund-va', { 
        virtual_account_number: fundAccountNumber,
        amount: parseFloat(fundAmount) 
      });
      addLog('✅ VA Funding Simulation Successful!', 'success', response.data);
    } catch (error: any) {
      addLog(`❌ VA Funding Failed: ${error.response?.data?.detail || error.message}`, 'error');
    }
    setIsLoading(false);
  };

  const handleTransferVA = async () => {
    setIsLoading(true);
    addLog(`🚀 Transferring ₦${transferAmount} from ${transferFrom} to ${transferTo}...`, 'info');
    try {
      const response = await api.post('/testing/test-transfer-va', {
        from_account: transferFrom,
        to_account: transferTo,
        amount: parseFloat(transferAmount)
      });
      addLog('✅ VA Transfer Successful!', 'success', response.data);
    } catch (error: any) {
      addLog(`❌ VA Transfer Failed: ${error.response?.data?.detail || error.message}`, 'error');
    }
    setIsLoading(false);
  };
  
  const getLogColor = (level: string) => ({
    success: 'text-green-400', warning: 'text-yellow-400', error: 'text-red-400', info: 'text-blue-400'
  }[level] || 'text-blue-400');

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <div className="border-b border-gray-600 mb-4">
        <nav className="-mb-px flex space-x-4">
          <TabButton active={activeTab === 'create'} onClick={() => setActiveTab('create')}>1. Create VA</TabButton>
          <TabButton active={activeTab === 'fund'} onClick={() => setActiveTab('fund')}>2. Fund VA</TabButton>
          <TabButton active={activeTab === 'transfer'} onClick={() => setActiveTab('transfer')}>3. Transfer</TabButton>
        </nav>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Forms Panel */}
        <div>
          {activeTab === 'create' && (
            <div className="space-y-4">
              <InputField label="User ID" value={createUserId} onChange={e => setCreateUserId(e.target.value)} placeholder="e.g., 1" />
              <button onClick={handleCreateVA} disabled={isLoading || !createUserId} className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 rounded-lg disabled:bg-gray-600">
                {isLoading ? 'Creating...' : 'Create Virtual Account'}
              </button>
            </div>
          )}
          {activeTab === 'fund' && (
            <div className="space-y-4">
              <InputField label="Virtual Account Number" value={fundAccountNumber} onChange={e => setFundAccountNumber(e.target.value)} placeholder="Enter account number" />
              <InputField label="Amount (Naira)" value={fundAmount} onChange={e => setFundAmount(e.target.value)} placeholder="e.g., 5000" type="number" />
              <button onClick={handleFundVA} disabled={isLoading || !fundAccountNumber || !fundAmount} className="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-2 rounded-lg disabled:bg-gray-600">
                {isLoading ? 'Funding...' : 'Simulate Funding'}
              </button>
            </div>
          )}
          {activeTab === 'transfer' && (
            <div className="space-y-4">
              <InputField label="From Account Number" value={transferFrom} onChange={e => setTransferFrom(e.target.value)} placeholder="Source VA number" />
              <InputField label="To Account Number" value={transferTo} onChange={e => setTransferTo(e.target.value)} placeholder="Destination VA number" />
              <InputField label="Amount (Naira)" value={transferAmount} onChange={e => setTransferAmount(e.target.value)} placeholder="e.g., 1000" type="number" />
              <button onClick={handleTransferVA} disabled={isLoading || !transferFrom || !transferTo || !transferAmount} className="w-full bg-orange-500 hover:bg-orange-600 text-white font-medium py-2 rounded-lg disabled:bg-gray-600">
                {isLoading ? 'Transferring...' : 'Initiate Transfer'}
              </button>
            </div>
          )}
        </div>

        {/* Logs Panel */}
        <div className="bg-gray-900 rounded-lg border border-gray-600 h-[300px] flex flex-col">
          <div className="flex justify-between items-center p-3 border-b border-gray-600">
            <h4 className="text-white font-medium">Real-time Logs</h4>
            <button onClick={() => setLogs([])} className="text-xs text-gray-400 hover:text-white">Clear</button>
          </div>
          <div className="p-4 overflow-y-auto flex-1">
            {logs.length === 0 ? (
              <div className="text-gray-500 text-center py-8">Logs will appear here...</div>
            ) : (
              <div className="space-y-2">
                {logs.map((log) => (
                  <div key={log.id} className="font-mono text-sm">
                    <span className="text-gray-500 mr-2">{log.timestamp}</span>
                    <span className={`${getLogColor(log.level)}`}>{log.message}</span>
                    {log.data && <pre className="mt-1 text-xs text-gray-400 bg-gray-800 p-2 rounded whitespace-pre-wrap">{JSON.stringify(log.data, null, 2)}</pre>}
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentTestingPanel;