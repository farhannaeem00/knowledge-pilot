/**
 * TypeScript types mirroring the backend's Pydantic response schemas.
 * Kept as plain interfaces (not generated/shared) for now - hand-synced
 * with backend/app/presentation/api/v1/schemas/*.py. Revisit codegen
 * (e.g. openapi-typescript against /openapi.json) later if drift becomes
 * a real problem; not worth the setup cost at this stage.
 */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: string;
  is_email_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Workspace {
  id: string;
  owner_id: string;
  name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  version_number: number;
  is_current: boolean;
  original_filename: string | null;
  content_type: string | null;
  size_bytes: number;
  status: string;
  error_message: string | null;
  chunk_count: number | null;
  created_at: string;
}

export interface Document {
  id: string;
  workspace_id: string;
  folder_id: string | null;
  title: string;
  source_type: string;
  tags: string[] | null;
  is_favorite: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentWithVersions extends Document {
  versions: DocumentVersion[];
}

export interface SummaryContent {
  overview: string;
  executive_summary: string;
  key_ideas: string[];
  section_summary: { title: string; summary: string }[];
  important_concepts: string[];
  important_statistics: string[];
  examples: string[];
  pros: string[];
  cons: string[];
  actionable_insights: string[];
  key_takeaways: string[];
  conclusion: string;
  reading_time_minutes: number;
  difficulty_level: string;
  confidence_score: number;
}

export interface Summary {
  id: string;
  version_id: string;
  style: string;
  status: string;
  error_message: string | null;
  content_json: SummaryContent | null;
  is_active: boolean;
  model_used: string | null;
  created_at: string;
}

export interface ChatThread {
  id: string;
  workspace_id: string;
  document_id: string;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  thread_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Note {
  id: string;
  workspace_id: string;
  document_id: string | null;
  title: string;
  content_md: string;
  tags: string[] | null;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface Highlight {
  id: string;
  version_id: string;
  level: "must_read" | "important" | "optional" | "custom";
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note: string | null;
  created_at: string;
}

export interface ScriptContent {
  hook: string;
  introduction: string;
  body: string[];
  examples: string[];
  cta: string;
  estimated_duration_seconds: number;
}

export interface Script {
  id: string;
  workspace_id: string;
  document_id: string;
  platform: string;
  status: string;
  error_message: string | null;
  content_json: ScriptContent | null;
  model_used: string | null;
  created_at: string;
}

export interface Notification {
  id: string;
  type: string;
  payload: Record<string, unknown> | null;
  read_at: string | null;
  created_at: string;
}

export interface ApiError {
  error_code: string;
  message: string;
}