from typing import List
from app.models.user import User
from app.models.scholarship import Scholarship
from app.services.web_scholarship_search import WebScholarshipSearch


class ScholarshipSearcher:
    """Search for scholarships based on user profile and queries"""

    def __init__(self):
        self.web_search = WebScholarshipSearch()

    def search_by_profile(self, user: User) -> List[Scholarship]:
        """Search scholarships matching user profile"""

        query = Scholarship.query

        if user.course:
            query = query.filter(
                (Scholarship.course_type.is_(None)) |
                (Scholarship.course_type.contains(user.course))
            )

        if user.category:
            query = query.filter(
                (Scholarship.accepted_categories.is_(None)) |
                (Scholarship.accepted_categories.contains([user.category]))
            )

        return query.all()

    def search_by_query(self, query_text: str, user: User):
        """
        Search scholarships from internet
        """
        return self.web_search.search(query_text)

    def get_featured_scholarships(self, limit: int = 10):
        return Scholarship.query.limit(limit).all()