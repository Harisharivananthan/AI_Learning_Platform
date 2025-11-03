"use client";
import React, { useState } from "react";

export default function RecommendByInterest() {
  const [interest, setInterest] = useState("");
  const [recommendations, setRecommendations] = useState([]);

  const handleSearch = () => {
    fetch(`http://127.0.0.1:8000/recommend/interest/?interest=${interest}`)
      .then((res) => res.json())
      .then((data) => setRecommendations(data.recommendations));
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-4 text-center">
        🎯 Recommend Courses by Interest
      </h1>

      <div className="flex justify-center gap-3 mb-6">
        <input
          type="text"
          placeholder="Enter your interest..."
          value={interest}
          onChange={(e) => setInterest(e.target.value)}
          className="border p-2 rounded w-1/2"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Search
        </button>
      </div>

      <ul className="bg-white rounded-lg shadow p-4">
        {recommendations.length === 0 ? (
          <p className="text-center text-gray-500">No recommendations found</p>
        ) : (
          recommendations.map((r, i) => <li key={i} className="py-2">{r}</li>)
        )}
      </ul>
    </div>
  );
}
