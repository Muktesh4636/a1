import React, { useState, useEffect } from 'react';
import api from '../services/api';
import WalletDeposit from './WalletDeposit';
import WalletWithdraw from './WalletWithdraw';
import PaymentTransactions from './PaymentTransactions';

export default function Profile({ user, wallet, onLogout, onRefreshWallet }) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await api.getTransactions();
      setTransactions(data.results || data || []);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getTransactionColor = (type) => {
    switch (type) {
      case 'WIN':
        return 'text-green-400';
      case 'BET':
        return 'text-red-400';
      case 'DEPOSIT':
        return 'text-blue-400';
      case 'WITHDRAW':
        return 'text-orange-400';
      default:
        return 'text-white';
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white/10 rounded-lg p-6 backdrop-blur-sm">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">Profile</h2>
        <button
          onClick={onLogout}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Logout
        </button>
      </div>

      {/* User Info */}
      <div className="bg-white/5 rounded-lg p-4 mb-4">
        <h3 className="text-lg font-semibold text-white mb-2">User Information</h3>
        <div className="space-y-2 text-white/80">
          <p><strong>Username:</strong> {user?.username}</p>
          <p><strong>Email:</strong> {user?.email}</p>
        </div>
      </div>

      {/* Wallet */}
      <div className="bg-white/5 rounded-lg p-4 mb-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Wallet Balance</h3>
            <p className="text-3xl font-bold text-green-400">₹{wallet?.balance || '0.00'}</p>
          </div>
          <button
            onClick={onRefreshWallet}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Transactions */}
      <div className="bg-white/5 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-white mb-4">Transaction History</h3>
        {loading ? (
          <p className="text-white/80">Loading transactions...</p>
        ) : transactions.length === 0 ? (
          <p className="text-white/80">No transactions yet</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {transactions.map((tx) => (
              <div
                key={tx.id}
                className="bg-white/5 rounded p-3 flex justify-between items-center"
              >
                <div>
                  <p className={`font-semibold ${getTransactionColor(tx.transaction_type)}`}>
                    {tx.transaction_type}
                  </p>
                  <p className="text-white/60 text-sm">{tx.description || 'No description'}</p>
                  <p className="text-white/40 text-xs">{formatDate(tx.created_at)}</p>
                </div>
                <div className="text-right">
                  <p className={`font-bold ${getTransactionColor(tx.transaction_type)}`}>
                    {['BET', 'WITHDRAW'].includes(tx.transaction_type) ? '-' : '+'}₹{parseFloat(tx.amount).toFixed(2)}
                  </p>
                  <p className="text-white/60 text-sm">
                    Balance: ₹{parseFloat(tx.balance_after).toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Wallet Operations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Deposit Section */}
        <div className="bg-gradient-to-br from-blue-500/20 to-indigo-500/20 backdrop-blur-sm rounded-lg p-4 border border-blue-500/30">
          <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
            💰 Deposit Funds
          </h4>
          <WalletDeposit
            user={user}
            onSuccess={() => {
              onRefreshWallet?.();
              loadTransactions();
            }}
          />
        </div>

        {/* Withdraw Section */}
        <div className="bg-gradient-to-br from-orange-500/20 to-red-500/20 backdrop-blur-sm rounded-lg p-4 border border-orange-500/30">
          <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
            💸 Withdraw Funds
          </h4>
          <WalletWithdraw
            onSuccess={() => {
              onRefreshWallet?.();
              loadTransactions();
            }}
          />
        </div>
      </div>

      <div className="mt-6">
        <PaymentTransactions />
      </div>
    </div>
  );
}




