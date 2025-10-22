"use client";

import React from "react";
import { Account } from "../../app/(dashboard)/settings/page"; // Import the type

interface AccountsTableProps {
  accounts: Account[];
}

const AccountsTable: React.FC<AccountsTableProps> = ({ accounts }) => {
    
    return (<div className="w-full rounded-lg border relative max-h-[70vh] overflow-y-auto">
      <table className="w-full text-left table-fixed">
        <thead className="bg-gray-800 sticky top-0 z-10">
          <tr>
            <th className="p-4">Name</th>
            <th className="p-4">Type</th>
            <th className="p-4">Sub Type</th>
            <th className="p-4">Available Amount</th>
            <th className="p-4">Current Amount</th>
            <th className="p-4">Mask</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((tx) => (
            <tr key={tx.id} className="border-t">
                <td className="p-4">{tx.name}</td>
                <td className="p-4">{tx.type}</td>
                <td className="p-4 text-right">{tx.subtype}</td>
                <td className="p-4 text-right">{tx.available_balance !== null ? `$${tx.available_balance.toFixed(2)}` : 'N/A'}</td>
                <td className="p-4 text-right">{tx.current_balance !== null ? `$${tx.current_balance.toFixed(2)}` : 'N/A'}</td>
                <td className="p-4">{tx.mask}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>)
};

export default AccountsTable;