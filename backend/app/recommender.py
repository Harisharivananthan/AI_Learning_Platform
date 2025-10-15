from typing import List
from . import models

def recommend_courses_for_user(user_id: int, db) -> List[models.Course]:
    """
    Placeholder logic — later this will use ML to recommend courses.
    For now, return top 3 courses with least progress.
    """
    progress_data = db.query(models.Progress).filter(models.Progress.user_id == user_id).all()
    if not progress_data:
        return db.query(models.Course).limit(3).all()

    incomplete_courses = [p.course for p in progress_data if p.completion_percentage < 100]
    return incomplete_courses[:3]
