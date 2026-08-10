"use client";

/**
 * Client-side route guard. Auth state lives in localStorage (no
 * cookies), so Next.js edge middleware can't see it - this component is
 * the correct place to enforce "must be logged in" for a client-heavy
 * app like this one, not a workaround.
 *
 * On mount, re-validates against /auth/me rather than trusting the
 * persisted store blindly - catches the case where a token expired
 * while the tab was closed.
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient, getAccessToken } from "@/lib/api-client";
import { useAuthStore } from "@/store/auth-store";
import type { User } from "@/types/api";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const [status, setStatus] = useState<"checking" | "ok" | "redirecting">("checking");

  useEffect(() => {
    let cancelled = false;

    async function verify() {
      const token = getAccessToken();
      if (!token) {
        if (!cancelled) {
          setStatus("redirecting");
          router.replace("/login");
        }
        return;
      }
      try {
        const user = await apiClient.get<User>("/auth/me");
        if (!cancelled) {
          setUser(user);
          setStatus("ok");
        }
      } catch {
        if (!cancelled) {
          setStatus("redirecting");
          router.replace("/login");
        }
      }
    }

    verify();
    return () => {
      cancelled = true;
    };
  }, [router, setUser]);

  if (status !== "ok") {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Loading...
      </div>
    );
  }

  return <>{children}</>;
}