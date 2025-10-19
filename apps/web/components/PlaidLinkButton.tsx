"use client";

import React, { useState, useEffect } from "react";
import { usePlaidLink } from "react-plaid-link";
import { useAuth } from "@clerk/nextjs";

const PlaidLinkButton = () => {
  const { userId, isLoaded } = useAuth();
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
    
  // 1. Fetch the link_token from our server
  // A one-time token that launches the Plaid Link modal.
  useEffect(() => {
    const createLinkToken = async () => {
      try {
        const payload: { clerk_id?: string | null } = {};
        if (userId) {
          payload.clerk_id = userId;
        }
        
        const response = await fetch(`${apiUrl}/api/plaid/create_link_token`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          // Send the clerk_id to associate the token with the user.
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Failed to create link token");
        }

        const { link_token } = await response.json();
        setLinkToken(link_token);
      } catch (error) {
        console.error("Error creating link token:", error);
      }
    };

    if (isLoaded) {
      createLinkToken();
    }
  }, [userId, isLoaded]);

  // 2. Define the onSuccess callback
  // This function is called when the user successfully links their account.
  // It gives us a `public_token` that we must send to our backend.
  const onSuccess = React.useCallback(
    async (public_token: string) => {
      try {
        const payload: { public_token: string; clerk_id?: string | null } = { public_token};
        if (userId) {
          payload.clerk_id = userId;
        }

        // Send the public_token to backend to exchange for an access_token
        const response = await fetch(`${apiUrl}/api/plaid/exchange_public_token`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Failed to exchange public token");
        }
        window.location.reload(); 

      } catch (error) {
        console.error("Error exchanging public token:", error);
        return;
      }
    },
    [userId]
  );

  // 3. Configure and initialize the usePlaidLink hook
  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess,
  });

  return (
    <button onClick={() => open()} disabled={!ready || !linkToken}>
      Connect a Bank Account
    </button>
  );
};

export default PlaidLinkButton;
