import json
from typing import Dict, List, Optional
from app.models.user import User
from app.models.scholarship import Scholarship
from app.models.application import Application, ApplicationDocument
from app.services.eligibilty_checker import EligibilityChecker
from app.services.document_processor import DocumentProcessor
from app.services.scholarship_searcher import ScholarshipSearcher
from app import db

class AIAgent:
    """Main AI Agent for Life Pilot"""
    
    def __init__(self):
        self.eligibility_checker = EligibilityChecker()
        self.document_processor = DocumentProcessor()
        self.scholarship_searcher = ScholarshipSearcher()

    def search_scholarships(self, user, query=None):
        """Search scholarships by user profile or query."""
        if query:
            results = self.scholarship_searcher.search_by_query(query, user)

            eligible_scholarships = []
            for scholarship in results:
                score = 0

                if scholarship.get("min_cgpa") is None:
                    score += 25
                elif user.cgpa and user.cgpa >= scholarship["min_cgpa"]:
                    score += 25

                if scholarship.get("max_income") is None:
                    score += 25
                elif user.income and user.income <= scholarship["max_income"]:
                    score += 25

                if scholarship.get("gender") is None:
                    score += 25
                elif getattr(user, "gender", None) == scholarship["gender"]:
                    score += 25

                if scholarship.get("category") is None:
                    score += 25
                elif getattr(user, "category", None) == scholarship["category"]:
                    score += 25

                scholarship["eligibility_score"] = score
                if score >= 50:
                    eligible_scholarships.append(scholarship)

            eligible_scholarships.sort(
                key=lambda x: x["eligibility_score"],
                reverse=True
            )
            return eligible_scholarships

        return self.scholarship_searcher.search_by_profile(user)

    def check_eligibility(self, user: User, scholarship: Scholarship) -> Dict:
        """
        Check detailed eligibility for a scholarship
        """
        return self.eligibility_checker.check(user, scholarship)
    
    def auto_fill_application(self, user: User, scholarship: Scholarship) -> Dict:
        """
        Auto-fill application form using user data and uploaded documents
        """
        application_data = {
            'full_name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'phone': user.phone,
            'cgpa': user.cgpa,
            'course': user.course,
            'year_of_study': user.year_of_study,
            'category': user.category,
            'income': user.income,
        }
        
        # Extract additional info from documents
        doc_info = self.document_processor.extract_user_info(user)
        application_data.update(doc_info)
        
        return application_data
    
    def recommend_scholarships(self, user: User, top_n: int = 5) -> List[Scholarship]:
        """
        Recommend best scholarships for user based on eligibility score
        """
        all_scholarships = Scholarship.query.all()
        
        scored_scholarships = []
        for scholarship in all_scholarships:
            eligibility = self.check_eligibility(user, scholarship)
            if eligibility['is_eligible']:
                scored_scholarships.append({
                    'scholarship': scholarship,
                    'score': eligibility['score'],
                    'notes': eligibility['notes']
                })
        
        # Sort by score
        scored_scholarships.sort(key=lambda x: x['score'], reverse=True)
        
        return [item['scholarship'] for item in scored_scholarships[:top_n]]
    
    def create_application(self, user: User, scholarship: Scholarship) -> Application:
        """
        Create a new application with auto-filled data
        """
        application_data = self.auto_fill_application(user, scholarship)
        
        application = Application(
            user_id=user.id,
            scholarship_id=scholarship.id,
            application_data=application_data,
            auto_filled=True,
            eligibility_score=self.check_eligibility(user, scholarship)['score']
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Auto-attach documents
        self.attach_documents(application, scholarship)
        
        return application
    
    def attach_documents(self, application: Application, scholarship: Scholarship):
        """
        Auto-attach relevant documents from user's uploads
        """
        required_docs = scholarship.required_documents or []
        user_docs = application.user.documents
        
        for req_doc_type in required_docs:
            for doc in user_docs:
                if doc.document_type == req_doc_type:
                    app_doc = ApplicationDocument(
                        application_id=application.id,
                        document_id=doc.id,
                        document_type=req_doc_type
                    )
                    db.session.add(app_doc)
        
        db.session.commit()
    
    def generate_review_summary(self, application: Application) -> str:
        """
        Generate a summary for user to review before submission
        """
        user = User.query.get(application.user_id)
        scholarship = Scholarship.query.get(application.scholarship_id)
        eligibility = self.check_eligibility(user, scholarship)
        
        summary = f"""
        Application Review Summary
        =========================
        
        Scholarship: {scholarship.name}
        Amount: ₹{scholarship.amount}
        
        Eligibility Score: {eligibility['score']}/100
        Is Eligible: {'Yes' if eligibility['is_eligible'] else 'No'}
        
        Auto-filled Information:
        - Name: {application.application_data.get('full_name')}
        - Email: {application.application_data.get('email')}
        - CGPA: {application.application_data.get('cgpa')}
        - Course: {application.application_data.get('course')}
        - Category: {application.application_data.get('category')}
        
        Documents Attached: {len(application.documents)}
        
        AI Notes: {application.ai_notes}
        """
        
        return summary