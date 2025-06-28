"use client";

import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";

function page() {
  const { user } = useUser();
  const [apiMessage, setApiMessage] = useState("");

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

  if (!user) return null;

  return (
    <section className="flex flex-col w-full h-full items-center">
      <div>
        <p>Welcome to your dashboard, {user.firstName}!</p>
        <p>API Status: {apiMessage}</p>
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
