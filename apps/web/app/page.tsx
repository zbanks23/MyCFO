"use client";

import { SignInButton, SignUpButton, SignedOut, useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function RootPage() {
  const { userId } = useAuth();
  const router = useRouter();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

  const handleSyncUser = async () => {
    console.log("Data being sent to backend:", userId);
    try {
      const response = await fetch(`${apiUrl}/api/sync_user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userId),
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

  const handleGuestContinue = () => {
    router.push("/home");
  };

  useEffect(() => {
    if (userId) {
      router.push("/home");
      handleSyncUser();
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
