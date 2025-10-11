"use client";

import React, { useState, useEffect } from "react";
import { usePlaidLink } from "react-plaid-link";
import { useAuth } from "@clerk/nextjs";

const PlaidLinkButton = () => {
  const { userId } = useAuth();
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";

  // 1. Fetch the link_token from our server
  // A one-time token that launches the Plaid Link modal.
  useEffect(() => {
    const createLinkToken = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/plaid/create_link_token`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          // Send the clerk_id to associate the token with the user.
          body: JSON.stringify({ clerk_id: userId }),
        });
        const { link_token } = await response.json();
        setLinkToken(link_token);
      } catch (error) {
        console.error("Error creating link token:", error);
      }
    };
    if (userId) {
      createLinkToken();
    }
  }, [userId]);

  // 2. Define the onSuccess callback
  // This function is called when the user successfully links their account.
  // It gives us a `public_token` that we must send to our backend.
  const onSuccess = React.useCallback(
    async (public_token: string) => {
      // Send the public_token to your server to exchange for an access_token
      await fetch(`${apiUrl}/api/plaid/exchange_public_token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ public_token, clerk_id: userId }),
      });
      window.location.reload();
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
