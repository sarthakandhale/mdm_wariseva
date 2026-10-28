import re

INDIAN_MOBILE_REGEX = r'^[6-9]\d{9}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_full_name(name):
    if not name or len(name.strip()) < 2:
        return False, "Full Name is required and must be at least 2 characters long."
    return True, None

def validate_mobile(mobile):
    if not mobile:
        return False, "Mobile number is required."
    clean_mobile = mobile.strip().replace(" ", "").replace("-", "")
    if clean_mobile.startswith("+91"):
        clean_mobile = clean_mobile[3:]
    elif clean_mobile.startswith("0"):
        clean_mobile = clean_mobile[1:]
    
    if not re.match(INDIAN_MOBILE_REGEX, clean_mobile):
        return False, "Invalid Indian mobile number. Must be a 10-digit number starting with 6, 7, 8, or 9."
    return True, clean_mobile

def validate_email(email):
    if not email or not email.strip():
        return True, None  # Email is optional
    email_clean = email.strip().lower()
    if not re.match(EMAIL_REGEX, email_clean):
        return False, "Invalid email format."
    return True, email_clean

def validate_password(password):
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>\/?]', password):
        return False, "Password must contain at least one special character."
    return True, None


def validate_registration_payload(data):
    errors = []
    
    # Name
    valid_name, name_err = validate_full_name(data.get('full_name'))
    if not valid_name:
        errors.append(name_err)
        
    # Mobile
    valid_mob, mob_res = validate_mobile(data.get('mobile'))
    if not valid_mob:
        errors.append(mob_res)
    clean_mobile = mob_res if valid_mob else None

    # Email
    valid_email, email_res = validate_email(data.get('email'))
    if not valid_email:
        errors.append(email_res)
    clean_email = email_res if valid_email else None

    # Password
    valid_pass, pass_err = validate_password(data.get('password'))
    if not valid_pass:
        errors.append(pass_err)
        
    # Confirm Password
    if data.get('password') != data.get('confirm_password'):
        errors.append("Password and Confirm Password do not match.")

    # Role
    role_name = data.get('role', 'PARENT_GUARDIAN')
    allowed_public_roles = ['PARENT_GUARDIAN', 'VOLUNTEER', 'POLICE_OFFICER', 'MEDICAL_STAFF', 'HELP_CENTER_OPERATOR', 'EVENT_ADMIN']
    if role_name == 'SUPER_ADMIN' or role_name not in allowed_public_roles:
        errors.append("Invalid role specified for self-registration. SUPER_ADMIN accounts cannot be registered publicly.")

    return len(errors) == 0, errors, {
        'full_name': data.get('full_name', '').strip() if data.get('full_name') else '',
        'mobile': clean_mobile,
        'email': clean_email,
        'role_name': role_name,
        'preferred_language': data.get('preferred_language', 'en')
    }
