"use client";
import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function Navbar() {
  const { user, signOut } = useAuth();

  return (
    <nav className="w-full flex items-center justify-between px-6 py-4 bg-gray-100 border-b mb-8">
      <Link href="/" className="font-bold text-lg">StudyVault</Link>
      <div className="flex items-center gap-4">
        {user && (
          <>
            <Link href="/dashboard" className="text-blue-600 hover:underline">
              Dashboard
            </Link>
            <Link href="/profile" className="text-blue-600 hover:underline">
              Profile
            </Link>
            <button
              onClick={signOut}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              Sign Out
            </button>
          </>
        )}
        {!user && (
          <>
            <Link href="/signin" className="text-blue-600 hover:underline">
              Sign In
            </Link>
            <Link href="/signup" className="text-blue-600 hover:underline">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
