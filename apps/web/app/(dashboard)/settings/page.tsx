"use client";

import PlaidLinkButton from "@/components/PlaidLinkButton";
import React, {useState, useEffect, useCallback} from "react";
import { useAuth } from "@clerk/nextjs";
import AccountsTable from "../../../components/settings/AccountsTable";

export interface Account {
  bank_account_id: string;
  item_id: string;
  user_id: string;
  mask: string;
  name: string;
  official_name: string;
  available_balance: number | null;
  current_balance: number | null;
  balance_limit: number | null;
  type: string;
  subtype: string;
}

export default function AccountsPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
  const { userId, isLoaded } = useAuth();
  const [accounts, setAccounts] = useState<Account[]>([]);

  const fetchAccounts = useCallback(async () => {
    if (!isLoaded) return;
    console.log("Fetching linked accounts for user:", userId);
    try {
      const response = await fetch(`${apiUrl}/api/plaid/retrieve_bank_account_info?clerk_id=${userId}`, {credentials: "include",});
      if (!response.ok) {
        throw new Error("Failed to fetch linked accounts");
      }
      const data = await response.json();
      console.log("Retrieved linked accounts:", data);
      setAccounts(data);
    } catch (error) {
      console.error("Error retrieving linked accounts:", error);
    }
  }, [userId, isLoaded]);
  
  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  return (
    <>
      <div>
        <PlaidLinkButton />
      </div>
      <div>
        <AccountsTable accounts={accounts} />
      </div>
    </>
  );
};