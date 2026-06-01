from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.scholarship import Scholarship
from app.models.application import Application
from app.services.ai_agent import AIAgent

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    ai_agent = AIAgent()
    
    # Get user's applications
    applications = Application.query.filter_by(user_id=current_user.id).all()
    
    # Get recommended scholarships
    recommendations = ai_agent.recommend_scholarships(current_user, top_n=5)
    
    # Get statistics
    total_apps = len(applications)
    submitted_apps = len([a for a in applications if a.status == 'submitted'])
    approved_apps = len([a for a in applications if a.status == 'approved'])
    
    return render_template('dashboard/index.html',
                         applications=applications,
                         recommendations=recommendations,
                         stats={
                             'total': total_apps,
                             'submitted': submitted_apps,
                             'approved': approved_apps
                         })

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.cgpa = float(request.form.get('cgpa', 0))
        current_user.course = request.form.get('course', '')
        current_user.year_of_study = int(request.form.get('year_of_study', 1))
        current_user.category = request.form.get('category', '')
        current_user.income = int(request.form.get('income', 0))
        current_user.phone = request.form.get('phone', '')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard.profile'))
    
    return render_template('dashboard/profile.html')