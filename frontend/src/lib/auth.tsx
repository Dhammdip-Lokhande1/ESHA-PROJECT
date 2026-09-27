"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, fetchMeApi, loginApi, registerApi } from "./api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("ehsa_auth_token") : null
  );
  const [isLoading, setIsLoading] = useState<boolean>(() =>
    typeof window !== "undefined" && Boolean(localStorage.getItem("ehsa_auth_token"))
  );

  useEffect(() => {
    const storedToken = localStorage.getItem("ehsa_auth_token");
    if (!storedToken) return;

    let isMounted = true;
    fetchMeApi()
      .then((userData) => {
        if (isMounted) setUser(userData);
      })
      .catch(() => {
        if (isMounted) {
          localStorage.removeItem("ehsa_auth_token");
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (username: string, password: string) => {
    const data = await loginApi(username, password);
    localStorage.setItem("ehsa_auth_token", data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  };

  const register = async (username: string, email: string, password: string) => {
    await registerApi(username, email, password);
    // Automatically log in after registration
    await login(username, password);
  };

  const logout = () => {
    localStorage.removeItem("ehsa_auth_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
