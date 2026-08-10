"use client";

import * as React from "react";
import * as AvatarPrimitive from "@radix-ui/react-avatar";
import { cn } from "@/lib/utils";

type AvatarProps = React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root>;
type AvatarRef = React.ElementRef<typeof AvatarPrimitive.Root>;

function AvatarInner(props: AvatarProps, ref: React.ForwardedRef<AvatarRef>) {
  const { className, ...rest } = props;
  return <AvatarPrimitive.Root ref={ref} className={cn("relative flex h-9 w-9 shrink-0 overflow-hidden rounded-full", className)} {...rest} />;
}
const Avatar = React.forwardRef(AvatarInner);

type AvatarImageProps = React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image>;
type AvatarImageRef = React.ElementRef<typeof AvatarPrimitive.Image>;

function AvatarImageInner(props: AvatarImageProps, ref: React.ForwardedRef<AvatarImageRef>) {
  const { className, ...rest } = props;
  return <AvatarPrimitive.Image ref={ref} className={cn("aspect-square h-full w-full", className)} {...rest} />;
}
const AvatarImage = React.forwardRef(AvatarImageInner);

type AvatarFallbackProps = React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>;
type AvatarFallbackRef = React.ElementRef<typeof AvatarPrimitive.Fallback>;

function AvatarFallbackInner(props: AvatarFallbackProps, ref: React.ForwardedRef<AvatarFallbackRef>) {
  const { className, ...rest } = props;
  return (
    <AvatarPrimitive.Fallback
      ref={ref}
      className={cn("flex h-full w-full items-center justify-center rounded-full bg-muted text-sm font-medium", className)}
      {...rest}
    />
  );
}
const AvatarFallback = React.forwardRef(AvatarFallbackInner);

export { Avatar, AvatarImage, AvatarFallback };