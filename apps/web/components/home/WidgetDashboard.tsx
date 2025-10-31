"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
} from "@dnd-kit/core";
import { useAuth } from "@clerk/nextjs";

const CurrentCheckingAccountBalance = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
    const { userId } = useAuth();

    const getCurrentCheckingAccountBalance = async () => {
        const response = await fetch(`${apiUrl}/api/plaid/retrieve_checking_account_balance?clerk_id=${userId}`, {
        method: "GET",
        credentials: "include",
        });
        const data = await response.json();
        return data.checking_account_balance;
    }
    const [checkingBalance, setCheckingBalance] = useState<number | null>(null);
    useEffect(() => {
        const fetchBalance = async () => {
            const balance = await getCurrentCheckingAccountBalance();
            setCheckingBalance(balance);
        };
        fetchBalance();
    }, []);
    return (
        <div>
            Current Checking Account Balance: {checkingBalance !== null ? `$${checkingBalance}` : "Loading..."}
        </div>
    )
}

const CurrentAvailableBalance = () => {
    return (
    <div>Current Available Balance</div>
  )
}

const CurrentSavingsAccountBalance = () => {
    return (
    <div>Current Savings Account Balance</div>
  )
}

const CurrentInvestmentAccountBalance = () => {
    return (
    <div>Current Investment Account Balance</div>
  )
}

const TotalNetWorth = () => {
    return (
    <div>Total Net Worth</div>
  )
}

const TotalLiabilities = () => {
    return (
    <div>Total Liabilities</div>
  )
}

const TotalAssets = () => {
    return (
    <div>Total Assets</div>
  )
}

const WidgetDashboard: React.FC = () => {
  return (
    <div className="grid h-screen xl:w-full text-center gap-4 grid-cols-4 grid-rows-3 p-8">
      <div className="rounded-lg bg-gray-700 p-4">
        Total Net Worth: $1,000,000
      </div>
      <div className="col-span-2 rounded-lg bg-gray-700 p-4">
        <CurrentCheckingAccountBalance />
      </div>
      <div className="row-span-2 rounded-lg bg-gray-700 p-4">
        Budget Bar Chart
        <ul>
          <li>Rent & Utilities: $1000</li>
          <li>Groceries: $300</li>
          <li>Transportation: $300</li>
          <li>Subscription: $50</li>
          <li>Dinning: $200</li>
          <li>Miscellaneous: $150</li>
        </ul>
      </div>
      <div className="col-span-2 row-span-2 rounded-lg bg-gray-700 p-4">
        Expenses Pie Chart
      </div>
      <div className="rounded-lg bg-gray-700 p-4">Income Sources bar chart</div>
      <div className="rounded-lg bg-gray-700 p-4">Stock Watchlist</div>
      <div className="rounded-lg bg-gray-700 p-4">Savings Goal</div>
    </div>
  );
};

export default WidgetDashboard;
