import NavBar from "@repo/ui/components/NavBar";
import React from "react";

function layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="bg-gray-900 h-screen w-full text-white">
      <div className="absolute w-2/3 flex justify-center translate-x-1/4">
        <NavBar />
      </div>
      {children}
    </div>
  );
}

export default layout;
