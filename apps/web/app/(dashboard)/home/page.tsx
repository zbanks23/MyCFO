"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { DndContext } from "@dnd-kit/core";
import WidgetDashboard from "@/components/WidgetDashboard";

function page() {
  const { user } = useUser();
  const [syncStatus, setSyncStatus] = useState("");
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

  useEffect(() => {
    const getApiStatus = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/status`);
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        console.log(data.message);
      } catch (error) {
        console.error("Failed to fetch API status:", error);
        console.log("Failed to connect to API");
      }
    };

    getApiStatus();
  }, []);

  const handleSyncUser = async () => {
    if (!user) return;

    console.log("Data being sent to backend:", user);
    setSyncStatus("Syncing...");
    try {
      const response = await fetch(`${apiUrl}/api/sync_user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(user),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to sync user");
      }
      setSyncStatus(`Sync successful: ${data.message}`);
    } catch (error: any) {
      console.error("Sync failed:", error);
      setSyncStatus(`Sync failed: ${error.message}`);
    }
  };

  if (!user) return null;

  return (
    <section className="flex flex-col w-full h-full items-center">
      <div>
        <p>Welcome to your dashboard, {user.firstName}!</p>
      </div>
      <div className="mt-8">
        <button
          onClick={handleSyncUser}
          className="px-4 py-2 bg-green-500 text-white font-semibold rounded-md hover:bg-green-600"
        >
          Sync My User Data to DB
        </button>
        <p className="mt-2 text-sm text-gray-600">
          Status: <span className="font-medium">{syncStatus}</span>
        </p>
      </div>
      <WidgetDashboard />
    </section>
  );
}

export default page;
