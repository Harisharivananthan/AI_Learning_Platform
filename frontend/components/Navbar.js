"use client";
import Link from "next/link";

export default function Navbar() {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    window.location.href = "/login";
  };

  return (
    <nav className="bg-blue-600 p-4 text-white flex justify-between">
      <div>
        <Link href="/" className="mr-4">Home</Link>
        {token && <Link href="/courses" className="mr-4">Courses</Link>}
        {token && <Link href="/analytics" className="mr-4">Analytics</Link>}
      </div>
      {token ? (
        <button onClick={handleLogout}>Logout</button>
      ) : (
        <Link href="/login">Login</Link>
      )}
    </nav>
  );
}
