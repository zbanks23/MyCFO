"use client";

import { useState, useEffect } from "react";
import { useUser, useAuth } from "@clerk/nextjs";
import { DndContext } from "@dnd-kit/core";
import WidgetDashboard from "@/components/home/WidgetDashboard";

function page() {
  const { user } = useUser();
  const { userId } = useAuth();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

  useEffect(() => {
    const getStatus = async () => {
      try {
        const statusResponse = await fetch(`${apiUrl}/api/core/status`, {credentials: "include",});
        if (!statusResponse.ok) {
          throw new Error("Network response was not ok");
        }
        const statusData = await statusResponse.json();
        console.log(statusData.message);

        const sessionResponse = await fetch(`${apiUrl}/api/core/session_test?clerk_id=${userId}`, {credentials: "include",});
        if (!sessionResponse.ok) {
          // throw new Error("Network response was not ok");
        }
        const sessionData = await sessionResponse.json();
        console.log(sessionData.message);

      } catch (error) {
        console.error("Failed to fetch API status:", error);
        console.log("Failed to connect to API");
      }
    };

    getStatus();
  }, []);

  const firstName = user?.firstName ?? "Guest";

  return (
    <section className="flex flex-col w-full h-full items-center">
      <div>
        <p>Welcome to your dashboard, {firstName}!</p>
      </div>
      <WidgetDashboard />
    </section>
  );
}

export default page;
