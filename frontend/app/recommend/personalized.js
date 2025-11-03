"use client";
import React, { useState } from "react";

export default function PersonalizedRecommendations() {
  const [userId, setUserId] = useState("");
  const [courses, setCourses] = useState([]);

  const handleFetch = () => {
    fetch(`http://127.0.0.1:8000/recommend/personalized/${userId}`)
      .then((res) => res.json())
      .then((data) => setCourses(data))
      .catch(() => setCourses([]));
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4 text-center">
        🤖 Personalized Recommendations
      </h1>

      <div className="flex justify-center gap-3 mb-6">
        <input
          type="number"
          placeholder="Enter your user ID..."
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="border p-2 rounded w-1/2"
        />
        <button
          onClick={handleFetch}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Get Recommendations
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {courses.length > 0 ? (
          courses.map((course) => (
            <div key={course.id} className="p-4 bg-white rounded shadow">
              <h3 className="font-bold">{course.title}</h3>
              <p className="text-sm text-gray-600">{course.category}</p>
            </div>
          ))
        ) : (
          <p className="text-center text-gray-500">No personalized courses found</p>
        )}
      </div>
    </div>
  );
}
