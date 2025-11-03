# backend/app/recommender.py
from typing import List
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np

from fastapi import APIRouter, Depends
from app import models, database
from app.ai_service import generate_ai_recommendation


# -------------------------------------------------------
# 🌟 1️⃣ Free-text Interest Recommender (Day 5)
# -------------------------------------------------------
def recommend_courses_by_interest(interest: str):
    """
    Recommend courses based on free-text input using TF-IDF similarity.
    """
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
    top_indices = similarity.argsort()[-3:][::-1]
    recommendations = [course_data[i]["title"] for i in top_indices]
    return recommendations


# -------------------------------------------------------
# 🌟 2️⃣ Personalized Course Recommender (Day 6)
# -------------------------------------------------------
def recommend_courses_for_user(user_id: int, db: Session) -> List[models.Course]:
    """
    Personalized recommendation based on:
    - User progress (incomplete courses)
    - Course similarity using TF-IDF
    """
    # Get all courses
    courses = db.query(models.Course).all()
    courses_df = pd.DataFrame([{
        "id": c.id,
        "title": c.title,
        "category": c.category,
        "description": c.description
    } for c in courses])

    # Get user progress
    progress = db.query(models.Progress).filter(models.Progress.user_id == user_id).all()
    progress_df = pd.DataFrame([{
        "course_id": p.course_id,
        "completion": p.completion_percentage
    } for p in progress])

    # Find incomplete courses
    incomplete_ids = progress_df[progress_df.completion < 100]["course_id"].tolist()
    if not incomplete_ids:
        incomplete_ids = courses_df["id"].tolist()

    filtered_courses = courses_df[courses_df["id"].isin(incomplete_ids)]

    # TF-IDF on category + description
    filtered_courses["text"] = filtered_courses["category"] + " " + filtered_courses["description"].fillna("")
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(filtered_courses["text"])

    # User profile vector
    if len(filtered_courses) > 0:
        user_vector = tfidf_matrix.mean(axis=0)
    else:
        user_vector = tfidf_matrix[0]

    # Cosine similarity
    similarity = cosine_similarity(user_vector, tfidf_matrix).flatten()
    top_indices = similarity.argsort()[-3:][::-1]
    top_courses = filtered_courses.iloc[top_indices]

    return db.query(models.Course).filter(models.Course.id.in_(top_courses["id"].tolist())).all()


# -------------------------------------------------------
# 🌟 3️⃣ Category-Based Recommender (Analytics Support)
# -------------------------------------------------------
def recommend_courses_by_category(category: str, db: Session) -> List[models.Course]:
    """
    Return top 3 courses for a given category.
    """
    return db.query(models.Course).filter(models.Course.category.ilike(f"%{category}%")).limit(3).all()


# -------------------------------------------------------
# 🌟 4️⃣ ML-Based Course Recommender (Day 8)
# -------------------------------------------------------
def ml_recommend_courses(user_id: int, db: Session, top_n=3) -> List[models.Course]:
    """
    ML-based recommendation using Nearest Neighbors on TF-IDF embeddings.
    """
    # Fetch courses
    courses = db.query(models.Course).all()
    courses_df = pd.DataFrame([{
        "id": c.id,
        "title": c.title,
        "category": c.category,
        "description": c.description
    } for c in courses])

    if courses_df.empty:
        return []

    # TF-IDF features
    courses_df["text"] = courses_df["category"] + " " + courses_df["description"].fillna("")
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(courses_df["text"])

    # User progress
    progress = db.query(models.Progress).filter(models.Progress.user_id == user_id).all()
    completed_course_ids = [p.course_id for p in progress if p.completion_percentage >= 50]

    # Fallback: new user
    if not completed_course_ids:
        return courses[:top_n]

    # Nearest Neighbors
    nn = NearestNeighbors(n_neighbors=top_n, metric="cosine")
    nn.fit(tfidf_matrix)

    user_course_idx = [
        courses_df[courses_df["id"] == cid].index[0]
        for cid in completed_course_ids if cid in courses_df["id"].values
    ]
    if not user_course_idx:
        return courses[:top_n]

    distances, indices = nn.kneighbors(tfidf_matrix[user_course_idx])
    recommended_ids = list(set(courses_df.iloc[indices.flatten()]["id"].tolist()))
    recommended_ids = [cid for cid in recommended_ids if cid not in completed_course_ids][:top_n]

    return db.query(models.Course).filter(models.Course.id.in_(recommended_ids)).all()


# -------------------------------------------------------
# 🌟 5️⃣ AI Assistant Router (AI-Powered Suggestions)
# -------------------------------------------------------
router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.get("/recommendations/{user_id}")
def get_ai_recommendations(user_id: int, db: Session = Depends(database.get_db)):
    """
    Generate AI-based personalized learning suggestions using user's course progress.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    progress_entries = db.query(models.Progress).filter(models.Progress.user_id == user_id).all()
    summary = ", ".join(
        [f"{p.course_id}:{p.completion_percentage}%" for p in progress_entries]
    ) or "No progress yet."

    ai_message = generate_ai_recommendation(user.username, summary)
    return {"user": user.username, "ai_recommendations": ai_message}
