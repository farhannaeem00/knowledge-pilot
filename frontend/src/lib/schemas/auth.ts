/**
 * Zod schemas for auth forms. Rules mirror the backend's Pydantic
 * validation (password min length 8, matching RegisterRequest) so
 * invalid input is caught client-side before an API round-trip.
 */
import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  full_name: z.string().min(1, "Name is required").max(255),
  email: z.string().min(1, "Email is required").email("Enter a valid email"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password is too long"),
});
export type RegisterFormValues = z.infer<typeof registerSchema>;