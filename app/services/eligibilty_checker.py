from typing import Dict
from app.models.user import User
from app.models.scholarship import Scholarship


class EligibilityChecker:
    """Check user eligibility for scholarships"""

    def check(self, user: User, scholarship: Scholarship) -> Dict:
        """
        Returns:
        {
            'is_eligible': bool,
            'score': float,
            'notes': str,
            'missing': list,
            'recommendation': str
        }
        """

        notes = []
        missing = []
        score = 100.0

        # CGPA Check
        if scholarship.min_cgpa:
            if user.cgpa is None:
                missing.append("CGPA")
                score -= 30
                notes.append("CGPA not provided")

            elif user.cgpa < scholarship.min_cgpa:
                score -= (scholarship.min_cgpa - user.cgpa) * 20
                notes.append(
                    f"CGPA {user.cgpa} is below minimum {scholarship.min_cgpa}"
                )

        # Income Check
        if scholarship.max_income:
            if user.income is None:
                missing.append("Income")
                score -= 20
                notes.append("Income not provided")

            elif user.income > scholarship.max_income:
                score -= 50
                notes.append(
                    f"Income ₹{user.income} exceeds maximum ₹{scholarship.max_income}"
                )

        # Category Check
        if scholarship.accepted_categories:
            if user.category is None:
                missing.append("Category")
                score -= 15
                notes.append("Category not provided")

            elif user.category not in scholarship.accepted_categories:
                score -= 40
                notes.append(
                    f"Category {user.category} not accepted"
                )

        # Course Check
        if scholarship.course_type:
            if user.course is None:
                missing.append("Course")
                score -= 15
                notes.append("Course not provided")

            elif scholarship.course_type not in user.course:
                score -= 30
                notes.append(
                    f"Course {user.course} doesn't match {scholarship.course_type}"
                )

        # Required Documents Check
        required_docs = scholarship.required_documents or []

        try:
            user_doc_types = [doc.document_type for doc in user.documents]
        except:
            user_doc_types = []

        for req_doc in required_docs:
            if req_doc not in user_doc_types:
                missing.append(req_doc)
                score -= 10
                notes.append(f"Missing document: {req_doc}")

        # Final Score
        score = max(0, min(100, score))

        # Eligibility Decision
        is_eligible = score >= 60

        # Recommendation Level
        if score >= 90:
            recommendation = "Highly Recommended"

        elif score >= 75:
            recommendation = "Recommended"

        elif score >= 60:
            recommendation = "Possible Match"

        else:
            recommendation = "Not Recommended"

        return {
            "is_eligible": is_eligible,
            "score": round(score, 2),
            "notes": "; ".join(notes) if notes else "All criteria met",
            "missing": missing,
            "recommendation": recommendation
        }