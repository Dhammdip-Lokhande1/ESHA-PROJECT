"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Activity, Shield, LogOut, LogIn, UserPlus, Users } from "lucide-react";

const emptySubscribe = () => () => {};
function useIsMounted() {
  return React.useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  );
}

export function Navbar() {
  const { user, logout, isLoading } = useAuth();
  const mounted = useIsMounted();

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 sticky top-0 z-50 backdrop-blur-md">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="bg-blue-600 p-2 rounded-xl group-hover:bg-blue-500 transition-colors shadow-lg shadow-blue-500/20">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <span className="font-extrabold text-lg tracking-tight text-white">EHSA</span>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-slate-300">
          <Link href="/" className="hover:text-blue-400 transition-colors">Compare</Link>
          <Link href="/batch" className="hover:text-blue-400 transition-colors">Batch</Link>
          {mounted && !!user && (
            <Link href="/dashboard" className="hover:text-blue-400 transition-colors">My Dashboard</Link>
          )}
          {mounted && !!user && (
            <Link href="/history" className="hover:text-blue-400 transition-colors">History</Link>
          )}
          {mounted && !!user && (
            <Link href="/analytics" className="hover:text-emerald-400 transition-colors">Analytics</Link>
          )}
          {mounted && user?.role === "admin" && (
            <Link href="/admin" className="flex items-center gap-1.5 text-purple-400 hover:text-purple-300 transition-colors">
              <Users className="w-4 h-4" />
              Users
            </Link>
          )}
          <Link href="/benchmark" className="text-slate-400 hover:text-slate-200 transition-colors text-xs font-mono bg-slate-800/60 px-2.5 py-1 rounded-lg border border-slate-700/50">
            Benchmark
          </Link>
        </nav>

        {/* User Account Controls */}
        <div className="flex items-center gap-3">
          {!mounted || isLoading ? (
            <div className="w-20 h-8 bg-slate-800/50 rounded-xl animate-pulse" />
          ) : user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl">
                <Shield className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-semibold text-slate-200">{user.username}</span>
                <span
                  className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded-full font-bold border ${
                    user.role === "admin"
                      ? "bg-purple-500/10 text-purple-400 border-purple-500/20"
                      : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                  }`}
                >
                  {user.role}
                </span>
              </div>
              <button
                onClick={logout}
                title="Logout"
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl border border-transparent hover:border-red-500/20 transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl border border-slate-700 transition-all"
              >
                <LogIn className="w-3.5 h-3.5" />
                Login
              </Link>
              <Link
                href="/register"
                className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-xl shadow-md transition-all"
              >
                <UserPlus className="w-3.5 h-3.5" />
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
