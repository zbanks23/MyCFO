"use client";

import React, { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { Transaction } from "../../app/(dashboard)/transactions/page"; // Import the type

interface TransactionTableProps {
  transactions: Transaction[];
}

const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
}) => {
  const { userId } = useAuth();
  const [notes, setNotes] = useState<string>("");

  const handleEnter = async (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (event.key !== "Enter" || event.shiftKey) return; // Only proceed on Enter without Shift

    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault(); // Prevent newline insertion
    }

    const textToSave = notes.trim();
    if (!textToSave) {
      // FIXME: Add user feedback for empty notes
    }

    try {
      const response = await fetch(
        `http://localhost:5001/api/transactions/note/${event.currentTarget.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            clerk_id: userId,
            note: textToSave,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update transaction note");
      }

      const result = await response.json();
      console.log("Transaction note updated:", result);
      setNotes(""); // Clear the textarea after successful save
    } catch (error) {
      console.error("Failed to update transaction note:", error);
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
            <th className="p-4 text-center">Note</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id} className="border-t">
              <td className="p-4">{new Date(tx.date).toLocaleDateString()}</td>
              <td className="p-4">{tx.name}</td>
              <td className="p-4">{tx.category}</td>
              <td className="p-4 text-right">${tx.amount.toFixed(2)}</td>
              <td className="p-4">
                <textarea
                  id={tx.id}
                  defaultValue={tx.note ?? ""}
                  onChange={(e) => setNotes(e.target.value)}
                  onKeyDown={handleEnter}
                  className="text-center"
                ></textarea>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TransactionTable;
