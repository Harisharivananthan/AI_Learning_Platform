# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

# -------------------- Internal Imports --------------------
from app import models, schemas, database, utils, auth, recommender
from app.recommender import router as ai_router          # AI recommender endpoints
from app.api import ai_routes                            # Additional AI routes
from app.ai_chat import router as chat_router             # Chatbot routes

# -------------------- Initialize Application --------------------
app = FastAPI(title="AI Learning Platform Backend")

# -------------------- Include Routers --------------------
app.include_router(ai_router)          # Recommender endpoints
app.include_router(ai_routes.router)   # AI API endpoints
app.include_router(chat_router)        # Chatbot endpoints

# -------------------- Create Database Tables --------------------
models.Base.metadata.create_all(bind=database.engine)

# -------------------- Database Dependency --------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- Root Route --------------------
@app.get("/")
def home():
    return {"message": "AI Learning Platform is running!"}

# -------------------- User Registration --------------------
@app.post("/register/", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = utils.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -------------------- User Login --------------------
@app.post("/login/")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not utils.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

# -------------------- Course Management --------------------
@app.post("/courses/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.get("/courses/", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

# -------------------- User Progress --------------------
@app.post("/progress/", response_model=schemas.ProgressResponse)
def create_progress(progress: schemas.ProgressCreate, db: Session = Depends(get_db)):
    new_progress = models.Progress(**progress.dict())
    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)
    return new_progress

@app.get("/progress/user/{user_id}", response_model=list[schemas.ProgressResponse])
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Progress).filter(models.Progress.user_id == user_id).all()

@app.put("/progress/{progress_id}", response_model=schemas.ProgressResponse)
def update_progress(progress_id: int, updated: schemas.ProgressCreate, db: Session = Depends(get_db)):
    progress = db.query(models.Progress).filter(models.Progress.id == progress_id).first()
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")

    progress.completion_percentage = updated.completion_percentage
    progress.status = updated.status
    db.commit()
    db.refresh(progress)
    return progress

# -------------------- Interest-Based Recommender --------------------
@app.get("/recommend/interest/")
def recommend_by_interest(interest: str):
    results = recommender.recommend_courses_by_interest(interest)
    return {"recommendations": results}

# -------------------- Personalized Recommender --------------------
@app.get("/recommend/personalized/{user_id}", response_model=list[schemas.CourseResponse])
def recommend_personalized(user_id: int, db: Session = Depends(get_db)):
    courses = recommender.recommend_courses_for_user(user_id, db)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found for recommendation")
    return courses

# -------------------- Analytics Endpoints --------------------
@app.get("/analytics/top-courses/")
def top_courses(db: Session = Depends(get_db), limit: int = 5):
    results = (
        db.query(models.Course.title, func.avg(models.Progress.completion_percentage).label("avg_completion"))
        .join(models.Progress, models.Course.id == models.Progress.course_id)
        .group_by(models.Course.id)
        .order_by(func.avg(models.Progress.completion_percentage).desc())
        .limit(limit)
        .all()
    )
    return [{"title": r[0], "avg_completion": round(r[1], 2)} for r in results]

@app.get("/analytics/active-users/")
def active_users(db: Session = Depends(get_db), limit: int = 5):
    results = (
        db.query(models.User.username, func.count(models.Progress.id).label("courses_count"))
        .join(models.Progress, models.User.id == models.Progress.user_id)
        .filter(models.Progress.completion_percentage > 0)
        .group_by(models.User.id)
        .order_by(func.count(models.Progress.id).desc())
        .limit(limit)
        .all()
    )
    return [{"username": r[0], "courses_count": r[1]} for r in results]

@app.get("/analytics/user-progress/{user_id}")
def user_progress_summary(user_id: int, db: Session = Depends(get_db)):
    progress_data = (
        db.query(models.Course.title, models.Progress.completion_percentage, models.Progress.status)
        .join(models.Progress, models.Course.id == models.Progress.course_id)
        .filter(models.Progress.user_id == user_id)
        .all()
    )
    if not progress_data:
        return JSONResponse({"message": "No progress found for this user"}, status_code=404)
    return [{"course": r[0], "completion": r[1], "status": r[2]} for r in progress_data]

# -------------------- Career & Adaptive Learning --------------------
@app.get("/career/recommend/{user_id}")
def career_recommendation(user_id: int, db: Session = Depends(get_db)):
    """Recommend possible AI/ML career paths based on user's completed courses."""
    progress = db.query(models.Progress).filter(models.Progress.user_id == user_id).all()
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found for this user")

    completed_courses = [
        db.query(models.Course).filter(models.Course.id == p.course_id).first().title
        for p in progress if p.completion_percentage >= 80
    ]

    if not completed_courses:
        return {"message": "Complete at least one course to get career recommendations"}

    recommendations = recommender.recommend_career_paths(completed_courses)
    return {"completed_courses": completed_courses, "career_recommendations": recommendations}

@app.get("/learning/insights/{user_id}")
def adaptive_learning_insights(user_id: int, db: Session = Depends(get_db)):
    """Provide adaptive feedback based on user performance."""
    progress = db.query(models.Progress).filter(models.Progress.user_id == user_id).all()
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found")

    avg_completion = sum([p.completion_percentage for p in progress]) / len(progress)
    if avg_completion >= 90:
        message = "Excellent progress! You’re ready for advanced projects or internships."
    elif avg_completion >= 50:
        message = "Good job! Keep pushing toward 100% completion to unlock next recommendations."
    else:
        message = "Focus on completing more beginner-level courses to strengthen your foundation."

    return {
        "user_id": user_id,
        "average_completion": round(avg_completion, 2),
        "adaptive_message": message,
    }
