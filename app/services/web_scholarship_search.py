import requests

class WebScholarshipSearch:

    def search(self, query):
        results = []

        sources = [
            {
                "name": "Buddy4Study",
                "url": f"https://www.buddy4study.com/search?keyword={query}"
            },
            {
                "name": "National Scholarship Portal",
                "url": "https://scholarships.gov.in/"
            },
            {
                "name": "AICTE Scholarships",
                "url": "https://www.aicte-india.org/"
            },
            {
                "name": "Vidya Lakshmi",
                "url": "https://www.vidyalakshmi.co.in/"
            }
        ]

        for source in sources:
            results.append({
                "name": f"{query.title()} Opportunities",
                "provider": source["name"],
                "amount": "Check Website",
                "description": f"Scholarships related to {query}",
                "url": source["url"]
            })

        return results