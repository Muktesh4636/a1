import React, { useEffect, useMemo, useState } from 'react';
import api from '../services/api';

const typeLabels = {
  DEPOSIT: 'Deposit',
  WITHDRAW: 'Withdrawal',
  BET: 'Bet Placed',
  WIN: 'Winnings',
  REFUND: 'Refund',
};

const typeColors = {
  DEPOSIT: 'text-green-300',
  WITHDRAW: 'text-red-300',
  BET: 'text-yellow-200',
  WIN: 'text-emerald-300',
  REFUND: 'text-indigo-200',
};

export default function PaymentTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('ALL');
  const [error, setError] = useState('');

  const loadTransactions = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.getTransactions();
      setTransactions(data.results || data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, []);

  const filteredTransactions = useMemo(() => {
    if (filter === 'ALL') return transactions;
    return transactions.filter((tx) => tx.transaction_type === filter);
  }, [transactions, filter]);

  const totalDeposits = useMemo(() => {
    return transactions
      .filter((tx) => tx.transaction_type === 'DEPOSIT')
      .reduce((sum, tx) => sum + parseFloat(tx.amount), 0);
  }, [transactions]);

  return (
    <div className="bg-white/5 rounded-lg p-4 backdrop-blur-sm">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white">Payment & Wallet Transactions</h3>
          <p className="text-white/60 text-sm">
            Track every deposit, bet, win, and refund in real-time.
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-white/10 text-white text-sm rounded px-3 py-2 border border-white/20 focus:outline-none"
          >
            <option value="ALL">All Types</option>
            <option value="DEPOSIT">Deposits</option>
            <option value="WIN">Wins</option>
            <option value="BET">Bets</option>
            <option value="REFUND">Refunds</option>
            <option value="WITHDRAW">Withdrawals</option>
          </select>
          <button
            onClick={loadTransactions}
            className="px-3 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="bg-white/5 rounded p-4 border border-white/10 mb-4">
        <p className="text-white text-sm font-semibold uppercase tracking-wide">Total Deposited</p>
        <p className="text-3xl font-bold text-green-300">₹{totalDeposits.toFixed(2)}</p>
        <p className="text-white/50 text-xs mt-1">
          Includes all successful deposits credited to your wallet.
        </p>
      </div>

      {error && <p className="text-sm text-red-300 mb-3">{error}</p>}

      {filteredTransactions.length === 0 ? (
        <p className="text-white/70 text-sm">No transactions to display.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm text-white/80">
            <thead>
              <tr className="border-b border-white/10 text-white/60 text-xs uppercase tracking-wide">
                <th className="py-2 pr-4">Type</th>
                <th className="py-2 pr-4">Amount</th>
                <th className="py-2 pr-4">Description</th>
                <th className="py-2 pr-4">Balance After</th>
                <th className="py-2 pr-4">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map((tx) => (
                <tr key={tx.id} className="border-b border-white/5 last:border-0">
                  <td className={`py-3 pr-4 font-semibold ${typeColors[tx.transaction_type] || 'text-white'}`}>
                    {typeLabels[tx.transaction_type] || tx.transaction_type}
                  </td>
                  <td className="py-3 pr-4">
                    {['BET', 'WITHDRAW'].includes(tx.transaction_type) ? '-' : '+'}₹{parseFloat(tx.amount).toFixed(2)}
                  </td>
                  <td className="py-3 pr-4 text-white/70">{tx.description || '—'}</td>
                  <td className="py-3 pr-4">₹{parseFloat(tx.balance_after).toFixed(2)}</td>
                  <td className="py-3 pr-4 text-white/60">
                    {new Date(tx.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}





