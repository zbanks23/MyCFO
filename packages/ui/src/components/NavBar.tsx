import React from "react";
import Link from "next/link";

const NavBar = () => {
  return (
    <>
      <nav className="w-2/3 flex flex-row justify-center h-10">
        <Link href={"/budget"} className="flex-1 text-center">
          Budget
        </Link>
        <Link href={"/home"} className="flex-1 text-center">
          Home
        </Link>
        <Link href={"/spending"} className="flex-1 text-center">
          Spending
        </Link>
        <Link href={"/profile"} className="flex-1 text-center">
          Profile
        </Link>
      </nav>
    </>
  );
};

export default NavBar;
