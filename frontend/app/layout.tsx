import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "../components/navbar";

export const metadata: Metadata = {
  title: "RiskLens — AI Transaction Risk Intelligence",
  description: "Defense-only AI risk intelligence for merchants.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="page-shell">
      <Navbar />
      {children}
    </div>
  );
}
