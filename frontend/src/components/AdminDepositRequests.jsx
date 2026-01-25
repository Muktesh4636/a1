import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function AdminDepositRequests({ onActionComplete }) {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadRequests = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.getPendingDeposits();
      setRequests(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const handleApprove = async (id) => {
    try {
      await api.approveDepositRequest(id);
      loadRequests();
      if (onActionComplete) onActionComplete();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReject = async (id) => {
    const note = window.prompt('Reason for rejection (optional):') || '';
    try {
      await api.rejectDepositRequest(id, note);
      loadRequests();
      if (onActionComplete) onActionComplete();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-white/5 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white">Pending Deposit Requests</h3>
        <button
          onClick={loadRequests}
          className="text-sm text-white/70 underline"
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      {error && <p className="text-sm text-red-300 mb-2">{error}</p>}
      {requests.length === 0 ? (
        <p className="text-white/70 text-sm">No pending deposits 🎉</p>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
          {requests.map((request) => (
            <div key={request.id} className="bg-white/5 rounded p-3 text-white/80">
              <div className="flex justify-between items-center mb-2">
                <div>
                  <p className="font-semibold">{request.user?.username}</p>
                  <p className="text-xs text-white/60">
                    {new Date(request.created_at).toLocaleString()}
                  </p>
                </div>
                <span className="text-lg font-bold text-green-300">
                  ₹{parseFloat(request.amount).toFixed(2)}
                </span>
              </div>
              {request.payment_reference && (
                <p className="text-xs mb-2">Reference: {request.payment_reference}</p>
              )}
              {request.screenshot_url && (
                <img
                  src={request.screenshot_url}
                  alt="Payment proof"
                  className="w-full max-h-48 object-cover rounded mb-2 border border-white/10"
                />
              )}
              <div className="flex gap-2">
                <button
                  onClick={() => handleApprove(request.id)}
                  className="flex-1 px-3 py-2 bg-green-600 rounded text-white hover:bg-green-700"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleReject(request.id)}
                  className="flex-1 px-3 py-2 bg-red-600 rounded text-white hover:bg-red-700"
                >
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}





