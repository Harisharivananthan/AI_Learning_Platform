const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function registerUser(username, email, password) {
  const response = await fetch(`${API_BASE}/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Registration failed");
  }

  return await response.json();
}

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE}/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Login failed");
  }

  const data = await response.json();
  localStorage.setItem("token", data.access_token);
  return data;
}
