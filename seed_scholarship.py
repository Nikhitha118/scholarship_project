from app import create_app, db
from app.models.scholarship import Scholarship
from datetime import date

app = create_app()

with app.app_context():

    # Delete old scholarships (optional)
    Scholarship.query.delete()
    db.session.commit()

    scholarships = [

        Scholarship(
            name="Post Matric Scholarship",
            provider="Government of India",
            amount=50000,
            category="Need-based",
            course_type="B.Tech",
            max_income=250000,
            accepted_categories=["SC", "ST"],
            application_end=date(2026, 12, 31)
        ),

        Scholarship(
            name="OBC Scholarship",
            provider="State Government",
            amount=30000,
            category="Need-based",
            course_type="B.Tech",
            max_income=200000,
            accepted_categories=["OBC"],
            application_end=date(2026, 12, 31)
        ),

        Scholarship(
            name="Merit Scholarship",
            provider="AICTE",
            amount=75000,
            category="Merit-based",
            course_type="B.Tech",
            min_cgpa=7.0,
            max_income=500000,
            accepted_categories=["OC", "General", "OBC", "SC", "ST"],
            application_end=date(2026, 12, 31)
        ),

        Scholarship(
            name="Minority Scholarship",
            provider="National Scholarship Portal",
            amount=40000,
            category="Need-based",
            max_income=250000,
            accepted_categories=["Minority"],
            application_end=date(2026, 12, 31)
        ),

        Scholarship(
            name="General Merit Scholarship",
            provider="State Education Board",
            amount=25000,
            category="Merit-based",
            course_type="B.Tech",
            min_cgpa=7.0,
            max_income=300000,
            accepted_categories=["OC", "General"],
            application_end=date(2026, 11, 30)
        ),

        Scholarship(
            name="Engineering Excellence Scholarship",
            provider="Tech Foundation",
            amount=60000,
            category="Academic",
            course_type="B.Tech",
            min_cgpa=7.5,
            max_income=500000,
            accepted_categories=["OC", "General", "OBC", "SC", "ST"],
            application_end=date(2026, 10, 31)
        ),

        Scholarship(
            name="Women in STEM Scholarship",
            provider="Women Tech Trust",
            amount=45000,
            category="Academic",
            course_type="B.Tech",
            max_income=500000,
            accepted_categories=["OC", "General", "OBC", "SC", "ST"],
            application_end=date(2026, 9, 30)
        ),

        Scholarship(
            name="Academic Achievement Scholarship",
            provider="National Education Trust",
            amount=35000,
            category="Merit-based",
            course_type="B.Tech",
            min_cgpa=6.5,
            max_income=400000,
            accepted_categories=["OC", "General"],
            application_end=date(2026, 12, 15)
        )

    ]

    db.session.add_all(scholarships)
    db.session.commit()

    print("8 Scholarships Added Successfully!")