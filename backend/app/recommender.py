# backend/app/recommender.py
from typing import List
from . import models
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------
# 1️⃣ Personalized recommender (existing)
# ---------------------------------------------
def recommend_courses_for_user(user_id: int, db: Session) -> List[models.Course]:
    """
    Simple rule-based recommender for existing user.
    For now, it returns up to 3 courses where user has less than 100% progress.
    """
    progress_data = db.query(models.Progress).filter(models.Progress.user_id == user_id).all()
    if not progress_data:
        # If no progress found, recommend first 3 courses
        return db.query(models.Course).limit(3).all()

    incomplete_courses = [p.course for p in progress_data if p.completion_percentage < 100]
    return incomplete_courses[:3]

# ---------------------------------------------
# 2️⃣ AI-based recommender by interest (NEW)
# ---------------------------------------------
def recommend_courses(interest: str):
    """
    Recommend courses based on free-text input using TF-IDF + cosine similarity.
    """
    # Example mock dataset — in Day 6, this will pull from the database
    course_data = [
        {"title": "Python for Beginners", "description": "Learn Python programming from scratch"},
        {"title": "Machine Learning Fundamentals", "description": "Supervised and unsupervised learning"},
        {"title": "Deep Learning with TensorFlow", "description": "Neural networks and CNNs"},
        {"title": "AI for Everyone", "description": "Introduction to artificial intelligence"},
        {"title": "Data Science with Python", "description": "Data analysis, visualization, and pandas"},
        {"title": "Natural Language Processing", "description": "Text analysis and language models"},
    ]

    corpus = [c["description"] for c in course_data] + [interest]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(corpus)
    similarity = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    # Sort by similarity and pick top 3
    top_indices = similarity.argsort()[-3:][::-1]
    recommendations = [course_data[i]["title"] for i in top_indices]

    return recommendations
