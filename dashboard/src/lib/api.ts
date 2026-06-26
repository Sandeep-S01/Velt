const trimTrailingSlash = (url: string) => url.replace(/\/+$/, '');

const configuredApiUrl = import.meta.env.VITE_API_URL;
const developmentApiUrl = 'http://localhost:8000/api/v1';
const productionApiUrl = '/api/v1';

export const API_BASE_URL = trimTrailingSlash(
  configuredApiUrl || (import.meta.env.DEV ? developmentApiUrl : productionApiUrl)
);

export const getApiBaseUrl = () => {
  const url = API_BASE_URL;
  if (url.endsWith('/api/v1')) {
    return url.slice(0, -7);
  }
  return url;
};

export const getApiDocsUrl = () => `${API_BASE_URL}/docs`;

export const WIDGET_SCRIPT_URL = trimTrailingSlash(
  import.meta.env.VITE_WIDGET_URL || (import.meta.env.DEV ? 'http://localhost:8000/widget.js' : '/widget.js')
);


export interface APIError {
  detail: string;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('token');
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'An error occurred';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      errorDetail = response.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { method: 'GET', ...options }),

  post: <T>(endpoint: string, body?: any, options?: RequestInit) => {
    const isFormData = body instanceof FormData;
    const headers = new Headers(options?.headers || {});
    
    if (!isFormData && body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    return request<T>(endpoint, {
      method: 'POST',
      body: isFormData ? body : JSON.stringify(body),
      ...options,
      headers,
    });
  },

  put: <T>(endpoint: string, body?: any, options?: RequestInit) => {
    const headers = new Headers(options?.headers || {});
    if (body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    return request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
      ...options,
      headers,
    });
  },

  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { method: 'DELETE', ...options }),
};
