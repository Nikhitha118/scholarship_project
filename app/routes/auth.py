from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.utils.security import enable_2fa, validate_2fa, generate_totp_secret

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Check if 2FA is enabled
            if user.two_factor_enabled:
                session['pending_user_id'] = user.id
                return redirect(url_for('auth.verify_2fa'))
            
            login_user(user, remember=remember)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['pending_user_id'])
    
    if request.method == 'POST':
        token = request.form['token']
        is_valid, error = validate_2fa(user, token)
        
        if is_valid:
            login_user(user)
            session.pop('pending_user_id', None)
            flash('2FA verified! Logged in successfully.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(error, 'error')
    
    return render_template('auth/2fa_verify.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if request.method == 'POST':
        if 'enable' in request.form:
            qr_code, error = enable_2fa(current_user.id)
            if error:
                flash(error, 'error')
            else:
                session['qr_code'] = qr_code
                return redirect(url_for('auth.confirm_2fa'))
        elif 'disable' in request.form:
            current_user.two_factor_enabled = False
            current_user.totp_secret = None
            db.session.commit()
            flash('2FA disabled successfully', 'success')
    
    return render_template('dashboard/2fa_setup.html')

@auth_bp.route('/confirm-2fa', methods=['GET', 'POST'])
@login_required
def confirm_2fa():
    qr_code = session.get('qr_code')
    
    if request.method == 'POST':
        token = request.form['token']
        is_valid, error = validate_2fa(current_user, token)
        
        if is_valid:
            current_user.two_factor_enabled = True
            db.session.commit()
            flash('2FA enabled successfully!', 'success')
            session.pop('qr_code', None)
            return redirect(url_for('dashboard.profile'))
        else:
            flash('Invalid code. Please try again.', 'error')
    
    return render_template('auth/confirm_2fa.html', qr_code=qr_code)