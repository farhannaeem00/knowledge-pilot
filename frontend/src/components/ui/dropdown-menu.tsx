"use client";

import * as React from "react";
import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import { cn } from "@/lib/utils";

const DropdownMenu = DropdownMenuPrimitive.Root;
const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;
const DropdownMenuGroup = DropdownMenuPrimitive.Group;
const DropdownMenuPortal = DropdownMenuPrimitive.Portal;
const DropdownMenuSub = DropdownMenuPrimitive.Sub;
const DropdownMenuRadioGroup = DropdownMenuPrimitive.RadioGroup;

type ContentProps = React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content>;
type ContentRef = React.ElementRef<typeof DropdownMenuPrimitive.Content>;

function DropdownMenuContentInner(props: ContentProps, ref: React.ForwardedRef<ContentRef>) {
  const { className, sideOffset = 4, ...rest } = props;
  return (
    <DropdownMenuPrimitive.Portal>
      <DropdownMenuPrimitive.Content
        ref={ref}
        sideOffset={sideOffset}
        className={cn(
          "z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
          "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
          className
        )}
        style={{ backgroundColor: "hsl(var(--card))" }}
        {...rest}
      />
    </DropdownMenuPrimitive.Portal>
  );
}
const DropdownMenuContent = React.forwardRef(DropdownMenuContentInner);

type ItemProps = React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item> & { inset?: boolean };
type ItemRef = React.ElementRef<typeof DropdownMenuPrimitive.Item>;

function DropdownMenuItemInner(props: ItemProps, ref: React.ForwardedRef<ItemRef>) {
  const { className, inset, ...rest } = props;
  return (
    <DropdownMenuPrimitive.Item
      ref={ref}
      className={cn(
        "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        inset && "pl-8",
        className
      )}
      {...rest}
    />
  );
}
const DropdownMenuItem = React.forwardRef(DropdownMenuItemInner);

type LabelProps = React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Label> & { inset?: boolean };
type LabelRef = React.ElementRef<typeof DropdownMenuPrimitive.Label>;

function DropdownMenuLabelInner(props: LabelProps, ref: React.ForwardedRef<LabelRef>) {
  const { className, inset, ...rest } = props;
  return (
    <DropdownMenuPrimitive.Label ref={ref} className={cn("px-2 py-1.5 text-sm font-semibold", inset && "pl-8", className)} {...rest} />
  );
}
const DropdownMenuLabel = React.forwardRef(DropdownMenuLabelInner);

type SeparatorProps = React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>;
type SeparatorRef = React.ElementRef<typeof DropdownMenuPrimitive.Separator>;

function DropdownMenuSeparatorInner(props: SeparatorProps, ref: React.ForwardedRef<SeparatorRef>) {
  const { className, ...rest } = props;
  return <DropdownMenuPrimitive.Separator ref={ref} className={cn("-mx-1 my-1 h-px bg-muted", className)} {...rest} />;
}
const DropdownMenuSeparator = React.forwardRef(DropdownMenuSeparatorInner);

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuRadioGroup,
}; 