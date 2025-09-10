import React from "react";
import Link from "next/link";
import { SignedIn, UserButton } from "@clerk/nextjs";

const NavBar = () => {
  return (
    <div className="flex">
      <div className="w-1/5"></div>
      <nav className="w-3/5 flex flex-row items-center h-10">
        <Link href={"/goals"} className="flex-1 text-center">
          Goals
        </Link>
        <Link href={"/budget"} className="flex-1 text-center">
          Budget
        </Link>
        <Link href={"/home"} className="flex-1 text-center">
          Home
        </Link>
        <Link href={"/transactions"} className="flex-1 text-center">
          Transactions
        </Link>
        <Link href={"/settings"} className="flex-1 text-center">
          Settings
        </Link>
      </nav>
      <div className="w-1/5 flex items-center">
        <SignedIn>
          <UserButton />
        </SignedIn>
      </div>
    </div>
  );
};

export default NavBar;
