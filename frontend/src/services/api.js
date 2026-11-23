/**
 * Centralized API client for Financial Filing Auditor backend.
 * Automatically injects the JWT token from localStorage.
 */
const API_BASE_URL = 'http://localhost:8000/api'

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let errorDetail = 'API request failed'
    try {
      const err = await response.json()
      errorDetail = err.detail || JSON.stringify(err)
    } catch {
      errorDetail = response.statusText
    }
    throw new Error(errorDetail)
  }

  return response.json()
}

export const api = {
  auth: {
    login: (email, password) =>
      request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    register: (email, password, full_name, role = 'auditor') =>
      request('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password, full_name, role }),
      }),
    me: () => request('/auth/me'),
  },
  audit: {
    create: (ticker, year, filing_type = '10-K') =>
      request('/audit/create', {
        method: 'POST',
        body: JSON.stringify({ ticker, year: parseInt(year, 10), filing_type }),
      }),
    get: (id) => request(`/audit/${id}`),
    getSample: () => request('/audit/sample'),
    submitReview: (id, payload) =>
      request(`/audit/${id}/review`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    history: () => request('/audit/history'),
  },
}
