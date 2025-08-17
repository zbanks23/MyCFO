"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { Transaction } from "../../app/(dashboard)/transactions/page";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface TransactionFormProps {
  transaction: Transaction | null; // Null if creating, object if editing
  onSuccess: () => void;
}

export const TransactionForm = React.forwardRef<
  HTMLFormElement,
  TransactionFormProps
>(({ transaction, onSuccess }, ref) => {
  const { userId } = useAuth();
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState("");
  const [category, setCategory] = useState("");

  // When the 'transaction' prop changes (i.e., when "Edit" is clicked),
  // populate the form with its data.
  useEffect(() => {
    if (transaction) {
      setName(transaction.name);
      setAmount(String(transaction.amount));
      // The date needs to be in YYYY-MM-DD format for the input type="date"
      setDate(new Date(transaction.date).toISOString().split("T")[0]!);
      setCategory(transaction.category);
    } else {
      // If creating a new one, reset the form
      setName("");
      setAmount("");
      setDate(new Date().toISOString().split("T")[0]!); // Default to today
      setCategory("");
    }
  }, [transaction]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) return;

    const isEditing = !!transaction;
    const url = isEditing
      ? `http://localhost:5001/api/transactions/${transaction.id}`
      : "http://localhost:5001/api/transactions";
    const method = isEditing ? "PUT" : "POST";

    const body = JSON.stringify({
      clerk_id: userId,
      name,
      amount: parseFloat(amount),
      date,
      category,
    });

    try {
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body,
      });

      if (!response.ok) {
        throw new Error("Failed to save transaction");
      }

      onSuccess(); // Tell the parent component we are done
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <form ref={ref} onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="name">Name</Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="amount">Amount</Label>
        <Input
          id="amount"
          type="number"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="date">Date</Label>
        <Input
          id="date"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="category">Category</Label>
        <Input
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
      </div>
      <div className="flex justify-end">
        <Button type="submit">
          {transaction ? "Save Changes" : "Create Transaction"}
        </Button>
      </div>
    </form>
  );
});

TransactionForm.displayName = "TransactionForm";
