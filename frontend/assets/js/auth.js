/**
 * ReuniteAI Auth Manager
 * Manages user sessions, authentication guards, and role-based redirects with GitHub Pages compatibility.
 */

class Auth {
  static getToken() {
    return localStorage.getItem('reunite_session_token');
  }

  static getCurrentUser() {
    const raw = localStorage.getItem('reunite_user');
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  static setSession(token, user) {
    localStorage.setItem('reunite_session_token', token);
    localStorage.setItem('reunite_user', JSON.stringify(user));
  }

  static clearSession() {
    localStorage.removeItem('reunite_session_token');
    localStorage.removeItem('reunite_user');
  }

  static getRoleDashboard(roleName) {
    const map = {
      'PARENT_GUARDIAN': '/dashboard/parent.html',
      'VOLUNTEER': '/dashboard/volunteer.html',
      'POLICE_OFFICER': '/dashboard/police.html',
      'MEDICAL_STAFF': '/dashboard/medical.html',
      'HELP_CENTER_OPERATOR': '/dashboard/help-center.html',
      'EVENT_ADMIN': '/admin/dashboard.html',
      'SUPER_ADMIN': '/admin/dashboard.html'
    };
    const target = map[roleName] || '/dashboard/parent.html';
    return (window.getAppPath ? window.getAppPath(target) : target);
  }

  static async logout() {
    try {
      if (window.APIClient) {
        await APIClient.post('/api/auth/logout', {});
      }
    } catch (e) {
      console.warn('Logout API error:', e);
    } finally {
      this.clearSession();
      const loginUrl = window.getAppPath ? window.getAppPath('/login.html?logout=1') : '/login.html?logout=1';
      window.location.href = loginUrl;
    }
  }

  static requireAuth(allowedRoles = []) {
    const user = this.getCurrentUser();
    const token = this.getToken();

    if (!user || !token) {
      const loginUrl = window.getAppPath ? window.getAppPath('/login.html?auth=required') : '/login.html?auth=required';
      window.location.href = loginUrl;
      return false;
    }

    if (allowedRoles.length > 0) {
      if (!allowedRoles.includes(user.role) && user.role !== 'SUPER_ADMIN') {
        alert(`Access Denied: Your role (${user.role}) is not authorized to view this page.`);
        window.location.href = this.getRoleDashboard(user.role);
        return false;
      }
    }

    // Populate Top Navbar User Details
    document.addEventListener('DOMContentLoaded', () => {
      const nameElem = document.getElementById('navUserName');
      const roleElem = document.getElementById('navUserRole');
      const avatarElem = document.getElementById('navUserAvatar');

      if (nameElem) nameElem.innerText = user.full_name;
      if (roleElem) roleElem.innerText = (user.role || '').replace(/_/g, ' ');
      if (avatarElem && user.full_name) {
        const initials = user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        avatarElem.innerText = initials;
      }
    });

    return true;
  }

  /**
   * 1-Click Instant Demo Login Helper
   */
  static async loginAsDemo(role = 'VOLUNTEER') {
    const emailMap = {
      'SUPER_ADMIN': 'admin@demo.com',
      'VOLUNTEER': 'volunteer@demo.com',
      'PARENT_GUARDIAN': 'parent@demo.com',
      'POLICE_OFFICER': 'police@demo.com',
      'MEDICAL_STAFF': 'medical@demo.com',
      'HELP_CENTER_OPERATOR': 'helpcenter@demo.com'
    };

    const email = emailMap[role] || 'volunteer@demo.com';
    const res = await APIClient.post('/api/auth/login', {
      identifier: email,
      password: 'DemoPassword123'
    });

    if (res.success && res.token && res.user) {
      this.setSession(res.token, res.user);
      window.location.href = this.getRoleDashboard(res.user.role);
      return true;
    }
    return false;
  }

  static showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 400);
    }, 3500);
  }
}

window.Auth = Auth;
