import NavBar from "../../components/NavBar";
import React from "react";

function layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="h-screen w-full text-white">
      <NavBar />
      {children}
    </div>
  );
}

export default layout;
