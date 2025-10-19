"use client";

import { SignInButton, SignUpButton, SignedOut, useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

export default function RootPage() {
  const { isLoaded, isSignedIn, user } = useUser();
  const router = useRouter();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

  const handleSyncUser = async () => {
    console.log("Data being sent to backend");
    try {
      const response = await fetch(`${apiUrl}/api/users/sync_user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(user),
        credentials: "include",
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to sync user");
      }
      console.log(`Sync successful: ${data.message}`);
    } catch (error: any) {
      console.error("Sync failed:", error);
    }
  };

  const handleGuestContinue = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/users/continue_as_guest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      const data = await response.json();
      console.log(data.message);
      if (!response.ok) {
        throw new Error(data.error || "Failed to continue as guest");
      }
    } catch (error) {
      console.error("Error continuing as guest:", error);
    }
    router.push("/home");
  };

  useEffect(() => {
    if (isLoaded) {
      if (isSignedIn) {
        const syncAndRedirect = async () => {
          await handleSyncUser();
          router.push("/home");
        };
        syncAndRedirect();
      }
    }
  }, [user]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <main className="text-center">
        <h1 className="text-4xl font-bold mb-4 text-gray-400">
          Welcome to MyCFO
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Your personal finance tracker. Please login / signup to continue, or continue as guest.
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
            <button
              className="bg-gray-400 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
              onClick={handleGuestContinue}
            >
              Continue as Guest
            </button>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}
