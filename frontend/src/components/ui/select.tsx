"use client";

import * as React from "react";
import * as SelectPrimitive from "@radix-ui/react-select";
import { Check, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const Select = SelectPrimitive.Root;
const SelectGroup = SelectPrimitive.Group;
const SelectValue = SelectPrimitive.Value;

type TriggerProps = React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>;
type TriggerRef = React.ElementRef<typeof SelectPrimitive.Trigger>;

function SelectTriggerInner(props: TriggerProps, ref: React.ForwardedRef<TriggerRef>) {
  const { className, children, ...rest } = props;
  return (
    <SelectPrimitive.Trigger
      ref={ref}
      className={cn(
        "flex h-9 w-full items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...rest}
    >
      {children}
      <SelectPrimitive.Icon asChild>
        <ChevronDown className="h-4 w-4 opacity-50" />
      </SelectPrimitive.Icon>
    </SelectPrimitive.Trigger>
  );
}
const SelectTrigger = React.forwardRef(SelectTriggerInner);

type ContentProps = React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>;
type ContentRef = React.ElementRef<typeof SelectPrimitive.Content>;

function SelectContentInner(props: ContentProps, ref: React.ForwardedRef<ContentRef>) {
  const { className, children, position = "popper", ...rest } = props;
  return (
    <SelectPrimitive.Portal>
      <SelectPrimitive.Content
        ref={ref}
        className={cn(
          "relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border shadow-md",
          position === "popper" && "translate-y-1",
          className
        )}
        style={{ backgroundColor: "hsl(var(--card))" }}
        position={position}
        {...rest}
      >
        <SelectPrimitive.Viewport className="p-1">{children}</SelectPrimitive.Viewport>
      </SelectPrimitive.Content>
    </SelectPrimitive.Portal>
  );
}
const SelectContent = React.forwardRef(SelectContentInner);

type ItemProps = React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>;
type ItemRef = React.ElementRef<typeof SelectPrimitive.Item>;

function SelectItemInner(props: ItemProps, ref: React.ForwardedRef<ItemRef>) {
  const { className, children, ...rest } = props;
  return (
    <SelectPrimitive.Item
      ref={ref}
      className={cn(
        "relative flex w-full cursor-pointer select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        className
      )}
      {...rest}
    >
      <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
        <SelectPrimitive.ItemIndicator>
          <Check className="h-4 w-4" />
        </SelectPrimitive.ItemIndicator>
      </span>
      <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
    </SelectPrimitive.Item>
  );
}
const SelectItem = React.forwardRef(SelectItemInner);

export { Select, SelectGroup, SelectValue, SelectTrigger, SelectContent, SelectItem };