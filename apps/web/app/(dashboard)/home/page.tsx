"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { DndContext } from "@dnd-kit/core";
import WidgetDashboard from "@/components/WidgetDashboard";

function page() {
  const { user } = useUser();
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
