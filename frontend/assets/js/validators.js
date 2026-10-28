/**
 * ReuniteAI Client-Side Form Validation Utilities
 */

const Validators = {
  INDIAN_MOBILE_REGEX: /^[6-9]\d{9}$/,
  EMAIL_REGEX: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,

  validateName(name) {
    if (!name || name.trim().length < 2) {
      return { valid: false, message: 'Full Name is required and must be at least 2 characters.' };
    }
    return { valid: true };
  },

  validateMobile(mobile) {
    if (!mobile) {
      return { valid: false, message: 'Mobile number is required.' };
    }
    const clean = mobile.trim().replace(/\s+|-/g, '');
    let formatted = clean;
    if (clean.startsWith('+91')) formatted = clean.substring(3);
    else if (clean.startsWith('0')) formatted = clean.substring(1);

    if (!this.INDIAN_MOBILE_REGEX.test(formatted)) {
      return { valid: false, message: 'Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.' };
    }
    return { valid: true, clean: formatted };
  },

  validateEmail(email) {
    if (!email || !email.trim()) {
      return { valid: true }; // Email is optional
    }
    if (!this.EMAIL_REGEX.test(email.trim())) {
      return { valid: false, message: 'Please enter a valid email address.' };
    }
    return { valid: true };
  },

  validatePassword(password) {
    if (!password || password.length < 8) {
      return { valid: false, message: 'Password must be at least 8 characters long.' };
    }
    if (!/[A-Z]/.test(password)) {
      return { valid: false, message: 'Password must contain at least one uppercase letter (A-Z).' };
    }
    if (!/[a-z]/.test(password)) {
      return { valid: false, message: 'Password must contain at least one lowercase letter (a-z).' };
    }
    if (!/\d/.test(password)) {
      return { valid: false, message: 'Password must contain at least one number (0-9).' };
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};:'"\\|,.<>\/?]/.test(password)) {
      return { valid: false, message: 'Password must contain at least one special character (!@#$%^&*).' };
    }
    return { valid: true };
  },


  validateConfirmPassword(password, confirmPassword) {
    if (password !== confirmPassword) {
      return { valid: false, message: 'Confirm Password does not match Password.' };
    }
    return { valid: true };
  },

  showFieldError(inputElem, message) {
    const group = inputElem.closest('.form-group');
    if (!group) return;
    group.classList.add('has-error');
    let feedback = group.querySelector('.invalid-feedback');
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.className = 'invalid-feedback';
      group.appendChild(feedback);
    }
    feedback.innerText = message;
  },

  clearFieldError(inputElem) {
    const group = inputElem.closest('.form-group');
    if (!group) return;
    group.classList.remove('has-error');
    const feedback = group.querySelector('.invalid-feedback');
    if (feedback) feedback.innerText = '';
  }
};
