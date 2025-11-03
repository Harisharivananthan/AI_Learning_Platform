# backend/seed_data_day8.py
from sqlalchemy.orm import Session
from app import models, utils, database
import random

# -------------------------
# 1️⃣ Connect to Database
# -------------------------
db: Session = database.SessionLocal()

# -------------------------
# 2️⃣ Create Users
# -------------------------
users_data = [
    {"username": "harish", "email": "harish@example.com", "password": "123456"},
    {"username": "alice", "email": "alice@example.com", "password": "password1"},
    {"username": "bob", "email": "bob@example.com", "password": "password2"},
    {"username": "carol", "email": "carol@example.com", "password": "password3"},
    {"username": "david", "email": "david@example.com", "password": "password4"},
]

users = []
for u in users_data:
    hashed_pw = utils.hash_password(u["password"])
    user = models.User(username=u["username"], email=u["email"], password=hashed_pw)
    db.add(user)
    users.append(user)

db.commit()
print(f"✅ Added {len(users)} users.")

# -------------------------
# 3️⃣ Create Courses
# -------------------------
courses_data = [
    {"title": "Python for Beginners", "category": "Programming", "description": "Learn Python programming from scratch."},
    {"title": "Advanced Python", "category": "Programming", "description": "Deep dive into OOP, decorators, and async programming."},
    {"title": "Machine Learning Fundamentals", "category": "Machine Learning", "description": "Supervised and unsupervised learning."},
    {"title": "Deep Learning with TensorFlow", "category": "AI", "description": "Understand neural networks, CNNs, and RNNs."},
    {"title": "Natural Language Processing", "category": "AI", "description": "Text analytics, tokenization, and transformers."},
    {"title": "Data Science with Python", "category": "Data Science", "description": "Data cleaning, visualization, and predictive analysis."},
    {"title": "Computer Vision Essentials", "category": "AI", "description": "Image processing, object detection, and CNN models."},
    {"title": "AI for Everyone", "category": "AI", "description": "An introduction to AI and real-world applications."},
    {"title": "Reinforcement Learning", "category": "Machine Learning", "description": "Learn reward-based learning and policy gradients."},
    {"title": "Chatbot Development", "category": "NLP", "description": "Build smart conversational agents using transformers."},
    {"title": "SQL for Data Analysis", "category": "Data Science", "description": "Learn SQL queries for analyzing data."},
    {"title": "Statistics Fundamentals", "category": "Data Science", "description": "Probability and statistics for ML."},
    {"title": "Time Series Analysis", "category": "Data Science", "description": "Forecasting using Python."},
]

courses = []
for c in courses_data:
    course = models.Course(**c)
    db.add(course)
    courses.append(course)

db.commit()
print(f"✅ Added {len(courses)} courses.")

# -------------------------
# 4️⃣ Create Random Progress
# -------------------------
progress_entries = []
for user in users:
    for course in courses:
        completion = random.choice([0, 10, 25, 50, 75, 100])
        if completion == 100:
            status = "completed"
        elif completion > 0:
            status = "in-progress"
        else:
            status = "not-started"

        progress = models.Progress(
            user_id=user.id,
            course_id=course.id,
            completion_percentage=completion,
            status=status
        )
        db.add(progress)
        progress_entries.append(progress)

db.commit()
print(f"✅ Added {len(progress_entries)} progress entries.")

# -------------------------
# 5️⃣ Verification Summary
# -------------------------
user_count = db.query(models.User).count()
course_count = db.query(models.Course).count()
progress_count = db.query(models.Progress).count()
print(f"\n📊 Summary:")
print(f"Users: {user_count}")
print(f"Courses: {course_count}")
print(f"Progress Records: {progress_count}")

# -------------------------
# 6️⃣ Close DB
# -------------------------
db.close()
print("\n✅ Day 8 Dataset Seeding Complete!")
