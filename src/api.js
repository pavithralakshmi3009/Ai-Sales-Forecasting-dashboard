// ==========================================
// Centralized API Client — JWT Authentication
// ==========================================

const API_BASE = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '/api';

// ----------------------------------------
// Token Management
// ----------------------------------------
function getAuthToken() {
  return localStorage.getItem('auth_token');
}

function setAuthToken(token) {
  localStorage.setItem('auth_token', token);
}

function removeAuthToken() {
  localStorage.removeItem('auth_token');
}

// ----------------------------------------
// Core Request Helper
// ----------------------------------------
async function request(url, options = {}) {
  const token = getAuthToken();

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Add Authorization header if token exists
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (file uploads)
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const targetUrl = `${API_BASE}${url}`;
  console.log(`[API Request] ${config.method || 'GET'} -> ${targetUrl}`);
  const response = await fetch(targetUrl, config);
  return response;
}

// ----------------------------------------
// Auth
// ----------------------------------------
export async function login(username, password) {
  try {
    const res = await request('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    let data;
    try {
      data = await res.json();
    } catch {
      data = { message: `Backend returned invalid response format (HTTP ${res.status})` };
    }

    console.log(`[API Response] /login HTTP ${res.status}:`, data);

    // Store token on successful login
    if (res.ok && (data.token || data.success)) {
      if (data.token) {
        setAuthToken(data.token);
      }
    }

    return { ok: res.ok, data };
  } catch (err) {
    console.error(`[API Network Error] Could not connect to backend at ${API_BASE}:`, err);
    throw err;
  }
}

export async function logout() {
  const res = await request('/logout', { method: 'POST' });
  const data = await res.json();

  // Always remove the token on logout
  removeAuthToken();

  return { ok: res.ok, data };
}

export async function checkAuthStatus() {
  const token = getAuthToken();
  if (!token) {
    return { ok: true, data: { logged_in: false } };
  }

  try {
    const res = await request('/auth/status');
    const data = await res.json();

    // If token is invalid, clean it up
    if (!data.logged_in) {
      removeAuthToken();
    }

    return { ok: res.ok, data };
  } catch {
    removeAuthToken();
    return { ok: true, data: { logged_in: false } };
  }
}

// ----------------------------------------
// Sales CRUD
// ----------------------------------------
export async function getSales(limit = null) {
  const url = limit ? `/sales?limit=${limit}` : '/sales';
  const res = await request(url);
  return { ok: res.ok, data: await res.json() };
}

export async function addSale(saleData) {
  const res = await request('/sales', {
    method: 'POST',
    body: JSON.stringify(saleData),
  });
  return { ok: res.ok, data: await res.json() };
}

export async function updateSale(id, saleData) {
  const res = await request(`/sales/${id}`, {
    method: 'PUT',
    body: JSON.stringify(saleData),
  });
  return { ok: res.ok, data: await res.json() };
}

export async function deleteSale(id) {
  const res = await request(`/sales/${id}`, { method: 'DELETE' });
  return { ok: res.ok, data: await res.json() };
}

export async function searchSales(product) {
  const res = await request(`/sales/search?product=${encodeURIComponent(product)}`);
  return { ok: res.ok, data: await res.json() };
}

// ----------------------------------------
// Dashboard Stats
// ----------------------------------------
export async function getStats() {
  const res = await request('/stats');
  return { ok: res.ok, data: await res.json() };
}

// ----------------------------------------
// Dataset
// ----------------------------------------
export async function getDataset() {
  const res = await request('/dataset');
  return { ok: res.ok, data: await res.json() };
}

// ----------------------------------------
// AI Prediction
// ----------------------------------------
export async function predictSales(month) {
  const res = await request('/predict', {
    method: 'POST',
    body: JSON.stringify({ month: parseInt(month) }),
  });
  return { ok: res.ok, data: await res.json() };
}

export async function predictTransaction(transactionData) {
  const res = await request('/predict/transaction', {
    method: 'POST',
    body: JSON.stringify(transactionData),
  });
  return { ok: res.ok, data: await res.json() };
}

// ----------------------------------------
// CSV Upload
// ----------------------------------------
export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await request('/upload-csv', {
    method: 'POST',
    body: formData,
  });
  return { ok: res.ok, data: await res.json() };
}

// ----------------------------------------
// Exports (authenticated downloads)
// ----------------------------------------
export async function downloadExcel() {
  const res = await request('/export/excel');
  if (!res.ok) {
    const data = await res.json();
    return { ok: false, data };
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'Sales_Report.xlsx';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  return { ok: true };
}

export async function downloadPDF() {
  const res = await request('/export/pdf');
  if (!res.ok) {
    const data = await res.json();
    return { ok: false, data };
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'Sales_Report.pdf';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  return { ok: true };
}
