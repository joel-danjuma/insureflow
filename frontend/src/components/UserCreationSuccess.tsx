'use client';

import React, { useState } from 'react';

interface UserCreationSuccessProps {
  result: {
    success: boolean;
    user: {
      id: number;
      email: string;
      full_name: string;
      username: string;
      role: string;
    };
    generated_password: string;
    virtual_account?: {
      id: number;
      customer_identifier: string;
      virtual_account_number: string;
      bank_code: string;
      account_type: string;
      status: string;
    } | null;
    message: string;
  };
  onClose: () => void;
}

const UserCreationSuccess: React.FC<UserCreationSuccessProps> = ({ result, onClose }) => {
  const [passwordCopied, setPasswordCopied] = useState(false);
  const [accountCopied, setAccountCopied] = useState(false);

  const copyToClipboard = async (text: string, type: 'password' | 'account') => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'password') {
        setPasswordCopied(true);
        setTimeout(() => setPasswordCopied(false), 2000);
      } else {
        setAccountCopied(true);
        setTimeout(() => setAccountCopied(false), 2000);
      }
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-white text-xl font-bold flex items-center gap-2">
            <span className="text-green-400">✓</span>
            User Created Successfully!
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors text-xl"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* Success Message */}
          <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
            <div className="text-green-400 text-sm">
              <strong>Success:</strong> {result.message}
            </div>
          </div>

          {/* User Details */}
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-semibold mb-3">User Details</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-400">Name:</span>
                <span className="text-white ml-2">{result.user.full_name}</span>
              </div>
              <div>
                <span className="text-gray-400">Username:</span>
                <span className="text-white ml-2">{result.user.username}</span>
              </div>
              <div>
                <span className="text-gray-400">Email:</span>
                <span className="text-white ml-2">{result.user.email}</span>
              </div>
              <div>
                <span className="text-gray-400">Role:</span>
                <span className="text-white ml-2 capitalize">{result.user.role.toLowerCase()}</span>
              </div>
            </div>
          </div>

          {/* Generated Password */}
          <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-4">
            <h4 className="text-orange-400 font-semibold mb-3 flex items-center gap-2">
              🔑 Generated Password
            </h4>
            <div className="flex items-center gap-3">
              <div className="flex-1 bg-gray-700 rounded-lg p-3 font-mono text-white text-lg">
                {result.generated_password}
              </div>
              <button
                onClick={() => copyToClipboard(result.generated_password, 'password')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  passwordCopied
                    ? 'bg-green-600 text-white'
                    : 'bg-orange-500 hover:bg-orange-600 text-white'
                }`}
              >
                {passwordCopied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <p className="text-orange-300 text-sm mt-2">
              ⚠️ <strong>Important:</strong> Please save this password securely and share it with the user. 
              This password will not be shown again.
            </p>
          </div>

          {/* Virtual Account Details */}
          {result.virtual_account ? (
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
              <h4 className="text-blue-400 font-semibold mb-3 flex items-center gap-2">
                🏦 Virtual Account Created
              </h4>
              <div className="space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-400">Account Number:</span>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-white font-mono text-lg">{result.virtual_account.virtual_account_number}</span>
                      <button
                        onClick={() => copyToClipboard(result.virtual_account!.virtual_account_number, 'account')}
                        className={`px-2 py-1 text-xs rounded font-medium transition-colors ${
                          accountCopied
                            ? 'bg-green-600 text-white'
                            : 'bg-blue-500 hover:bg-blue-600 text-white'
                        }`}
                      >
                        {accountCopied ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-400">Bank Code:</span>
                    <span className="text-white ml-2">{result.virtual_account.bank_code}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Account Type:</span>
                    <span className="text-white ml-2 capitalize">{result.virtual_account.account_type}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Status:</span>
                    <span className="text-green-400 ml-2 capitalize">{result.virtual_account.status}</span>
                  </div>
                </div>
                <div>
                  <span className="text-gray-400">Customer ID:</span>
                  <span className="text-white ml-2 font-mono text-sm">{result.virtual_account.customer_identifier}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
              <h4 className="text-yellow-400 font-semibold mb-2">⚠️ Virtual Account Creation Failed</h4>
              <p className="text-yellow-300 text-sm">
                The user was created successfully, but the virtual account could not be created. 
                You can try creating the virtual account manually later.
              </p>
            </div>
          )}

          {/* Next Steps */}
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-semibold mb-3">Next Steps</h4>
            <ul className="text-gray-300 text-sm space-y-2">
              <li>• Share the login credentials with the new user securely</li>
              <li>• Advise the user to change their password on first login</li>
              {result.virtual_account && (
                <li>• The virtual account is ready to receive premium payments</li>
              )}
              <li>• The user can now log in and access the broker dashboard</li>
            </ul>
          </div>
        </div>

        <div className="flex justify-end pt-6">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserCreationSuccess;
