/**
 * ReuniteAI Client-Side In-Memory / LocalStorage Database
 * Provides 100% static, offline-ready REST API emulation for GitHub Pages.
 */

(function(window) {
  'use strict';

  const STORAGE_KEY = 'reunite_static_db_v1';

  class MockDB {
    constructor() {
      this.data = this.loadData();
    }

    loadData() {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          return JSON.parse(stored);
        }
      } catch (e) {
        console.warn('Failed to parse stored mock DB:', e);
      }

      // Initialize from pre-seeded data if available
      if (window.REUNITE_SEED_DATA) {
        this.saveData(window.REUNITE_SEED_DATA);
        return JSON.parse(JSON.stringify(window.REUNITE_SEED_DATA));
      }

      return {};
    }

    saveData(data) {
      this.data = data || this.data;
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data));
      } catch (e) {
        console.warn('LocalStorage quota or save error:', e);
      }
    }

    reset() {
      if (window.REUNITE_SEED_DATA) {
        this.saveData(window.REUNITE_SEED_DATA);
      } else {
        localStorage.removeItem(STORAGE_KEY);
        this.data = {};
      }
      return true;
    }

    getTable(tableName) {
      if (!this.data[tableName]) {
        this.data[tableName] = [];
      }
      return this.data[tableName];
    }

    insert(tableName, row) {
      const table = this.getTable(tableName);
      if (!row.id) {
        row.id = table.length > 0 ? Math.max(...table.map(r => r.id || 0)) + 1 : 1;
      }
      if (!row.created_at) {
        row.created_at = new Date().toISOString();
      }
      table.push(row);
      this.saveData();
      return row;
    }

    update(tableName, id, updates) {
      const table = this.getTable(tableName);
      const idx = table.findIndex(r => r.id == id);
      if (idx !== -1) {
        table[idx] = { ...table[idx], ...updates, updated_at: new Date().toISOString() };
        this.saveData();
        return table[idx];
      }
      return null;
    }

    find(tableName, predicate) {
      return this.getTable(tableName).filter(predicate);
    }

    findOne(tableName, predicate) {
      return this.getTable(tableName).find(predicate);
    }

    delete(tableName, id) {
      const table = this.getTable(tableName);
      const idx = table.findIndex(r => r.id == id);
      if (idx !== -1) {
        table.splice(idx, 1);
        this.saveData();
        return true;
      }
      return false;
    }

    /* --- Mock API Dispatcher --- */
    async handleRequest(method, endpoint, body = {}) {
      method = method.toUpperCase();
      const cleanEndpoint = endpoint.split('?')[0].replace(/\/+$/, '');
      const urlParams = new URLSearchParams(endpoint.includes('?') ? endpoint.split('?')[1] : '');

      // Helper for role names
      const rolesMap = {
        1: 'PARENT_GUARDIAN',
        2: 'VOLUNTEER',
        3: 'POLICE_OFFICER',
        4: 'MEDICAL_STAFF',
        5: 'HELP_CENTER_OPERATOR',
        6: 'EVENT_ADMIN',
        7: 'SUPER_ADMIN'
      };

      // ----------------------------------------------------------------------
      // 1. AUTH ROUTES
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/auth/login' && method === 'POST') {
        const { identifier, password } = body;
        const users = this.getTable('users');
        let user = users.find(u => (u.email && u.email.toLowerCase() === (identifier || '').toLowerCase()) || u.mobile === identifier);
        
        // If demo user wasn't found by exact email, allow convenient demo logins:
        if (!user) {
          const lowerId = (identifier || '').toLowerCase();
          if (lowerId.includes('admin')) user = users.find(u => u.role_id === 7 || u.role_id === 6);
          else if (lowerId.includes('volunteer')) user = users.find(u => u.role_id === 2);
          else if (lowerId.includes('police')) user = users.find(u => u.role_id === 3);
          else if (lowerId.includes('medical') || lowerId.includes('doctor')) user = users.find(u => u.role_id === 4);
          else if (lowerId.includes('help')) user = users.find(u => u.role_id === 5);
          else if (lowerId.includes('parent')) user = users.find(u => u.role_id === 1);
        }

        // If still not found, create a parent user dynamically
        if (!user) {
          user = this.insert('users', {
            uuid: 'usr-auto-' + Date.now(),
            full_name: identifier ? identifier.split('@')[0] : 'Demo User',
            email: identifier && identifier.includes('@') ? identifier : `${identifier || 'user'}@demo.com`,
            mobile: '9876543299',
            role_id: 1,
            status: 'ACTIVE',
            is_verified: 1,
            preferred_language: 'en'
          });
        }

        const roleName = rolesMap[user.role_id] || 'PARENT_GUARDIAN';
        const sessionToken = 'mock-jwt-session-' + user.id + '-' + Date.now();

        const userObj = {
          id: user.id,
          uuid: user.uuid,
          full_name: user.full_name,
          email: user.email,
          mobile: user.mobile,
          role: roleName,
          role_name: roleName,
          preferred_language: user.preferred_language || 'en',
          status: user.status || 'ACTIVE'
        };

        // Log audit
        this.insert('audit_logs', {
          user_id: user.id,
          action: 'USER_LOGIN',
          details: `User ${user.full_name} (${roleName}) logged in via static client`,
          ip_address: '127.0.0.1',
          user_agent: navigator.userAgent
        });

        const redirectPath = (window.Auth && window.Auth.getRoleDashboard) ? window.Auth.getRoleDashboard(roleName) : ('dashboard/' + (roleName === 'VOLUNTEER' ? 'volunteer.html' : (roleName === 'SUPER_ADMIN' ? 'admin.html' : 'parent.html')));

        return {
          success: true,
          message: 'Login successful (Static Client Mode)',
          token: sessionToken,
          user: userObj,
          data: {
            session_token: sessionToken,
            token: sessionToken,
            user: userObj,
            redirect_url: redirectPath
          }
        };
      }

      if (cleanEndpoint === '/api/auth/register' && method === 'POST') {
        const roleId = parseInt(body.role_id || 1, 10);
        const roleName = rolesMap[roleId] || 'PARENT_GUARDIAN';
        const newUser = this.insert('users', {
          uuid: 'usr-' + Date.now(),
          full_name: body.full_name || 'Registered Pilgrim',
          email: body.email,
          mobile: body.mobile || '9999999999',
          role_id: roleId,
          status: roleId > 1 ? 'PENDING' : 'ACTIVE', // Volunteers/officials pending admin approval
          is_verified: roleId === 1 ? 1 : 0,
          preferred_language: body.preferred_language || 'en'
        });

        return {
          success: true,
          message: roleId > 1 ? 'Registration submitted! Awaiting administrator approval.' : 'Account registered successfully!',
          data: {
            user_id: newUser.id,
            status: newUser.status
          }
        };
      }

      if (cleanEndpoint === '/api/auth/logout' && method === 'POST') {
        return { success: true, message: 'Logged out successfully.' };
      }

      if (cleanEndpoint === '/api/auth/forgot-password' && method === 'POST') {
        return { success: true, message: 'Password reset instructions simulated to your mobile/email.' };
      }

      // ----------------------------------------------------------------------
      // 2. ADMIN & AUDIT ROUTES
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/admin/users/pending' && method === 'GET') {
        const users = this.getTable('users').filter(u => u.status === 'PENDING').map(u => ({
          ...u,
          role_name: rolesMap[u.role_id] || 'USER'
        }));
        return { success: true, data: { users, total: users.length } };
      }

      if (cleanEndpoint === '/api/admin/users' && method === 'GET') {
        const statusFilter = urlParams.get('status');
        const roleFilter = urlParams.get('role');
        const search = (urlParams.get('search') || '').toLowerCase();

        let users = this.getTable('users').map(u => ({
          ...u,
          role_name: rolesMap[u.role_id] || 'USER'
        }));

        if (statusFilter) users = users.filter(u => u.status === statusFilter);
        if (roleFilter) users = users.filter(u => u.role_name === roleFilter);
        if (search) users = users.filter(u => (u.full_name || '').toLowerCase().includes(search) || (u.email || '').toLowerCase().includes(search) || (u.mobile || '').includes(search));

        return { success: true, data: { users, total: users.length } };
      }

      const userActionMatch = cleanEndpoint.match(/^\/api\/admin\/users\/(\d+)\/(approve|reject)$/);
      if (userActionMatch && method === 'POST') {
        const userId = parseInt(userActionMatch[1], 10);
        const action = userActionMatch[2];
        const newStatus = action === 'approve' ? 'ACTIVE' : 'REJECTED';
        this.update('users', userId, { status: newStatus, is_verified: action === 'approve' ? 1 : 0 });
        return { success: true, message: `User account has been ${action}d successfully.` };
      }

      if (cleanEndpoint === '/api/admin/audit-logs' && method === 'GET') {
        const logs = this.getTable('audit_logs').slice().reverse().map(l => {
          const user = this.findOne('users', u => u.id === l.user_id);
          return {
            ...l,
            user_name: user ? user.full_name : 'System'
          };
        });
        return { success: true, data: { logs: logs.slice(0, 100), total: logs.length } };
      }

      if (cleanEndpoint === '/api/users/profile') {
        if (method === 'GET') {
          const current = JSON.parse(localStorage.getItem('reunite_user') || '{}');
          const user = this.findOne('users', u => u.id === current.id) || current;
          return { success: true, data: { user } };
        }
        if (method === 'PUT') {
          const current = JSON.parse(localStorage.getItem('reunite_user') || '{}');
          if (current.id) {
            this.update('users', current.id, body);
            const updated = { ...current, ...body };
            localStorage.setItem('reunite_user', JSON.stringify(updated));
            return { success: true, message: 'Profile updated successfully!', data: { user: updated } };
          }
          return { success: true, message: 'Profile updated!' };
        }
      }

      // ----------------------------------------------------------------------
      // 3. FAMILIES & PERSONS
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/families') {
        if (method === 'GET') {
          const families = this.getTable('families');
          return { success: true, data: { families, total: families.length } };
        }
        if (method === 'POST') {
          const family = this.insert('families', {
            family_code: 'RY-FAM-2026-' + Math.floor(100000 + Math.random() * 900000),
            family_name: body.family_name || 'Pilgrim Family',
            primary_contact_name: body.primary_contact_name || 'Head of Family',
            primary_contact_phone: body.primary_contact_phone || '9876543210',
            home_city: body.home_city || 'Puri',
            home_state: body.home_state || 'Odisha'
          });
          return { success: true, message: 'Family created successfully!', data: family };
        }
      }

      const familyIdMatch = cleanEndpoint.match(/^\/api\/families\/(\d+)$/);
      if (familyIdMatch && method === 'GET') {
        const family = this.findOne('families', f => f.id == familyIdMatch[1]);
        const members = this.getTable('person_profiles').filter(p => p.family_id == familyIdMatch[1]);
        return { success: true, data: { family, members } };
      }

      if (cleanEndpoint === '/api/persons') {
        if (method === 'GET') {
          const persons = this.getTable('person_profiles').map(p => {
            const family = this.findOne('families', f => f.id == p.family_id);
            const safety = this.findOne('person_safety_profiles', s => s.person_id == p.id);
            return {
              ...p,
              family_name: family ? family.family_name : 'General',
              safety_id: safety ? safety.safety_id : ('RY-PER-2026-' + String(p.id).padStart(6, '0')),
              age_category: p.age < 12 ? 'CHILD' : (p.age < 18 ? 'MINOR' : (p.age >= 60 ? 'ELDERLY' : 'ADULT'))
            };
          });
          return { success: true, data: { persons, total: persons.length } };
        }
        if (method === 'POST') {
          const person = this.insert('person_profiles', {
            family_id: body.family_id || 1,
            first_name: body.first_name || 'Pilgrim',
            last_name: body.last_name || 'Member',
            gender: body.gender || 'MALE',
            age: parseInt(body.age || 25, 10),
            aadhaar_last4: body.aadhaar_last4 || '1234',
            photo_url: body.photo_url || '../assets/images/placeholder-person.png'
          });

          // Insert safety profile
          const safetyId = 'RY-PER-2026-' + String(person.id).padStart(6, '0');
          this.insert('person_safety_profiles', {
            person_id: person.id,
            safety_id: safetyId,
            rfid_wristband_code: 'RFID-' + Math.floor(1000 + Math.random() * 9000)
          });

          return { success: true, message: 'Person profile registered successfully!', data: { person, safety_id: safetyId } };
        }
      }

      const personIdMatch = cleanEndpoint.match(/^\/api\/persons\/(\d+)$/);
      if (personIdMatch) {
        const id = personIdMatch[1];
        if (method === 'GET') {
          const person = this.findOne('person_profiles', p => p.id == id);
          const clothing = this.findOne('clothing_profiles', c => c.person_id == id) || {};
          const safety = this.findOne('person_safety_profiles', s => s.person_id == id) || {};
          const contacts = this.getTable('emergency_contacts').filter(c => c.person_id == id);
          return { success: true, data: { person, clothing, safety, emergency_contacts: contacts } };
        }
        if (method === 'PUT') {
          const updated = this.update('person_profiles', id, body);
          return { success: true, message: 'Person updated successfully!', data: updated };
        }
      }

      // ----------------------------------------------------------------------
      // 4. LOST PERSON CASES
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/lost-person/cases') {
        if (method === 'GET') {
          const cases = this.getTable('lost_person_cases').map(c => {
            const loc = this.findOne('lost_person_locations', l => l.case_id == c.id) || {};
            const clo = this.findOne('lost_person_clothing', cl => cl.case_id == c.id) || {};
            return { ...c, location: loc, clothing: clo };
          });
          return { success: true, data: { cases, total: cases.length } };
        }
        if (method === 'POST') {
          const caseId = 'WS-LP-2026-' + Math.floor(10000 + Math.random() * 90000);
          const newCase = this.insert('lost_person_cases', {
            case_number: caseId,
            full_name: body.full_name || 'Missing Pilgrim',
            age: parseInt(body.age || 30, 10),
            gender: body.gender || 'MALE',
            status: 'OPEN',
            priority: body.priority || (parseInt(body.age || 30, 10) < 12 ? 'CRITICAL' : 'HIGH'),
            last_seen_time: body.last_seen_time || new Date().toISOString(),
            contact_number: body.contact_number || '9876543210'
          });

          this.insert('lost_person_locations', {
            case_id: newCase.id,
            landmark: body.last_seen_location || 'Grand Road, Puri',
            latitude: body.latitude || 19.8135,
            longitude: body.longitude || 85.8312
          });

          this.insert('lost_person_clothing', {
            case_id: newCase.id,
            upper_clothing: body.upper_clothing || 'White Kurta',
            lower_clothing: body.lower_clothing || 'Dhoti'
          });

          return { success: true, message: 'Missing person case reported successfully!', data: newCase };
        }
      }

      const lostCaseMatch = cleanEndpoint.match(/^\/api\/lost-person\/cases\/(\d+)$/);
      if (lostCaseMatch && method === 'GET') {
        const id = lostCaseMatch[1];
        const c = this.findOne('lost_person_cases', x => x.id == id);
        const loc = this.findOne('lost_person_locations', l => l.case_id == id) || {};
        const clo = this.findOne('lost_person_clothing', cl => cl.case_id == id) || {};
        const sightings = this.getTable('lost_person_sightings').filter(s => s.case_id == id);
        const notes = this.getTable('lost_person_notes').filter(n => n.case_id == id);
        return { success: true, data: { case: c, location: loc, clothing: clo, sightings, notes } };
      }

      const sightingMatch = cleanEndpoint.match(/^\/api\/lost-person\/cases\/(\d+)\/sightings$/);
      if (sightingMatch && method === 'POST') {
        const sighting = this.insert('lost_person_sightings', {
          case_id: sightingMatch[1],
          sighting_time: new Date().toISOString(),
          location_description: body.location_description || 'Near Gundicha Temple',
          reported_by: body.reported_by || 'Volunteer Desk',
          details: body.details || 'Spotted near medical camp 3'
        });
        return { success: true, message: 'Sighting logged successfully!', data: sighting };
      }

      // ----------------------------------------------------------------------
      // 5. FOUND PERSON CASES
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/found-person/cases') {
        if (method === 'GET') {
          const cases = this.getTable('found_person_cases').map(c => {
            const loc = this.findOne('found_person_locations', l => l.case_id == c.id) || {};
            const clues = this.getTable('found_person_identification_clues').filter(cl => cl.case_id == c.id);
            return { ...c, location: loc, clues };
          });
          return { success: true, data: { cases, total: cases.length } };
        }
        if (method === 'POST') {
          const foundCode = 'WS-FP-2026-' + Math.floor(10000 + Math.random() * 90000);
          const newCase = this.insert('found_person_cases', {
            case_number: foundCode,
            temporary_name: body.temporary_name || 'Found Child / Elderly',
            estimated_age: body.estimated_age || 10,
            gender: body.gender || 'FEMALE',
            status: 'IN_CUSTODY',
            safe_custody_location: body.safe_custody_location || 'Help Center Kiosk 4, Badadanda'
          });
          return { success: true, message: 'Found person registered successfully!', data: newCase };
        }
      }

      const foundCaseMatch = cleanEndpoint.match(/^\/api\/found-person\/cases\/(\d+)$/);
      if (foundCaseMatch && method === 'GET') {
        const id = foundCaseMatch[1];
        const c = this.findOne('found_person_cases', x => x.id == id);
        const loc = this.findOne('found_person_locations', l => l.case_id == id) || {};
        const clues = this.getTable('found_person_identification_clues').filter(cl => cl.case_id == id);
        return { success: true, data: { case: c, location: loc, clues } };
      }

      // ----------------------------------------------------------------------
      // 6. LOST & FOUND ITEMS
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/lost-items') {
        if (method === 'GET') {
          const items = this.getTable('lost_item_cases');
          return { success: true, data: { items, total: items.length } };
        }
        if (method === 'POST') {
          const newItem = this.insert('lost_item_cases', {
            case_number: 'WS-LI-2026-' + Math.floor(10000 + Math.random() * 90000),
            item_name: body.item_name || 'Lost Wallet / Phone',
            category: body.category || 'ELECTRONICS',
            description: body.description || 'Lost near temple gate',
            status: 'SEARCHING'
          });
          return { success: true, message: 'Lost item reported successfully!', data: newItem };
        }
      }

      if (cleanEndpoint === '/api/found-items') {
        if (method === 'GET') {
          const items = this.getTable('found_item_cases');
          return { success: true, data: { items, total: items.length } };
        }
        if (method === 'POST') {
          const newItem = this.insert('found_item_cases', {
            case_number: 'WS-FI-2026-' + Math.floor(10000 + Math.random() * 90000),
            item_name: body.item_name || 'Found Item',
            category: body.category || 'WALLET_PURSE',
            description: body.description || 'Secured in Locker Room A',
            storage_locker: 'Locker #14B',
            status: 'IN_STORAGE'
          });
          return { success: true, message: 'Found item registered in storage!', data: newItem };
        }
      }

      // ----------------------------------------------------------------------
      // 7. AI MATCHING & DASHBOARD
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/ai/matches/person' || cleanEndpoint === '/api/ai/match/person') {
        const matches = this.getTable('ai_match_results').map(m => ({
          ...m,
          match_score_pct: Math.round((m.similarity_score || 0.89) * 100),
          confidence_tier: (m.similarity_score || 0.89) > 0.85 ? 'HIGH' : 'MEDIUM',
          explainability_points: [
            'Biometric facial landmark alignment: 91% similarity',
            'Estimated age match: within 2 years tolerance',
            'Clothing color match: Saffron Kurta with Red Border',
            'Proximity distance: 350 meters from reported lost location'
          ]
        }));
        return { success: true, data: { matches, total: matches.length } };
      }

      if (cleanEndpoint === '/api/ai/dashboard/stats' || cleanEndpoint === '/api/ai/matches/stats') {
        return {
          success: true,
          data: {
            pipeline_a_active: true,
            pipeline_b_active: true,
            total_matches_generated: 48,
            high_confidence_matches: 34,
            human_verified_reunions: 29,
            model_precision: '96.4%',
            model_recall: '94.2%',
            f1_score: '95.3%',
            average_reunite_time_mins: 24
          }
        };
      }

      // ----------------------------------------------------------------------
      // 8. MEDICAL EMERGENCY ASSISTANCE
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/medical/cases') {
        if (method === 'GET') {
          const cases = this.getTable('medical_cases').map(m => {
            const loc = this.findOne('medical_case_locations', l => l.case_id == m.id) || {};
            return { ...m, location: loc };
          });
          return { success: true, data: { cases, total: cases.length } };
        }
        if (method === 'POST') {
          const medCase = this.insert('medical_cases', {
            case_number: 'WS-MED-2026-' + Math.floor(10000 + Math.random() * 90000),
            patient_name: body.patient_name || 'Pilgrim (Dehydration)',
            priority: body.priority || 'HIGH',
            status: 'DISPATCHED',
            chief_complaint: body.chief_complaint || 'Heat exhaustion, faintness',
            camp_name: body.camp_name || 'Medical Camp 2 - Bada Danda'
          });
          return { success: true, message: 'Medical emergency logged! First responders dispatched.', data: medCase };
        }
      }

      if (cleanEndpoint === '/api/medical/camps' || cleanEndpoint === '/api/medical/facilities') {
        const camps = this.getTable('medical_facilities');
        return { success: true, data: { facilities: camps, total: camps.length } };
      }

      if (cleanEndpoint === '/api/medical/ambulances') {
        const amb = this.getTable('ambulances');
        return { success: true, data: { ambulances: amb, total: amb.length } };
      }

      // ----------------------------------------------------------------------
      // 9. VOLUNTEERS & TASKS
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/volunteers') {
        if (method === 'GET') {
          const vols = this.getTable('volunteers');
          return { success: true, data: { volunteers: vols, total: vols.length } };
        }
        if (method === 'POST') {
          const vol = this.insert('volunteers', {
            volunteer_code: 'WS-VOL-2026-' + Math.floor(10000 + Math.random() * 90000),
            full_name: body.full_name || 'Volunteer',
            mobile: body.mobile || '9876543210',
            duty_status: 'ON_DUTY',
            assigned_sector: body.sector || 'Grand Road - Sector 3'
          });
          return { success: true, message: 'Volunteer registered successfully!', data: vol };
        }
      }

      if (cleanEndpoint === '/api/volunteers/me') {
        const user = JSON.parse(localStorage.getItem('reunite_user') || '{}');
        const vol = this.findOne('volunteers', v => v.user_id == user.id) || {
          id: 1,
          full_name: user.full_name || 'Amitabh Mohanty',
          volunteer_code: 'WS-VOL-2026-001006',
          duty_status: 'ON_DUTY',
          assigned_sector: 'Bada Danda / Grand Road Sector 2',
          shift_start: '08:00 AM',
          shift_end: '04:00 PM',
          tasks_completed: 12
        };
        return { success: true, data: vol };
      }

      if (cleanEndpoint === '/api/volunteers/shift' && method === 'POST') {
        const status = body.status || 'ON_DUTY';
        return { success: true, message: `Shift status updated to ${status}. Attendance marked.`, duty_status: status };
      }

      if (cleanEndpoint === '/api/volunteer-tasks') {
        if (method === 'GET') {
          const tasks = this.getTable('volunteer_tasks');
          return { success: true, data: { tasks, total: tasks.length } };
        }
      }

      const taskActionMatch = cleanEndpoint.match(/^\/api\/volunteer-tasks\/(\d+)\/(accept|complete)$/);
      if (taskActionMatch && method === 'POST') {
        const taskId = taskActionMatch[1];
        const action = taskActionMatch[2];
        const newStatus = action === 'accept' ? 'IN_PROGRESS' : 'COMPLETED';
        this.update('volunteer_tasks', taskId, { status: newStatus });
        return { success: true, message: `Task marked as ${newStatus}!` };
      }

      const recMatch = cleanEndpoint.match(/^\/api\/volunteer-tasks\/(\d+)\/recommendations$/);
      if (recMatch && method === 'GET') {
        const recs = this.getTable('volunteer_recommendations').slice(0, 5).map((r, i) => ({
          ...r,
          volunteer_name: `Volunteer ${i + 1} (${['Odia + Hindi', 'First Aid Certified', 'Crowd Control Specialist'][i % 3]})`,
          score: Math.round(85 + (5 - i) * 2.8)
        }));
        return { success: true, data: { recommendations: recs } };
      }

      // ----------------------------------------------------------------------
      // 10. DINDI & WARI MOVEMENT ROUTES
      // ----------------------------------------------------------------------
      if (cleanEndpoint === '/api/dindis') {
        const dindis = this.getTable('dindis');
        return { success: true, data: { dindis, total: dindis.length } };
      }

      const dindiMatch = cleanEndpoint.match(/^\/api\/dindis\/(\d+)$/);
      if (dindiMatch && method === 'GET') {
        const id = dindiMatch[1];
        const d = this.findOne('dindis', x => x.id == id);
        const sched = this.getTable('dindi_schedules').filter(s => s.dindi_id == id);
        const ann = this.getTable('dindi_announcements').filter(a => a.dindi_id == id);
        return { success: true, data: { dindi: d, schedules: sched, announcements: ann } };
      }

      if (cleanEndpoint === '/api/routes' || cleanEndpoint === '/api/routes/sections') {
        const sections = this.getTable('route_sections');
        return { success: true, data: { sections, total: sections.length } };
      }

      if (cleanEndpoint === '/api/routes/crowd-zones') {
        const zones = this.getTable('crowd_zones');
        return { success: true, data: { zones, total: zones.length } };
      }

      if (cleanEndpoint === '/api/locations/nearby') {
        const locs = this.getTable('wari_locations');
        return { success: true, data: { locations: locs, total: locs.length } };
      }

      // Default Fallback
      console.warn(`[StaticMockDB] Unhandled endpoint: ${method} ${cleanEndpoint}. Returning generic success.`);
      return {
        success: true,
        message: 'Request handled in static client mode',
        data: {}
      };
    }
  }

  // Export globally
  window.StaticMockDB = new MockDB();

})(window);
