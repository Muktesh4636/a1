import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function WalletWithdraw({ onSuccess }) {
  const [amount, setAmount] = useState('');
  const [withdrawalMethod, setWithdrawalMethod] = useState('');
  const [withdrawalDetails, setWithdrawalDetails] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [requests, setRequests] = useState([]);
  const [loadingRequests, setLoadingRequests] = useState(false);
  
  // Bank Details State
  const [savedBankDetails, setSavedBankDetails] = useState([]);
  const [showAddBankForm, setShowBankForm] = useState(false);
  const [selectedSavedId, setSelectedSavedId] = useState(null);
  const [saveBankInfo, setSaveBankInfo] = useState(false);
  const [newBankDetail, setNewBankDetail] = useState({
    account_name: '',
    bank_name: '',
    account_number: '',
    ifsc_code: '',
    upi_id: '',
    is_default: true
  });

  const loadRequests = async () => {
    try {
      setLoadingRequests(true);
      const data = await api.getMyWithdrawRequests();
      setRequests(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingRequests(false);
    }
  };

  const loadBankDetails = async () => {
    try {
      const data = await api.getMyBankDetails();
      setSavedBankDetails(data);
      // Auto-select default or first one
      const defaultDetail = data.find(d => d.is_default) || data[0];
      if (defaultDetail) {
        setSelectedSavedId(defaultDetail.id);
        setWithdrawalMethod(defaultDetail.bank_name ? 'Bank Transfer' : 'UPI');
        const details = defaultDetail.upi_id 
          ? `UPI ID: ${defaultDetail.upi_id}\nName: ${defaultDetail.account_name}` 
          : `Name: ${defaultDetail.account_name}\nBank: ${defaultDetail.bank_name}\nA/C: ${defaultDetail.account_number}\nIFSC: ${defaultDetail.ifsc_code}`;
        setWithdrawalDetails(details);
      }
    } catch (err) {
      console.error('Error loading bank details:', err);
    }
  };

  useEffect(() => {
    loadRequests();
    loadBankDetails();
  }, []);

  const handleSelectSavedDetail = (detail) => {
    setSelectedSavedId(detail.id);
    setShowBankForm(false);
    setWithdrawalMethod(detail.bank_name ? 'Bank Transfer' : 'UPI');
    let details = '';
    if (detail.upi_id) {
      details = `UPI ID: ${detail.upi_id}\nName: ${detail.account_name}`;
    } else {
      details = `Name: ${detail.account_name}\nBank: ${detail.bank_name}\nA/C: ${detail.account_number}\nIFSC: ${detail.ifsc_code}`;
    }
    setWithdrawalDetails(details);
    setStatusMessage(`Selected: ${detail.account_name} (${detail.upi_id || detail.bank_name})`);
  };

  const handleAddNewToggle = () => {
    setShowBankForm(true);
    setSelectedSavedId(null);
    setWithdrawalMethod('');
    setWithdrawalDetails('');
  };

  const handleSaveBankDetail = async (e) => {
    e.preventDefault();
    try {
      await api.addBankDetail(newBankDetail);
      setStatusMessage('Bank details saved successfully!');
      setShowBankForm(false);
      loadBankDetails();
      setNewBankDetail({
        account_name: '',
        bank_name: '',
        account_number: '',
        ifsc_code: '',
        upi_id: '',
        is_default: false
      });
    } catch (err) {
      setStatusMessage('Error saving bank details: ' + err.message);
    }
  };

  const resetForm = () => {
    setAmount('');
    // Don't reset method/details if they are using a saved one
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!withdrawalMethod || !withdrawalDetails) {
      setStatusMessage('Please fill in all withdrawal details.');
      return;
    }
    try {
      setIsSubmitting(true);
      setStatusMessage('');
      await api.initiateWithdraw({
        amount,
        withdrawalMethod,
        withdrawalDetails,
      });
      setStatusMessage('Withdraw request submitted successfully! Your details will be saved for future use once approved by admin.');
      resetForm();
      loadRequests();
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setStatusMessage(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED':
        return <span className="px-2 py-1 text-xs rounded bg-green-500/20 text-green-200">Approved</span>;
      case 'REJECTED':
        return <span className="px-2 py-1 text-xs rounded bg-red-500/20 text-red-200">Rejected</span>;
      default:
        return <span className="px-2 py-1 text-xs rounded bg-yellow-500/20 text-yellow-100">Pending</span>;
    }
  };

  return (
    <div className="bg-white/5 rounded-lg p-4 mt-4">
      <h3 className="text-lg font-semibold text-white mb-3">Withdraw Funds</h3>
      <p className="text-sm text-white/70 mb-4">
        Request withdrawal from your wallet. Enter your withdrawal details and submit the request. Your withdrawal will be reviewed by admin and funds will be transferred once approved.
      </p>

      <form className="space-y-4" onSubmit={handleSubmit}>
        {/* Step 1: Amount */}
        <div className="bg-white/5 p-4 rounded-lg border border-white/10 mb-2">
          <label className="block text-white font-semibold text-sm mb-2">💰 Withdrawal Amount</label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-green-400 font-bold">₹</span>
            <input
              type="number"
              min="1"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full pl-8 pr-3 py-3 rounded bg-black/40 text-white border border-white/20 focus:outline-none focus:border-orange-500 text-lg font-bold shadow-inner"
              placeholder="0.00"
              required
            />
          </div>
        </div>

        {/* Step 2: Choose Destination */}
        <div className="bg-white/5 p-4 rounded-lg border border-white/10">
          <label className="block text-white font-semibold text-sm mb-3">📍 Withdrawal Destination</label>
          
          {/* Saved Details Selection */}
          {savedBankDetails.length > 0 && (
            <div className="space-y-2 mb-4">
              <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-1">
                {savedBankDetails.map(detail => (
                  <button
                    key={detail.id}
                    type="button"
                    onClick={() => handleSelectSavedDetail(detail)}
                    className={`w-full text-left p-3 rounded-xl border transition-all flex justify-between items-center group ${
                      selectedSavedId === detail.id
                        ? 'bg-orange-500/20 border-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.2)]'
                        : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                        selectedSavedId === detail.id ? 'bg-orange-500 text-white' : 'bg-white/10 text-white/60'
                      }`}>
                        {detail.bank_name ? '🏦' : '📱'}
                      </div>
                      <div className="text-xs">
                        <p className={`font-bold ${selectedSavedId === detail.id ? 'text-white' : 'text-white/80'}`}>
                          {detail.account_name}
                        </p>
                        <p className="text-white/50 font-mono">
                          {detail.upi_id || `${detail.bank_name} (${detail.account_number.slice(-4)})`}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      {detail.is_default && <span className="text-[9px] bg-indigo-500/40 text-indigo-100 px-2 py-0.5 rounded-full font-bold uppercase tracking-tighter">Default</span>}
                      {selectedSavedId === detail.id && <span className="text-orange-500 text-lg">✓</span>}
                    </div>
                  </button>
                ))}
              </div>
              
              <button 
                type="button"
                onClick={handleAddNewToggle}
                className={`w-full py-2 border-2 border-dashed rounded-xl text-xs font-bold transition-all ${
                  showAddBankForm 
                    ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                    : 'bg-white/5 border-white/10 text-white/40 hover:bg-white/10 hover:text-white/60'
                }`}
              >
                {showAddBankForm ? '✕ Cancel New Entry' : '⊕ Add New Account / UPI'}
              </button>
            </div>
          )}

          {/* Add Bank Form */}
          {(showAddBankForm || savedBankDetails.length === 0) && (
            <div className="bg-black/20 p-4 rounded-xl border border-indigo-500/30 space-y-4 animate-fadeIn">
              <h4 className="text-indigo-300 text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
                <span className="w-5 h-5 bg-indigo-500/20 rounded flex items-center justify-center">!</span>
                New Withdrawal Info
              </h4>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-[10px] text-white/40 ml-1">Account Holder Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 rounded bg-white/5 text-white border border-white/10 text-sm outline-none focus:border-indigo-500"
                    value={newBankDetail.account_name}
                    onChange={e => setNewBankDetail({...newBankDetail, account_name: e.target.value})}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-white/40 ml-1">UPI ID (Optional)</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 rounded bg-white/5 text-white border border-white/10 text-sm outline-none focus:border-indigo-500"
                    value={newBankDetail.upi_id}
                    onChange={e => setNewBankDetail({...newBankDetail, upi_id: e.target.value})}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-white/40 ml-1">Bank Name</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 rounded bg-white/5 text-white border border-white/10 text-sm outline-none focus:border-indigo-500"
                    value={newBankDetail.bank_name}
                    onChange={e => setNewBankDetail({...newBankDetail, bank_name: e.target.value})}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-white/40 ml-1">Account Number</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 rounded bg-white/5 text-white border border-white/10 text-sm outline-none focus:border-indigo-500"
                    value={newBankDetail.account_number}
                    onChange={e => setNewBankDetail({...newBankDetail, account_number: e.target.value})}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-white/40 ml-1">IFSC Code</label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 rounded bg-white/5 text-white border border-white/10 text-sm outline-none focus:border-indigo-500"
                    value={newBankDetail.ifsc_code}
                    onChange={e => setNewBankDetail({...newBankDetail, ifsc_code: e.target.value})}
                  />
                </div>
                <div className="flex items-center pt-4">
                  <label className="flex items-center gap-2 text-white/70 text-xs cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="accent-indigo-500"
                      checked={newBankDetail.is_default}
                      onChange={e => setNewBankDetail({...newBankDetail, is_default: e.target.checked})}
                    />
                    Set as Default
                  </label>
                </div>
              </div>
              <button
                type="button"
                onClick={handleSaveBankDetail}
                disabled={!newBankDetail.account_name || (!newBankDetail.upi_id && !newBankDetail.account_number)}
                className="w-full py-2.5 bg-indigo-600 text-white rounded-lg text-xs font-black uppercase tracking-widest hover:bg-indigo-500 disabled:opacity-30 shadow-lg shadow-indigo-900/40"
              >
                💾 Confirm and Save New Details
              </button>
            </div>
          )}
        </div>

        {/* Hidden but used fields for manual entry/display */}
        {(showAddBankForm || savedBankDetails.length === 0) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-white/60 text-[10px] font-black uppercase tracking-widest mb-1 ml-1">Method</label>
              <select
                value={withdrawalMethod}
                onChange={(e) => setWithdrawalMethod(e.target.value)}
                className="w-full px-3 py-2.5 rounded bg-white/5 text-white border border-white/10 focus:outline-none text-sm"
                required
              >
                <option value="">Select Method</option>
                <option value="UPI">UPI</option>
                <option value="Bank Transfer">Bank Transfer</option>
              </select>
            </div>
            <div>
              <label className="block text-white/60 text-[10px] font-black uppercase tracking-widest mb-1 ml-1">Final Details</label>
              <textarea
                value={withdrawalDetails}
                onChange={(e) => setWithdrawalDetails(e.target.value)}
                className="w-full px-3 py-2 rounded bg-white/5 text-white border border-white/10 focus:outline-none min-h-[42px] text-xs"
                placeholder="Details will appear here..."
                required
              />
            </div>
          </div>
        )}

        {statusMessage && (
          <div className={`text-xs p-3 rounded-lg border flex items-center gap-2 ${
            statusMessage.includes('Error') || statusMessage.includes('Please') 
              ? 'bg-red-500/10 border-red-500/30 text-red-300' 
              : 'bg-green-500/10 border-green-500/30 text-green-300'
          }`}>
            <span>{statusMessage.includes('success') ? '✅' : '💡'}</span>
            {statusMessage}
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting || !amount || !withdrawalDetails}
          className="w-full px-4 py-4 rounded-2xl bg-gradient-to-r from-orange-500 to-red-600 text-white font-black text-lg shadow-xl shadow-red-900/20 active:translate-y-1 transition-all disabled:opacity-30 disabled:grayscale uppercase tracking-tighter"
        >
          {isSubmitting ? 'PROCESSING...' : '🚀 SEND WITHDRAW REQUEST'}
        </button>
      </form>

      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-white font-semibold">Recent Withdraw Requests</h4>
          <button
            onClick={loadRequests}
            className="text-xs text-white/70 underline"
            disabled={loadingRequests}
          >
            {loadingRequests ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        {requests.length === 0 ? (
          <p className="text-white/60 text-sm">No withdraw requests yet.</p>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
            {requests.map((request) => (
              <div key={request.id} className="bg-white/5 rounded p-3 text-white/80">
                <div className="flex justify-between items-center">
                  <span className="font-semibold">₹{parseFloat(request.amount).toFixed(2)}</span>
                  {renderStatusBadge(request.status)}
                </div>
                <p className="text-xs mt-1">
                  Method: {request.withdrawal_method}
                </p>
                <p className="text-xs mt-1">
                  Details: {request.withdrawal_details}
                </p>
                <p className="text-xs mt-1">
                  Submitted: {new Date(request.created_at).toLocaleString()}
                </p>
                {request.processed_by_name && (
                  <p className="text-[10px] text-white/40 mt-1 italic">
                    Processed by: {request.processed_by_name}
                  </p>
                )}
                {request.admin_note && (
                  <div className={`mt-2 p-2 border rounded text-xs ${
                    request.status === 'REJECTED' 
                      ? 'bg-red-500/10 border-red-500/20 text-red-200' 
                      : 'bg-green-500/10 border-green-500/20 text-green-200'
                  }`}>
                    <strong>Admin Message:</strong> {request.admin_note}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}