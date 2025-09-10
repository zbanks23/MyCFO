"use client";

import React from "react";
import { useAuth } from "@clerk/nextjs";
import { Transaction } from "../../app/(dashboard)/transactions/page"; // Import the type
import { Button } from "@/components/ui/button";

interface TransactionTableProps {
  transactions: Transaction[];
  onEdit: (transaction: Transaction) => void;
  onDelete: () => void; // A function to be called after deleting
}

const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  onEdit,
  onDelete,
}) => {
  const { userId } = useAuth();

  const handleDelete = async (transactionId: string) => {
    if (
      !userId ||
      !confirm("Are you sure you want to delete this transaction?")
    ) {
      return;
    }

    try {
      await fetch(
        `http://localhost:5001/api/transactions/${transactionId}?clerk_id=${userId}`,
        {
          method: "DELETE",
        }
      );
      onDelete(); // Notify the parent component to re-fetch data
    } catch (error) {
      console.error("Failed to delete transaction:", error);
    }
  };

  return (
    <div className="w-full rounded-lg border relative max-h-[70vh] overflow-y-auto">
      <table className="w-full text-left table-fixed">
        <thead className="bg-gray-800 sticky top-0 z-10">
          <tr>
            <th className="p-4">Date</th>
            <th className="p-4">Name</th>
            <th className="p-4">Category</th>
            <th className="p-4 text-right">Amount</th>
            <th className="p-4">Actions</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id} className="border-t">
              <td className="p-4">{new Date(tx.date).toLocaleDateString()}</td>
              <td className="p-4">{tx.name}</td>
              <td className="p-4">{tx.category}</td>
              <td className="p-4 text-right">${tx.amount.toFixed(2)}</td>
              <td className="p-4 flex gap-2">
                <Button variant="default" size="sm" onClick={() => onEdit(tx)}>
                  Edit
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDelete(tx.id)}
                >
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TransactionTable;
