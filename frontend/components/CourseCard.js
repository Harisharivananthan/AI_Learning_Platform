"use client";

export default function CourseCard({ course }) {
  return (
    <div style={{ border: "1px solid #ddd", margin: "10px", padding: "10px", borderRadius: "5px" }}>
      <h3>{course.title}</h3>
      <p>{course.description}</p>
      <p><b>Category:</b> {course.category}</p>
    </div>
  );
}
