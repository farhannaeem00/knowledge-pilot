/**
 * Admin hooks. All calls require role="admin" server-side (require_admin
 * dependency) - a non-admin gets a real 403 from the API even if they
 * reach these pages directly, not just a hidden UI link.
 */
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

export interface AdminUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
}

export interface AdminDocument {
  id: string;
  workspace_id: string;
  title: string;
  source_type: string;
  status: string;
  created_at: string;
}

export interface StorageStats {
  total_documents: number;
  total_versions: number;
  total_size_bytes: number;
}

export interface AIUsageSummary {
  total_calls: number;
  total_tokens_in: number;
  total_tokens_out: number;
  avg_latency_ms: number;
}

export interface AIUsageByFeature {
  feature: string;
  count: number;
}

export function useAdminUsers() {
  return useQuery({
    queryKey: ["admin-users"],
    queryFn: () => apiClient.get<AdminUser[]>("/admin/users"),
  });
}

export function useAdminDocuments() {
  return useQuery({
    queryKey: ["admin-documents"],
    queryFn: () => apiClient.get<AdminDocument[]>("/admin/documents"),
  });
}

export function useStorageStats() {
  return useQuery({
    queryKey: ["admin-storage"],
    queryFn: () => apiClient.get<StorageStats>("/admin/storage"),
  });
}

export function useAIUsageSummary() {
  return useQuery({
    queryKey: ["admin-ai-usage-summary"],
    queryFn: () => apiClient.get<AIUsageSummary>("/admin/ai-usage/summary"),
  });
}

export function useAIUsageByFeature() {
  return useQuery({
    queryKey: ["admin-ai-usage-by-feature"],
    queryFn: () => apiClient.get<AIUsageByFeature[]>("/admin/ai-usage/by-feature"),
  });
}