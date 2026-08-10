"use client";

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogPortal = DialogPrimitive.Portal;
const DialogClose = DialogPrimitive.Close;

type OverlayProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>;
type OverlayRef = React.ElementRef<typeof DialogPrimitive.Overlay>;

function DialogOverlayInner(props: OverlayProps, ref: React.ForwardedRef<OverlayRef>) {
  const { className, ...rest } = props;
  return (
    <DialogPrimitive.Overlay
      ref={ref}
      className={cn(
        "fixed inset-0 z-50 bg-black/50 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
        className
      )}
      {...rest}
    />
  );
}
const DialogOverlay = React.forwardRef(DialogOverlayInner);

type ContentProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>;
type ContentRef = React.ElementRef<typeof DialogPrimitive.Content>;

function DialogContentInner(props: ContentProps, ref: React.ForwardedRef<ContentRef>) {
  const { className, children, ...rest } = props;
  return (
    <DialogPortal>
      <DialogOverlay />
      <DialogPrimitive.Content
        ref={ref}
        className={cn(
          "fixed left-1/2 top-1/2 z-50 grid w-full max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 border bg-background p-6 shadow-lg duration-200 sm:rounded-lg",
          "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
          className
        )}
        {...rest}
      >
        {children}
        <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPortal>
  );
}
const DialogContent = React.forwardRef(DialogContentInner);

function DialogHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left", className)} {...props} />;
}

function DialogFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2", className)} {...props} />;
}

type TitleProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>;
type TitleRef = React.ElementRef<typeof DialogPrimitive.Title>;

function DialogTitleInner(props: TitleProps, ref: React.ForwardedRef<TitleRef>) {
  const { className, ...rest } = props;
  return <DialogPrimitive.Title ref={ref} className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...rest} />;
}
const DialogTitle = React.forwardRef(DialogTitleInner);

type DescProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>;
type DescRef = React.ElementRef<typeof DialogPrimitive.Description>;

function DialogDescriptionInner(props: DescProps, ref: React.ForwardedRef<DescRef>) {
  const { className, ...rest } = props;
  return <DialogPrimitive.Description ref={ref} className={cn("text-sm text-muted-foreground", className)} {...rest} />;
}
const DialogDescription = React.forwardRef(DialogDescriptionInner);

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
};