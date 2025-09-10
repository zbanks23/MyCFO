"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@clerk/nextjs";

import TransactionTable from "../../../components/transactions/TransactionTable";
import { TransactionForm } from "../../../components/transactions/TransactionForm";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

// Define a type for our transaction object for better code safety
export interface Transaction {
  id: string;
  date: string;
  name: string;
  amount: number;
  category: string;
}

export default function TransactionsPage() {
  const { userId } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] =
    useState<Transaction | null>(null);

  // Function to fetch transactions from our API
  const fetchTransactions = useCallback(async () => {
    if (!userId) return;
    try {
      const response = await fetch(
        `http://localhost:5001/api/transactions?clerk_id=${userId}`
      );
      const data = await response.json();
      setTransactions(data);
    } catch (error) {
      console.error("Failed to fetch transactions:", error);
    }
  }, [userId]);

  // Fetch transactions when the component mounts or userId changes
  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  // Handler to open the dialog for editing an existing transaction
  const handleEdit = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setIsDialogOpen(true);
  };

  // Handler to open the dialog for creating a new transaction
  const handleAddNew = () => {
    setEditingTransaction(null); // Clear any previous edit state
    setIsDialogOpen(true);
  };

  // Handler for when the form submission is successful
  const handleSuccess = () => {
    setIsDialogOpen(false); // Close the dialog
    setEditingTransaction(null); // Reset the editing state
    fetchTransactions(); // Re-fetch the data to show the latest changes
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Transactions</h1>
        <Button onClick={handleAddNew}>Add New Transaction</Button>
      </div>

      <TransactionTable
        transactions={transactions}
        onEdit={handleEdit}
        onDelete={fetchTransactions} // Re-fetch data after a delete
      />

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingTransaction ? "Edit Transaction" : "Add New Transaction"}
            </DialogTitle>
            <DialogDescription>
              Enter the details of your transaction in the form. Click Submit
              when you're done.
            </DialogDescription>
          </DialogHeader>
          <TransactionForm
            transaction={editingTransaction}
            onSuccess={handleSuccess}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
