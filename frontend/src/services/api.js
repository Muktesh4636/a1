// Django API service
// Use relative URL to leverage Vite proxy, or absolute URL if VITE_API_URL is set
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  // Get headers with authentication
  getHeaders(contentType = 'application/json') {
    const headers = {
    };
    if (contentType) {
      headers['Content-Type'] = contentType;
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  // Set tokens
  setTokens(access, refresh) {
    this.token = access;
    this.refreshToken = refresh;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  // Clear tokens
  clearTokens() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Handle API response
  async handleResponse(response) {
    if (!response.ok) {
      try {
        const error = await response.json();
        // Check for authentication errors
        if (response.status === 401 || response.status === 403) {
          // Clear tokens if authentication fails
          this.clearTokens();
          throw new Error(error.error || error.detail || error.message || 'Authentication failed. Please log in again.');
        }
        throw new Error(error.error || error.detail || error.message || `Request failed: ${response.statusText}`);
      } catch (e) {
        if (e.message) throw e;
        // Handle non-JSON error responses
        if (response.status === 401 || response.status === 403) {
          this.clearTokens();
          throw new Error('Authentication failed. Please log in again.');
        }
        throw new Error(`Request failed: ${response.status} ${response.statusText}`);
      }
    }
    return response.json();
  }
  
  // Check if backend is available
  async checkConnection() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'OPTIONS',
      });
      return true;
    } catch (err) {
      return false;
    }
  }

  // Authentication
  async register(username, email, password, password2) {
    const response = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, password2 }),
    });
    const data = await this.handleResponse(response);
    if (data.access) {
      this.setTokens(data.access, data.refresh);
    }
    return data;
  }

  async login(username, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await this.handleResponse(response);
      if (data.access) {
        this.setTokens(data.access, data.refresh);
      }
      return data;
    } catch (err) {
      // Improve error message for connection issues
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        throw new Error('Cannot connect to server. Please make sure the Django backend is running.');
      }
      throw err;
    }
  }

  async logout() {
    this.clearTokens();
  }

  async getProfile() {
    const response = await fetch(`${API_BASE_URL}/auth/profile/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  // Wallet
  async getWallet() {
    const response = await fetch(`${API_BASE_URL}/auth/wallet/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async getTransactions() {
    const response = await fetch(`${API_BASE_URL}/auth/transactions/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  // Deposits
  async createDepositLink(amount) {
    const response = await fetch(`${API_BASE_URL}/auth/deposits/initiate/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ amount }),
    });
    return this.handleResponse(response);
  }

  async submitDepositRequest({ amount, paymentLink, paymentReference, screenshot }) {
    const formData = new FormData();
    formData.append('amount', amount);
    if (paymentLink) formData.append('payment_link', paymentLink);
    if (paymentReference) formData.append('payment_reference', paymentReference);
    if (screenshot) formData.append('screenshot', screenshot);

    const response = await fetch(`${API_BASE_URL}/auth/deposits/upload-proof/`, {
      method: 'POST',
      headers: this.getHeaders(null),
      body: formData,
    });
    return this.handleResponse(response);
  }

  async getMyDepositRequests() {
    const response = await fetch(`${API_BASE_URL}/auth/deposits/mine/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async getPaymentMethods() {
    const response = await fetch(`${API_BASE_URL}/auth/payment-methods/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async extractUtr(screenshot) {
    const formData = new FormData();
    formData.append('screenshot', screenshot);
    const response = await fetch(`${API_BASE_URL}/auth/extract-utr/`, {
      method: 'POST',
      headers: this.getHeaders(null),
      body: formData,
    });
    return this.handleResponse(response);
  }

  async processScreenshot(screenshot, userId, amount) {
    const formData = new FormData();
    formData.append('screenshot', screenshot);
    if (userId) formData.append('user_id', userId);
    if (amount) formData.append('amount', amount);
    
    const response = await fetch(`${API_BASE_URL}/auth/process-screenshot/`, {
      method: 'POST',
      headers: this.getHeaders(null),
      body: formData,
    });
    return this.handleResponse(response);
  }

  async getPendingDeposits() {
    const response = await fetch(`${API_BASE_URL}/auth/deposits/pending/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async approveDepositRequest(id) {
    const response = await fetch(`${API_BASE_URL}/auth/deposits/${id}/approve/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({}),
    });
    return this.handleResponse(response);
  }

  async rejectDepositRequest(id, note = '') {
    const response = await fetch(`${API_BASE_URL}/auth/deposits/${id}/reject/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ note }),
    });
    return this.handleResponse(response);
  }

  // Withdraws
  async initiateWithdraw({ amount, withdrawalMethod, withdrawalDetails }) {
    const response = await fetch(`${API_BASE_URL}/auth/withdraws/initiate/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        amount,
        withdrawal_method: withdrawalMethod,
        withdrawal_details: withdrawalDetails
      }),
    });
    return this.handleResponse(response);
  }

  async getMyWithdrawRequests() {
    const response = await fetch(`${API_BASE_URL}/auth/withdraws/mine/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  // Bank Details
  async getMyBankDetails() {
    const response = await fetch(`${API_BASE_URL}/auth/bank-details/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async addBankDetail(data) {
    const response = await fetch(`${API_BASE_URL}/auth/bank-details/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  async deleteBankDetail(id) {
    const response = await fetch(`${API_BASE_URL}/auth/bank-details/${id}/`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    if (!response.ok) return this.handleResponse(response);
    return { success: true };
  }

  async updateBankDetail(id, data) {
    const response = await fetch(`${API_BASE_URL}/auth/bank-details/${id}/`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  // Game
  async getCurrentRound() {
    const response = await fetch(`${API_BASE_URL}/game/round/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async placeBet(number, chipAmount) {
    try {
      const response = await fetch(`${API_BASE_URL}/game/bet/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ number, chip_amount: chipAmount }),
      });
      return this.handleResponse(response);
    } catch (err) {
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        throw new Error('Cannot connect to server. Please make sure the Django backend is running.');
      }
      throw err;
    }
  }

  async getMyBets() {
    const response = await fetch(`${API_BASE_URL}/game/bets/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async removeBet(number) {
    try {
      const response = await fetch(`${API_BASE_URL}/game/bet/${number}/`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      return this.handleResponse(response);
    } catch (err) {
      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        throw new Error('Cannot connect to server. Please make sure the Django backend is running.');
      }
      throw err;
    }
  }

  // Game Settings (public endpoint, no auth required)
  async getGameSettings() {
    const response = await fetch(`${API_BASE_URL}/game/settings/`, {
      headers: { 'Content-Type': 'application/json' },
    });
    return this.handleResponse(response);
  }
}

export default new ApiService();

