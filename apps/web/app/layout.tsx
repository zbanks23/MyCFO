// File: apps/web/app/layout.tsx

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ClerkProvider, UserButton, SignedIn } from "@clerk/nextjs";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MyCFO",
  description: "A personal finance tracker developed by Zhicheng",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          <header>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </header>
          <div className="bg-gray-950">{children}</div>
        </body>
      </html>
    </ClerkProvider>
  );
}
