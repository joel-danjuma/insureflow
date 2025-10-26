'use client';

import React, { useState, useEffect, useRef } from 'react';
import api from '@/services/api';

interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  data?: any;
}

const PaymentTestingPanel = () => {
  const [simulationLogs, setSimulationLogs] = useState<LogEntry[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [simulationLogs]);

  const addLog = (message: string, level: 'info' | 'success' | 'warning' | 'error' = 'info', data?: any) => {
    const newLog: LogEntry = {
      id: `log-${Date.now()}-${Math.random()}`,
      timestamp: new Date().toLocaleTimeString(),
      message,
      level,
      data
    };
    setSimulationLogs(prev => [...prev, newLog]);
  };

  const clearLogs = () => {
    setSimulationLogs([]);
  };

  const runFullPaymentFlowTest = async () => {
    setIsSimulating(true);
    clearLogs();
    addLog('🚀 Starting full payment flow test...', 'info');

    try {
      const response = await api.post('/testing/test-full-payment-flow');
      const result = response.data;

      if (result.success) {
        addLog('✅ Virtual account creation successful!', 'success', result.virtual_account_details);
        addLog('✅ Payment simulation successful!', 'success', result.payment_simulation_details);
        addLog('🎉 Full payment flow test completed successfully.', 'success');
      } else {
        addLog(`❌ Test failed: ${result.message}`, 'error', result);
      }
    } catch (error: any) {
      console.error('Full payment flow test error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'An unknown network error occurred';
      addLog(`❌ Test failed: ${errorMessage}`, 'error');
    } finally {
      setIsSimulating(false);
    }
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'success': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-blue-400';
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-white text-xl font-semibold">Payment Flow Testing</h3>
      </div>

      {/* Simulation Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
        <button
          onClick={runFullPaymentFlowTest}
          disabled={isSimulating}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isSimulating
              ? 'bg-gray-600 cursor-not-allowed text-gray-400'
              : 'bg-orange-500 hover:bg-orange-600 text-white'
          }`}
        >
          {isSimulating ? 'Testing...' : 'Run Full Payment Flow Test'}
        </button>

        <button
          onClick={clearLogs}
          disabled={isSimulating}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isSimulating
              ? 'bg-gray-600 cursor-not-allowed text-gray-400'
              : 'bg-gray-600 hover:bg-gray-700 text-white'
          }`}
        >
          Clear Logs
        </button>
      </div>

      {/* Real-time Logs */}
      <div className="bg-gray-900 rounded-lg border border-gray-600">
        <div className="flex justify-between items-center p-3 border-b border-gray-600">
          <h4 className="text-white font-medium">Real-time Logs</h4>
          <span className="text-gray-400 text-sm">{simulationLogs.length} entries</span>
        </div>
        
        <div className="p-4 h-80 overflow-y-auto">
          {simulationLogs.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              No logs yet. Start a simulation to see real-time updates.
            </div>
          ) : (
            <div className="space-y-2">
              {simulationLogs.map((log) => (
                <div key={log.id} className="flex items-start gap-3 font-mono text-sm">
                  <span className="text-gray-500 text-xs mt-1 min-w-[80px]">
                    {log.timestamp}
                  </span>
                  <span className="mt-1">{getLogIcon(log.level)}</span>
                  <div className={`flex-1 ${getLogColor(log.level)}`}>
                    {log.message}
                    {log.data && (
                      <div className="mt-1 text-xs text-gray-400 bg-gray-800 p-2 rounded">
                        {JSON.stringify(log.data, null, 2)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentTestingPanel;