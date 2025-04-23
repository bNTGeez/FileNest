"use client";

import SignInForm from "../components/signinform";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Signin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      // Add your authentication logic here
      // Example:
      // const response = await signIn(email, password);
      // if (response.success) {
      //   router.push('/dashboard');
      // } else {
      //   setError(response.message);
      // }

      // For now, just simulate a successful login
      console.log("Login attempt with:", email, password);
      router.push("/dashboard");
    } catch (err) {
      setError("Failed to sign in. Please check your credentials.");
      console.error(err);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md">
        <SignInForm
          email={email}
          password={password}
          error={error}
          setEmail={setEmail}
          setPassword={setPassword}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
  );
}
