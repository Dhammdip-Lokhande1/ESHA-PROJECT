"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { User, listAdminUsersApi, updateAdminUserApi } from "@/lib/api";
import { Users, Shield, CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react";

export default function AdminPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAdminUsersApi();
      setUsers(data);
    } catch (err: unknown) {
      if (typeof err === "object" && err !== null && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || "Failed to load user list.");
      } else {
        setError("Network error while loading users.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser?.role !== "admin") return;
    let isMounted = true;
    listAdminUsersApi()
      .then((data) => {
        if (isMounted) {
          setUsers(data);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          if (typeof err === "object" && err !== null && "response" in err) {
            const axiosErr = err as { response?: { data?: { detail?: string } } };
            setError(axiosErr.response?.data?.detail || "Failed to load user list.");
          } else {
            setError("Network error while loading users.");
          }
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [currentUser]);

  const handleRoleChange = async (userId: string, newRole: string) => {
    setUpdatingId(userId);
    try {
      const updated = await updateAdminUserApi(userId, { role: newRole });
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (err: unknown) {
      if (typeof err === "object" && err !== null && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        alert(axiosErr.response?.data?.detail || "Role update failed.");
      }
    } finally {
      setUpdatingId(null);
    }
  };

  const handleStatusToggle = async (userId: string, currentStatus: boolean) => {
    setUpdatingId(userId);
    try {
      const updated = await updateAdminUserApi(userId, { is_active: !currentStatus });
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (err: unknown) {
      if (typeof err === "object" && err !== null && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        alert(axiosErr.response?.data?.detail || "Status update failed.");
      }
    } finally {
      setUpdatingId(null);
    }
  };

  if (currentUser?.role !== "admin") {
    return (
      <main className="min-h-[80vh] flex items-center justify-center p-6 bg-slate-950 text-slate-100">
        <div className="max-w-md w-full text-center p-8 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
          <p className="text-sm text-slate-400">
            You must be logged in as an Administrator to view user management.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-slate-100">
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <Users className="h-8 w-8 text-blue-400" />
            <h1 className="text-3xl font-extrabold text-white">User Management</h1>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Manage system users, assign RBAC roles, and control account activation status.
          </p>
        </div>
        <button
          onClick={loadUsers}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-sm font-semibold text-slate-200 border border-slate-700 transition-all"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-12 text-center text-slate-400">Loading users...</div>
      ) : (
        <div className="overflow-x-auto bg-slate-900/80 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur-md">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-xs tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-4 px-6">User</th>
                <th className="py-4 px-6">Email</th>
                <th className="py-4 px-6">Role</th>
                <th className="py-4 px-6">Status</th>
                <th className="py-4 px-6">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-850 transition-colors">
                  <td className="py-4 px-6 font-semibold text-white">
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-blue-400" />
                      {u.username}
                      {u.id === currentUser.id && (
                        <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full font-mono">
                          YOU
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-4 px-6 text-slate-400">{u.email}</td>
                  <td className="py-4 px-6">
                    <select
                      value={u.role}
                      disabled={updatingId === u.id || u.id === currentUser.id}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td className="py-4 px-6">
                    {u.is_active ? (
                      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
                        <CheckCircle className="h-3.5 w-3.5" />
                        Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-red-400 bg-red-500/10 border border-red-500/20 px-2.5 py-1 rounded-full">
                        <XCircle className="h-3.5 w-3.5" />
                        Inactive
                      </span>
                    )}
                  </td>
                  <td className="py-4 px-6">
                    <button
                      onClick={() => handleStatusToggle(u.id, u.is_active)}
                      disabled={updatingId === u.id || u.id === currentUser.id}
                      className={`text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all ${
                        u.is_active
                          ? "bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20"
                          : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20"
                      } disabled:opacity-40`}
                    >
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
