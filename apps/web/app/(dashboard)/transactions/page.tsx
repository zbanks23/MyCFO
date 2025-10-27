"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";

import TransactionTable from "../../../components/transactions/TransactionTable";

// Define a type for our transaction object for better code safety
export interface Transaction {
  id: string;
  date: string;
  name: string;
  amount: number;
  category: string;
  note: string | null;
}

export default function TransactionsPage() {
  const { userId } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

  const fetchTransactions = useCallback(async () => {
    if (!userId) return;
    try {
      const response = await fetch(`${apiUrl}/api/transactions?clerk_id=${userId}`);
      const data = await response.json();
      setTransactions(data);
    } catch (error) {
      console.error("Failed to fetch transactions:", error);
    }
  }, [userId]);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Transactions</h1>
      </div>

      <TransactionTable transactions={transactions} />
    </div>
  );
}
