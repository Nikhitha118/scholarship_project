from datetime import datetime
from app import db

class Scholarship(db.Model):
    __tablename__ = 'scholarships'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    provider = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    currency = db.Column(db.String(10), default='INR')
    
    # Eligibility criteria (stored as JSON)
    eligibility_criteria = db.Column(db.JSON)
    
    # Requirements
    required_documents = db.Column(db.JSON)  # ['marksheet', 'id_proof', 'income_certificate']
    
    # Dates
    application_start = db.Column(db.Date)
    application_end = db.Column(db.Date)
    
    # Metadata
    category = db.Column(db.String(50))  # Academic, Merit-based, Need-based
    course_type = db.Column(db.String(50))  # B.Tech, M.Tech, MBA
    min_cgpa = db.Column(db.Float)
    max_income = db.Column(db.Integer)
    accepted_categories = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='scholarship', lazy=True)
    
    def is_eligible(self, user):
        """Check if user meets eligibility criteria"""

        print("==========")
        print("Scholarship:", self.name)
        print("User Income:", user.income)
        print("Max Income:", self.max_income)
        print("User Category:", user.category)
        print("Accepted Categories:", self.accepted_categories)

        if self.min_cgpa and (user.cgpa is None or user.cgpa < self.min_cgpa):
            print("Failed CGPA")
            return False

        if self.max_income and (user.income is None or user.income > self.max_income):
            print("Failed Income")
            return False

        if self.accepted_categories:
            user_cat = str(user.category).upper()
            accepted = [str(cat).upper() for cat in self.accepted_categories]

            if user_cat not in accepted:
                print("Failed Category")
                return False

        #if self.course_type and user.course and self.course_type not in user.course:
         #   print("Failed Course")
          #  return False

        print("Eligible")
        return True