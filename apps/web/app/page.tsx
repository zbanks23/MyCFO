"use client";

import {
  SignInButton,
  SignUpButton,
  UserButton,
  SignedIn,
  SignedOut,
  useAuth,
} from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function RootPage() {
  const { userId } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (userId) {
      router.push("/home");
    }
  }, [userId, router]);

  if (userId) {
    return null;
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <main className="text-center">
        <h1 className="text-4xl font-bold mb-4 text-gray-400">
          Welcome to MyCFO
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Your personal finance tracker. Please sign in to continue.
        </p>

        <SignedOut>
          <div className="space-x-4">
            <SignInButton mode="modal">
              <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                Sign Up
              </button>
            </SignUpButton>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}
