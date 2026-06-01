import pyotp
import qrcode
import io
import base64
from app import db
from app.models.user import User

def generate_totp_secret():
    """Generate a new TOTP secret"""
    return pyotp.random_base32()

def generate_qr_code(user_email, totp_secret):
    """Generate QR code for 2FA setup"""
    provisioning_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name=user_email,
        issuer_name="Life Pilot AI"
    )
    
    img = qrcode.make(provisioning_uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def verify_totp(totp_secret, token):
    """Verify TOTP token"""
    totp = pyotp.TOTP(totp_secret)
    return totp.verify(token, valid_window=1)

def enable_2fa(user_id):
    """Enable 2FA for a user"""
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    
    totp_secret = generate_totp_secret()
    user.totp_secret = totp_secret
    db.session.commit()
    
    qr_code = generate_qr_code(user.email, totp_secret)
    return qr_code, None

def validate_2fa(user, token):
    """Validate 2FA token"""
    if not user.two_factor_enabled:
        return True, None
    
    if not user.totp_secret:
        return True, None
    
    if verify_totp(user.totp_secret, token):
        return True, None
    else:
        return False, "Invalid 2FA code"