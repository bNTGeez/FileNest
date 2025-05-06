"use client";
import React from "react";
import { useRouter } from "next/navigation";
const Homepage = () => {
  const router = useRouter();
  return (
    <div>
      <button onClick={() => router.push("/signup")}>Get Started</button>
    </div>
  );
};

export default Homepage;
