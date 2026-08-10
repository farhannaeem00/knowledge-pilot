import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Standard shadcn/ui class-merging helper. Every component we add via
 * the shadcn CLI in later steps expects this exact function to exist
 * at this exact path.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}