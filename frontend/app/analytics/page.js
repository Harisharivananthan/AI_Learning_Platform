"use client";
import React, { useEffect, useState } from "react";

export default function AnalyticsPage() {
  const [topCourses, setTopCourses] = useState([]);
  const [activeUsers, setActiveUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("http://127.0.0.1:8000/analytics/top-courses/").then((res) =>
        res.json()
      ),
      fetch("http://127.0.0.1:8000/analytics/active-users/").then((res) =>
        res.json()
      ),
    ])
      .then(([coursesData, usersData]) => {
        setTopCourses(coursesData);
        setActiveUsers(usersData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-center mt-10">Loading analytics...</p>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">📊 Analytics Dashboard</h1>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-3">🏆 Top Courses by Completion</h2>
        <ul className="bg-white rounded-lg shadow p-4">
          {topCourses.map((c, i) => (
            <li key={i} className="flex justify-between border-b py-2">
              <span>{c.title}</span>
              <span className="text-blue-600 font-semibold">
                {c.avg_completion}%
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-3">🔥 Most Active Users</h2>
        <ul className="bg-white rounded-lg shadow p-4">
          {activeUsers.map((u, i) => (
            <li key={i} className="flex justify-between border-b py-2">
              <span>{u.username}</span>
              <span className="text-green-600 font-semibold">
                {u.courses_count} courses
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
