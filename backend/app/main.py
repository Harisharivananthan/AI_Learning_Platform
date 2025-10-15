from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database, utils, auth
from . import recommender

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Learning Platform Backend")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/login/")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not utils.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/courses/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.get("/recommend/{user_id}", response_model=list[schemas.CourseResponse])
def recommend_courses(user_id: int, db: Session = Depends(get_db)):
    courses = recommender.recommend_courses_for_user(user_id, db)
    return courses

@app.get("/courses/", response_model=list[schemas.CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

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
