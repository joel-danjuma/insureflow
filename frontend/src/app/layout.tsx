import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/components/providers/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "InsureFlow",
  description: "Insurance Management Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          {/* The main layout component is not used here to prevent a nested layout, 
              as the dashboard pages will use it directly. This keeps the login page separate. */}
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
