import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function WalletDeposit({ user, onSuccess }) {
  const [amount, setAmount] = useState('');
  const [paymentLink, setPaymentLink] = useState('');
  const [paymentReference, setPaymentReference] = useState('');
  const [screenshotFile, setScreenshotFile] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [isGeneratingLink, setIsGeneratingLink] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [requests, setRequests] = useState([]);
  const [loadingRequests, setLoadingRequests] = useState(false);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [isExtractingUtr, setIsExtractingUtr] = useState(false);

  const loadRequests = async () => {
    try {
      setLoadingRequests(true);
      const data = await api.getMyDepositRequests();
      setRequests(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingRequests(false);
    }
  };

  const loadPaymentMethods = async () => {
    try {
      const data = await api.getPaymentMethods();
      setPaymentMethods(data);
      if (data.length > 0) {
        setSelectedMethod(data[0]);
      }
    } catch (err) {
      console.error('Error loading payment methods:', err);
    }
  };

  useEffect(() => {
    loadRequests();
    loadPaymentMethods();
  }, []);

  const handleScreenshotChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setScreenshotFile(file);
    
    // Auto-extract UTR using the new advanced API
    try {
      setIsExtractingUtr(true);
      setStatusMessage('Analyzing screenshot for UTR...');
      const result = await api.processScreenshot(file, user?.id, amount);
      if (result.success && result.utr) {
        setPaymentReference(result.utr);
        setStatusMessage('UTR extracted automatically!');
      } else {
        setStatusMessage(result.message || 'Could not extract UTR automatically. Please enter it manually.');
      }
    } catch (err) {
      console.log('UTR extraction failed or not available:', err);
      setStatusMessage('OCR service error. Please enter UTR manually.');
    } finally {
      setIsExtractingUtr(false);
    }
  };

  const resetForm = () => {
    setAmount('');
    setPaymentLink('');
    setPaymentReference('');
    setScreenshotFile(null);
  };

  const handleGenerateLink = async () => {
    if (!amount) {
      setStatusMessage('Enter an amount first.');
      return;
    }
    try {
      setIsGeneratingLink(true);
      setStatusMessage('');
      const data = await api.createDepositLink(amount);
      setPaymentLink(data.payment_link);
      setStatusMessage('Payment link generated. Complete payment then upload the screenshot. Your deposit will be reviewed and approved by admin.');
    } catch (err) {
      setStatusMessage(err.message);
    } finally {
      setIsGeneratingLink(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!screenshotFile) {
      setStatusMessage('Screenshot is required.');
      return;
    }
    try {
      setIsSubmitting(true);
      setStatusMessage('');
      await api.submitDepositRequest({
        amount,
        paymentLink,
        paymentReference,
        screenshot: screenshotFile,
      });
      setStatusMessage('Deposit request submitted successfully! Your request is pending admin approval. Funds will be added to your wallet once approved.');
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
      <h3 className="text-lg font-semibold text-white mb-3">Deposit Funds</h3>
      
      <div className="space-y-4">
        {/* Step 1: Amount */}
        <div>
          <label className="block text-white/80 text-sm mb-1">1. Enter Amount (₹)</label>
          <input
            type="number"
            min="1"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full px-3 py-2 rounded bg-white/10 text-white border border-white/20 focus:outline-none"
            placeholder="Enter amount"
            required
          />
        </div>

        {/* Step 2: Payment Method Selection */}
        {paymentMethods.length > 0 && (
          <div>
            <label className="block text-white/80 text-sm mb-2">2. Select Payment Method</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {paymentMethods.map((method) => (
                <button
                  key={method.id}
                  type="button"
                  onClick={() => setSelectedMethod(method)}
                  className={`p-3 rounded-lg border text-sm transition-all flex flex-col items-center gap-2 ${
                    selectedMethod?.id === method.id
                      ? 'bg-indigo-600/40 border-indigo-500 text-white'
                      : 'bg-white/5 border-white/10 text-white/60 hover:bg-white/10'
                  }`}
                >
                  <span className="text-xl">
                    {method.method_type === 'PHONEPE' && '📱'}
                    {method.method_type === 'GPAY' && '🇬'}
                    {method.method_type === 'PAYTM' && '🅿️'}
                    {method.method_type === 'UPI_QR' && '🔍'}
                    {method.method_type === 'BANK' && '🏦'}
                  </span>
                  <span>{method.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Payment Details */}
        {selectedMethod && (
          <div className="bg-indigo-900/20 border border-indigo-500/30 rounded-lg p-4 space-y-3 animate-fadeIn">
            <h4 className="text-indigo-200 font-bold text-sm border-bottom border-indigo-500/30 pb-2">
              Payment Details for {selectedMethod.name}
            </h4>
            
            {selectedMethod.qr_code && (
              <div className="flex flex-col items-center gap-2 py-2">
                <img 
                  src={selectedMethod.qr_code} 
                  alt="QR Code" 
                  className="w-48 h-48 rounded-lg bg-white p-2"
                />
                <span className="text-xs text-indigo-200">Scan QR to pay</span>
              </div>
            )}

            <div className="grid grid-cols-1 gap-2 text-sm">
              {selectedMethod.account_name && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-white/60">Name:</span>
                  <span className="text-white font-mono">{selectedMethod.account_name}</span>
                </div>
              )}
              {selectedMethod.upi_id && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-white/60">UPI ID:</span>
                  <span className="text-white font-mono">{selectedMethod.upi_id}</span>
                </div>
              )}
              {selectedMethod.account_number && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-white/60">Account:</span>
                  <span className="text-white font-mono">{selectedMethod.account_number}</span>
                </div>
              )}
              {selectedMethod.ifsc_code && (
                <div className="flex justify-between border-b border-white/5 py-1">
                  <span className="text-white/60">IFSC:</span>
                  <span className="text-white font-mono">{selectedMethod.ifsc_code}</span>
                </div>
              )}
            </div>
            
            <p className="text-[10px] text-indigo-300/70 italic text-center mt-2">
              Pay the amount then enter the transaction ID below.
            </p>
          </div>
        )}

        <form className="space-y-4" onSubmit={handleSubmit}>
          {/* Step 4: Screenshot & Reference */}
          <div className="space-y-3">
            <label className="block text-white/80 text-sm mb-1">3. Proof of Payment</label>
            
            <div className="relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleScreenshotChange}
                className="w-full text-sm text-white/60 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
                required
              />
              {isExtractingUtr && (
                <div className="mt-2 flex items-center gap-2 text-xs text-indigo-300">
                  <span className="animate-spin text-lg">⏳</span>
                  Analyzing screenshot for UTR...
                </div>
              )}
            </div>

            <div>
              <input
                type="text"
                value={paymentReference}
                onChange={(e) => setPaymentReference(e.target.value)}
                className="w-full px-3 py-2 rounded bg-white/10 text-white border border-white/20 focus:outline-none"
                placeholder="Transaction ID / UTR / Reference"
              />
              <span className="text-[10px] text-white/40 mt-1 block">Usually 12 digits for UPI</span>
            </div>
          </div>

          {statusMessage && (
            <div className={`text-sm p-3 rounded ${statusMessage.includes('success') ? 'bg-green-500/20 text-green-200' : 'bg-red-500/20 text-red-200'}`}>
              {statusMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !amount || !screenshotFile}
            className="w-full px-4 py-3 rounded bg-green-600 text-white font-bold hover:bg-green-700 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-lg shadow-green-900/20"
          >
            {isSubmitting ? 'Submitting...' : 'Complete Deposit'}
          </button>
        </form>
      </div>

      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-white font-semibold">Recent Deposit Requests</h4>
          <button
            onClick={loadRequests}
            className="text-xs text-white/70 underline"
            disabled={loadingRequests}
          >
            {loadingRequests ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        {requests.length === 0 ? (
          <p className="text-white/60 text-sm">No deposit requests yet.</p>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
            {requests.map((request) => (
              <div key={request.id} className="bg-white/5 rounded p-3 text-white/80">
                <div className="flex justify-between items-center">
                  <span className="font-semibold">₹{parseFloat(request.amount).toFixed(2)}</span>
                  {renderStatusBadge(request.status)}
                </div>
                <p className="text-xs mt-1">
                  Submitted: {new Date(request.created_at).toLocaleString()}
                </p>
                {request.admin_note && (
                  <div className={`mt-2 p-2 border rounded text-xs ${
                    request.status === 'REJECTED' 
                      ? 'bg-red-500/10 border-red-500/20 text-red-200' 
                      : 'bg-green-500/10 border-green-500/20 text-green-200'
                  }`}>
                    <strong>Admin Message:</strong> {request.admin_note}
                  </div>
                )}
                {request.payment_reference && (
                  <p className="text-xs mt-1">Reference: {request.payment_reference}</p>
                )}
                {request.screenshot_url && (
                  <a
                    href={request.screenshot_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-200 underline mt-1 inline-block"
                  >
                    View Screenshot
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

