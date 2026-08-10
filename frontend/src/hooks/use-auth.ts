/**
 * Auth actions as React Query mutations. Each mutation handles the full
 * flow: API call -> store tokens -> fetch /auth/me -> update auth store.
 * Pages call these hooks rather than touching apiClient/authStore
 * directly, keeping the auth flow in one place.
 */
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiClient, clearTokens, setTokens } from "@/lib/api-client";
import { useAuthStore } from "@/store/auth-store";
import type { LoginFormValues, RegisterFormValues } from "@/lib/schemas/auth";
import type { TokenResponse, User } from "@/types/api";

export function useLogin() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (values: LoginFormValues) => {
      const tokens = await apiClient.post<TokenResponse>("/auth/login", values);
      setTokens(tokens);
      const user = await apiClient.get<User>("/auth/me");
      return user;
    },
    onSuccess: (user) => {
      setUser(user);
      queryClient.invalidateQueries();
      router.push("/dashboard");
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: async (values: RegisterFormValues) => {
      return apiClient.post<User>("/auth/register", values);
    },
    onSuccess: () => {
      router.push("/login?registered=true");
    },
  });
}

export function useLogout() {
  const router = useRouter();
  const logout = useAuthStore((s) => s.logout);
  const queryClient = useQueryClient();

  return () => {
    clearTokens();
    logout();
    queryClient.clear();
    router.push("/login");
  };
}