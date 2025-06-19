import type { Metadata } from "next";
import { Public_Sans, Noto_Sans } from "next/font/google";
import "./globals.css";

const publicSans = Public_Sans({ 
  subsets: ["latin"],
  variable: "--font-public-sans",
  weight: ["400", "500", "700", "900"]
});

const notoSans = Noto_Sans({ 
  subsets: ["latin"],
  variable: "--font-noto-sans",
  weight: ["400", "500", "700", "900"]
});

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
      <body className={`${publicSans.variable} ${notoSans.variable}`} style={{fontFamily: '"Public Sans", "Noto Sans", sans-serif'}}>
        {/* The main layout component is not used here to prevent a nested layout, 
            as the dashboard pages will use it directly. This keeps the login page separate. */}
        {children}
      </body>
    </html>
  );
}
