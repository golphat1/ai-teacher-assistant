const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const TOKEN_STORAGE_KEY = 'ata_access_token';

export class ApiError extends Error {
  constructor(message, { status, details } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

export function getAccessToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setAccessToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearAccessToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

// Turns FastAPI's 422 validation error shape into one readable string.
function formatValidationDetail(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((err) => {
        const field = Array.isArray(err.loc) ? err.loc[err.loc.length - 1] : 'field';
        return `${field}: ${err.msg}`;
      })
      .join('; ');
  }
  return typeof detail === 'string' ? detail : 'Request failed.';
}

export async function apiRequest(path, { method = 'GET', body, headers = {} } = {}) {
  const token = getAccessToken();

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    throw new ApiError('Could not reach the server. Check your connection and try again.', {
      status: 0,
    });
  }

  let data = null;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    data = await response.json().catch(() => null);
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearAccessToken();
      throw new ApiError('Your session has expired. Please log in again.', { status: 401 });
    }
    if (response.status === 403) {
      throw new ApiError('You do not have permission to do that.', { status: 403 });
    }
    if (response.status === 422) {
      throw new ApiError(formatValidationDetail(data?.detail), { status: 422, details: data?.detail });
    }
    throw new ApiError(data?.detail || `Request failed with status ${response.status}.`, {
      status: response.status,
    });
  }

  return data;
}