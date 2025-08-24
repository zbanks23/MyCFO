import { SignedIn, UserProfile } from "@clerk/nextjs";
import React from "react";

const page = () => {
  return (
    <>
      <SignedIn>
        <UserProfile />
      </SignedIn>
    </>
  );
};

export default page;
