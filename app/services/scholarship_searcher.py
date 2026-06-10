from typing import List
from app.models.user import User
from app.models.scholarship import Scholarship
from app.services.web_scholarship_search import WebScholarshipSearch


class ScholarshipSearcher:
    """Search for scholarships based on user profile and queries"""

    def __init__(self):
        self.web_search = WebScholarshipSearch()

    def search_by_profile(self, user):
        scholarships = Scholarship.query.all()

        print("TOTAL SCHOLARSHIPS =", len(scholarships))

        eligible = []

        for scholarship in scholarships:
            if scholarship.is_eligible(user):
                eligible.append(scholarship)

        print("ELIGIBLE =", len(eligible))

        return eligible

    def search_by_query(self, query_text: str, user: User):
        """
        Search scholarships from internet
        """
        return self.web_search.search(query_text)

    def get_featured_scholarships(self, limit: int = 10):
        return Scholarship.query.limit(limit).all()