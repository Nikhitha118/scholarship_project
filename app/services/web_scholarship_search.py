import requests

class WebScholarshipSearch:

    def search(self, query):

        return [

            {
                "name": "Pragati Scholarship",
                "provider": "AICTE",
                "amount": 50000,
                "description": "Scholarship for female engineering students",

                "min_cgpa": 7.0,
                "max_income": 800000,
                "gender": "Female",
                "category": None,

                "eligibility_score": 0,

                "url": "https://www.aicte-india.org/"
            },

            {
                "name": "NSP Merit Scholarship",
                "provider": "National Scholarship Portal",
                "amount": 30000,
                "description": "Merit based scholarship",

                "min_cgpa": 8.0,
                "max_income": 600000,
                "gender": None,
                "category": ["OBC", "SC", "ST"],

                "eligibility_score": 0,

                "url": "https://scholarships.gov.in/"
            },

            {
                "name": "Saksham Scholarship",
                "provider": "AICTE",
                "amount": 50000,
                "description": "Scholarship for specially-abled students",

                "min_cgpa": 6.0,
                "max_income": 800000,
                "gender": None,
                "category": None,

                "eligibility_score": 0,

                "url": "https://www.aicte-india.org/"
            },

            {
                "name": "Post Matric Scholarship",
                "provider": "NSP",
                "amount": 25000,
                "description": "Scholarship for SC/ST students",

                "min_cgpa": 5.0,
                "max_income": 250000,
                "gender": None,
                "category": ["SC", "ST"],

                "eligibility_score": 0,

                "url": "https://scholarships.gov.in/"
            }
        ]