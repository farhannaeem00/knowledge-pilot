"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col">
          <Topbar />
          <main className="flex-1 bg-background p-6">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  );
}