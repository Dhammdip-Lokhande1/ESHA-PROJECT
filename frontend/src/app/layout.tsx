import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EHSA | Explainable Hybrid Similarity Analyzer",
  description: "Evidence-grounded code similarity investigation tool.",
};

import { AuthProvider } from "@/lib/auth";
import { Navbar } from "@/components/Navbar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <AuthProvider>
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
          
          <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500 mt-auto">
            EHSA Framework v1.0 &mdash; Explainable Hybrid Similarity Analyzer
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
