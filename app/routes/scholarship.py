from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.scholarship import Scholarship
from app.models.application import Application
from app.services.ai_agent import AIAgent

scholarships_bp = Blueprint('scholarships', __name__)

# -------------------------
# SCHOLARSHIP SEARCH
# -------------------------
@scholarships_bp.route('/scholarships')
@login_required
def search():
    query = request.args.get('q', '')

    ai_agent = AIAgent()

    scholarships_query = Scholarship.query

    # Search by scholarship name
    if query:
        scholarships_query = scholarships_query.filter(
            Scholarship.name.ilike(f"%{query}%")
        )

    all_scholarships = scholarships_query.all()

    # Show only eligible scholarships
    scholarships = []

    for scholarship in all_scholarships:
        eligibility = ai_agent.check_eligibility(
            current_user,
            scholarship
        )

        if eligibility.get("is_eligible", False):
            scholarships.append(scholarship)

    return render_template(
        'scholarships/search.html',
        scholarships=scholarships,
        query=query
    )


# -------------------------
# SCHOLARSHIP DETAILS
# -------------------------
@scholarships_bp.route('/scholarships/<int:id>')
@login_required
def details(id):
    scholarship = Scholarship.query.get_or_404(id)

    ai_agent = AIAgent()
    eligibility = ai_agent.check_eligibility(current_user, scholarship)

    return render_template(
        'scholarships/details.html',
        scholarship=scholarship,
        eligibility=eligibility
    )


# -------------------------
# APPLY SCHOLARSHIP
# -------------------------
@scholarships_bp.route('/scholarships/<int:id>/apply', methods=['GET', 'POST'])
@login_required
def apply(id):
    scholarship = Scholarship.query.get_or_404(id)

    ai_agent = AIAgent()

    #existing = Application.query.filter_by(
     #   user_id=current_user.id,
      #  scholarship_id=id
    #).first()

    #if existing:
     #   return redirect(
      #      url_for(
       #         'scholarships.application_details',
        #        id=existing.id
         #   )
      #  )

    if request.method == 'POST':
        application = ai_agent.create_application(
            current_user,
            scholarship
        )

        flash(
            'Application created successfully! Please review before submitting.',
            'success'
        )

        return redirect(
            url_for(
                'scholarships.application_details',
                id=application.id
            )
        )

    application_data = ai_agent.auto_fill_application(
        current_user,
        scholarship
    )

    eligibility = ai_agent.check_eligibility(
        current_user,
        scholarship
    )

    return render_template(
        'scholarships/apply.html',
        scholarship=scholarship,
        application_data=application_data,
        eligibility=eligibility
    )


# -------------------------
# APPLICATION DETAILS
# -------------------------
@scholarships_bp.route('/applications/<int:id>')
@login_required
def application_details(id):
    application = Application.query.get_or_404(id)

    if application.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard.index'))

    ai_agent = AIAgent()
    review_summary = ai_agent.generate_review_summary(application)

    return render_template(
        'scholarships/application_details.html',
        application=application,
        review_summary=review_summary
    )


# -------------------------
# REVIEW APPLICATION
# -------------------------
@scholarships_bp.route('/applications/<int:id>/review', methods=['POST'])
@login_required
def review_application(id):
    application = Application.query.get_or_404(id)

    if application.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard.index'))

    application.reviewed_by_user = True
    db.session.commit()

    flash('Application reviewed!', 'success')

    return redirect(
        url_for(
            'scholarships.application_details',
            id=id
        )
    )


# -------------------------
# SUBMIT APPLICATION
# -------------------------
@scholarships_bp.route('/applications/<int:id>/submit', methods=['POST'])
@login_required
def submit_application(id):
    application = Application.query.get_or_404(id)

    if application.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard.index'))

    if not application.reviewed_by_user:
        flash(
            'Please review your application before submitting',
            'warning'
        )

        return redirect(
            url_for(
                'scholarships.application_details',
                id=id
            )
        )

    application.status = 'submitted'
    application.submitted_at = db.func.current_timestamp()

    db.session.commit()

    flash(
        'Application submitted successfully!',
        'success'
    )

    return redirect(url_for('dashboard.index'))