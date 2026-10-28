/**
 * ReuniteAI API Client Module
 * REST API client with automatic Static Mock Fallback for GitHub Pages and offline testing.
 */

// Auto-load Mock Data & Mock DB synchronously via base path detection
(function() {
  try {
    const currentScript = document.currentScript;
    if (currentScript && currentScript.src) {
      const basePath = currentScript.src.replace(/assets\/js\/api\.js(\?.*)?$/, '');
      if (!window.REUNITE_SEED_DATA) {
        document.write('<script src="' + basePath + 'assets/js/mock-data.js"><\/script>');
      }
      if (!window.StaticMockDB) {
        document.write('<script src="' + basePath + 'assets/js/mock-db.js"><\/script>');
      }
    }
  } catch (e) {
    console.warn('Auto script injection error:', e);
  }
})();

// Universal App Path Resolver for GitHub Pages subpaths and custom domains
window.getAppPath = function(path) {
  if (!path) return '';
  const cleanPath = path.startsWith('/') ? path : '/' + path;

  // If on GitHub Pages, prepend the repository subpath (e.g. /reuniteai)
  if (window.location.hostname.endsWith('github.io')) {
    const parts = window.location.pathname.split('/').filter(Boolean);
    if (parts.length > 0) {
      const repoName = parts[0];
      if (!cleanPath.startsWith('/' + repoName)) {
        return '/' + repoName + cleanPath;
      }
    }
  }

  return cleanPath;
};

const API_BASE_URL = window.location.origin;

class APIClient {
  static isStaticMode() {
    return (
      window.location.protocol === 'file:' ||
      window.location.hostname.endsWith('github.io') ||
      window.REUNITE_FORCE_STATIC === true
    );
  }

  static getHeaders(extraHeaders = {}) {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...extraHeaders
    };

    const token = localStorage.getItem('reunite_session_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      headers['X-Session-Token'] = token;
    }

    return headers;
  }

  static async request(endpoint, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    let body = options.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch(e) {}
    }

    // 1. If running statically on GitHub Pages or file:// protocol, use MockDB immediately
    if (this.isStaticMode()) {
      if (window.StaticMockDB) {
        return await window.StaticMockDB.handleRequest(method, endpoint, body);
      }
    }

    // 2. Otherwise attempt standard REST API call with server
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    
    const config = {
      method: method,
      headers: this.getHeaders(options.headers),
      ...options
    };

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => null);

      if (response.ok && data) {
        return data;
      }

      // If server returned 404 or 500, fallback to MockDB for seamless experience
      if (window.StaticMockDB) {
        console.warn(`Server returned ${response.status} for ${endpoint}. Falling back to StaticMockDB.`);
        return await window.StaticMockDB.handleRequest(method, endpoint, body);
      }

      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        localStorage.removeItem('reunite_session_token');
        localStorage.removeItem('reunite_user');
        if (!window.location.pathname.includes('login.html')) {
          window.location.href = window.getAppPath('/login.html?expired=1');
        }
      }

      return {
        success: false,
        status: response.status,
        message: data?.message || `HTTP Error ${response.status}`
      };
    } catch (error) {
      // Network failure (server not running or offline) -> Seamlessly route to StaticMockDB!
      if (window.StaticMockDB) {
        console.info(`[ReuniteAI] Running in offline/static mode: ${method} ${endpoint}`);
        return await window.StaticMockDB.handleRequest(method, endpoint, body);
      }

      return {
        success: false,
        status: 0,
        message: 'Network connection failed.',
        error_code: 'NETWORK_ERROR'
      };
    }
  }

  static get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  static post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body });
  }

  static put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body });
  }

  static delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

window.APIClient = APIClient;
