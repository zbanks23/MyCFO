"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";

function page() {
  const { user } = useUser();
  const [apiMessage, setApiMessage] = useState("");
  const [syncStatus, setSyncStatus] = useState("");

  useEffect(() => {
    const getApiStatus = async () => {
      try {
        const response = await fetch("http://localhost:5001/api/status");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setApiMessage(data.message);
      } catch (error) {
        console.error("Failed to fetch API status:", error);
        setApiMessage("Failed to connect to API");
      }
    };

    getApiStatus();
  }, []);

  const handleSyncUser = async () => {
    if (!user) return;

    console.log("Data being sent to backend:", user);
    setSyncStatus("Syncing...");
    try {
      const response = await fetch("http://localhost:5001/api/sync_user", {
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
        <p>API Status: {apiMessage}</p>
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
      <div>Total Balance: $100,000</div>
      <div className="grid grid-cols-3 grid-rows-2 h-full w-full text-center">
        <div>Total Net Worth: $1,000,000</div>
        <div>Income vs Expenses line chart</div>
        <div>
          Spending Categories
          <ul>
            <li>Rent & Utilities: $1000</li>
            <li>Groceries: $300</li>
            <li>Transportation: $300</li>
            <li>Subscription: $50</li>
            <li>Dinning: $200</li>
            <li>Miscellaneous: $150</li>
          </ul>
        </div>
        <div>Income Sources bar chart</div>
        <div>Asset Pie Chart</div>
        <div>Savings Goal</div>
      </div>
    </section>
  );
}

export default page;
