from datetime import datetime
from app import db

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarships.id'), nullable=False)
    
    status = db.Column(db.String(20), default='draft')  # draft, submitted, under_review, approved, rejected
    auto_filled = db.Column(db.Boolean, default=False)
    reviewed_by_user = db.Column(db.Boolean, default=False)
    
    # Application data (JSON)
    application_data = db.Column(db.JSON)
    
    # AI agent notes
    ai_notes = db.Column(db.Text)
    eligibility_score = db.Column(db.Float)  # 0-100
    
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('ApplicationDocument', backref='application', lazy=True)
    
    def __repr__(self):
        return f'<Application {self.id} User {self.user_id} Scholarship {self.scholarship_id}>'


class ApplicationDocument(db.Model):
    __tablename__ = 'application_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    document_type = db.Column(db.String(50))  # marksheet, id_proof, etc
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    document = db.relationship('Document', backref='application_documents')