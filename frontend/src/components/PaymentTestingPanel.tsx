'use client';

import React, { useState, useEffect, useRef } from 'react';
import { formatNaira } from '@/utils/currency';

interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  level: 'info' | 'success' | 'warning' | 'error';
  data?: any;
}

interface SimulationSummary {
  virtual_accounts_created: number;
  payments_simulated: number;
  settlements_triggered: number;
  gaps_transfers: number;
  total_amount_processed: number;
  commission_calculated: number;
}

const PaymentTestingPanel = () => {
  const [simulationLogs, setSimulationLogs] = useState<LogEntry[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationSummary, setSimulationSummary] = useState<SimulationSummary | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<'single' | 'bulk' | 'settlement'>('single');
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
    setSimulationSummary(null);
  };

  const simulatePaymentFlow = async () => {
    setIsSimulating(true);
    setSimulationLogs([]);
    setSimulationSummary(null);

    try {
      addLog('🚀 Starting payment flow simulation...', 'info');
      addLog(`📋 Scenario: ${selectedScenario.toUpperCase()} payment simulation`, 'info');

      const response = await fetch('/api/v1/testing/simulate-payment-flow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          scenario: selectedScenario,
          amount: selectedScenario === 'bulk' ? 150000 : 50000,
          virtual_account_count: selectedScenario === 'bulk' ? 3 : 1
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        // Display logs from backend
        result.logs?.forEach((log: any) => {
          addLog(log.message, log.level, log.data);
        });

        // Display summary
        if (result.summary) {
          setSimulationSummary(result.summary);
          addLog('📊 Simulation completed successfully!', 'success');
        }
      } else {
        addLog(`❌ Simulation failed: ${result.error}`, 'error');
      }

    } catch (error) {
      console.error('Payment simulation error:', error);
      addLog(`❌ Network error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    } finally {
      setIsSimulating(false);
    }
  };

  const simulateVirtualAccountCreation = async () => {
    setIsSimulating(true);
    addLog('🏦 Creating virtual account for testing...', 'info');

    try {
      const response = await fetch('/api/v1/testing/create-test-virtual-account', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      const result = await response.json();

      if (result.success) {
        addLog(`✅ Virtual account created: ${result.virtual_account.account_number}`, 'success');
        addLog(`🏪 Bank: ${result.virtual_account.bank_name}`, 'info');
        addLog(`👤 Account Name: ${result.virtual_account.account_name}`, 'info');
      } else {
        addLog(`❌ Failed to create virtual account: ${result.error}`, 'error');
      }
    } catch (error) {
      addLog(`❌ Error creating virtual account: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
    } finally {
      setIsSimulating(false);
    }
  };

  const simulateDirectPayment = async () => {
    setIsSimulating(true);
    addLog('💳 Simulating direct payment to virtual account...', 'info');

    try {
      const response = await fetch('/api/v1/testing/simulate-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          virtual_account_number: '1234567890', // This would be dynamic
          amount: 75000
        })
      });

      const result = await response.json();

      if (result.success) {
        addLog(`✅ Payment simulation successful: ${formatNaira(75000)}`, 'success');
        addLog(`📨 Webhook should be triggered shortly...`, 'info');
      } else {
        addLog(`❌ Payment simulation failed: ${result.message}`, 'error');
      }
    } catch (error) {
      addLog(`❌ Error simulating payment: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
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
        <div className="flex items-center gap-2">
          <span className="text-gray-400 text-sm">Scenario:</span>
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value as any)}
            disabled={isSimulating}
            className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 focus:border-orange-500 focus:outline-none"
          >
            <option value="single">Single Payment</option>
            <option value="bulk">Bulk Payments</option>
            <option value="settlement">Settlement Flow</option>
          </select>
        </div>
      </div>

      {/* Simulation Controls */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-6">
        <button
          onClick={simulatePaymentFlow}
          disabled={isSimulating}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isSimulating
              ? 'bg-gray-600 cursor-not-allowed text-gray-400'
              : 'bg-orange-500 hover:bg-orange-600 text-white'
          }`}
        >
          {isSimulating ? 'Simulating...' : 'Full Payment Flow'}
        </button>

        <button
          onClick={simulateVirtualAccountCreation}
          disabled={isSimulating}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isSimulating
              ? 'bg-gray-600 cursor-not-allowed text-gray-400'
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          Create Virtual Account
        </button>

        <button
          onClick={simulateDirectPayment}
          disabled={isSimulating}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            isSimulating
              ? 'bg-gray-600 cursor-not-allowed text-gray-400'
              : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
        >
          Simulate Payment
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

      {/* Simulation Summary */}
      {simulationSummary && (
        <div className="bg-gray-900 rounded-lg p-4 mb-4 border border-gray-600">
          <h4 className="text-white font-semibold mb-3">Simulation Summary</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Virtual Accounts:</span>
              <div className="text-white font-medium">{simulationSummary.virtual_accounts_created}</div>
            </div>
            <div>
              <span className="text-gray-400">Payments:</span>
              <div className="text-white font-medium">{simulationSummary.payments_simulated}</div>
            </div>
            <div>
              <span className="text-gray-400">Settlements:</span>
              <div className="text-white font-medium">{simulationSummary.settlements_triggered}</div>
            </div>
            <div>
              <span className="text-gray-400">GAPS Transfers:</span>
              <div className="text-white font-medium">{simulationSummary.gaps_transfers}</div>
            </div>
            <div>
              <span className="text-gray-400">Total Amount:</span>
              <div className="text-white font-medium">{formatNaira(simulationSummary.total_amount_processed)}</div>
            </div>
            <div>
              <span className="text-gray-400">Commission:</span>
              <div className="text-white font-medium">{formatNaira(simulationSummary.commission_calculated)}</div>
            </div>
          </div>
        </div>
      )}

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

      {/* Scenario Descriptions */}
      <div className="mt-4 p-4 bg-gray-900 rounded-lg border border-gray-600">
        <h4 className="text-white font-medium mb-2">Scenario Descriptions</h4>
        <div className="text-sm text-gray-400 space-y-1">
          <div><strong>Single Payment:</strong> Tests one virtual account with ₦50,000 payment and settlement trigger</div>
          <div><strong>Bulk Payments:</strong> Tests 3 virtual accounts with ₦25k, ₦50k, ₦75k payments simultaneously</div>
          <div><strong>Settlement Flow:</strong> Tests complete flow including GAPS bulk transfer and commission calculations</div>
        </div>
      </div>
    </div>
  );
};

export default PaymentTestingPanel;
