const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

function getHeaders() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
}

export async function getCourses() {
  const res = await fetch(`${API_BASE}/courses/`, { headers: getHeaders() });
  if (!res.ok) throw new Error("Failed to fetch courses");
  return await res.json();
}

export async function getPersonalizedRecommendations(userId) {
  const res = await fetch(`${API_BASE}/recommend/personalized/${userId}`, {
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error("Failed to fetch recommendations");
  return await res.json();
}

export async function getAnalytics() {
  const [topCourses, activeUsers] = await Promise.all([
    fetch(`${API_BASE}/analytics/top-courses/`).then((r) => r.json()),
    fetch(`${API_BASE}/analytics/active-users/`).then((r) => r.json()),
  ]);
  return { topCourses, activeUsers };
}
