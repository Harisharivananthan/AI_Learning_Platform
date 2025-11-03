// frontend/app/courses/page.js
"use client";

import { useState, useEffect } from "react";

export default function CoursesPage() {
  const [allCourses, setAllCourses] = useState([]);
  const [personalized, setPersonalized] = useState([]);
  const [interest, setInterest] = useState("");
  const [interestResults, setInterestResults] = useState([]);
  const [userId, setUserId] = useState(null);
  const [token, setToken] = useState("");

  // Get token & userId from localStorage (after login)
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUserId = localStorage.getItem("userId");
    if (savedToken) setToken(savedToken);
    if (savedUserId) setUserId(savedUserId);
  }, []);

  // Fetch all courses
  useEffect(() => {
    fetch("http://127.0.0.1:8000/courses/")
      .then((res) => res.json())
      .then((data) => setAllCourses(data))
      .catch((err) => console.error(err));
  }, []);

  // Fetch personalized recommendations
  useEffect(() => {
    if (!userId || !token) return;
    fetch(`http://127.0.0.1:8000/recommend/personalized/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setPersonalized(data))
      .catch((err) => console.error(err));
  }, [userId, token]);

  // Handle interest search
  const handleInterestSearch = () => {
    if (!interest) return;
    fetch(`http://127.0.0.1:8000/recommend/interest/?interest=${interest}`)
      .then((res) => res.json())
      .then((data) => setInterestResults(data.recommendations))
      .catch((err) => console.error(err));
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">AI Learning Platform</h1>

      {/* Interest Search */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Enter your interest..."
          value={interest}
          onChange={(e) => setInterest(e.target.value)}
          className="border p-2 mr-2 rounded w-1/2"
        />
        <button
          onClick={handleInterestSearch}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Search
        </button>
      </div>

      {/* Interest Recommendations */}
      {interestResults.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Recommended for your interest:</h2>
          <ul className="list-disc pl-6">
            {interestResults.map((course, idx) => (
              <li key={idx}>{course}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Personalized Recommendations */}
      {personalized.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Personalized Recommendations:</h2>
          <ul className="list-disc pl-6">
            {personalized.map((course) => (
              <li key={course.id}>
                <strong>{course.title}</strong> - {course.category}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* All Courses */}
      <div>
        <h2 className="text-xl font-semibold mb-2">All Courses:</h2>
        <ul className="list-disc pl-6">
          {allCourses.map((course) => (
            <li key={course.id}>
              <strong>{course.title}</strong> - {course.category}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
