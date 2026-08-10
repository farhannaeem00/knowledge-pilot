"use client";

import * as React from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

const Tabs = TabsPrimitive.Root;

type ListProps = React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>;
type ListRef = React.ElementRef<typeof TabsPrimitive.List>;

function TabsListInner(props: ListProps, ref: React.ForwardedRef<ListRef>) {
  const { className, ...rest } = props;
  return (
    <TabsPrimitive.List
      ref={ref}
      className={cn("inline-flex h-9 items-center justify-start gap-1 border-b border-border", className)}
      {...rest}
    />
  );
}
const TabsList = React.forwardRef(TabsListInner);

type TriggerProps = React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>;
type TriggerRef = React.ElementRef<typeof TabsPrimitive.Trigger>;

function TabsTriggerInner(props: TriggerProps, ref: React.ForwardedRef<TriggerRef>) {
  const { className, ...rest } = props;
  return (
    <TabsPrimitive.Trigger
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap border-b-2 border-transparent px-3 py-2 text-sm font-medium text-muted-foreground transition-colors data-[state=active]:border-primary data-[state=active]:text-primary disabled:pointer-events-none disabled:opacity-50",
        className
      )}
      {...rest}
    />
  );
}
const TabsTrigger = React.forwardRef(TabsTriggerInner);

type ContentProps = React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>;
type ContentRef = React.ElementRef<typeof TabsPrimitive.Content>;

function TabsContentInner(props: ContentProps, ref: React.ForwardedRef<ContentRef>) {
  const { className, ...rest } = props;
  return (
    <TabsPrimitive.Content
      ref={ref}
      className={cn("mt-4 focus-visible:outline-none", className)}
      {...rest}
    />
  );
}
const TabsContent = React.forwardRef(TabsContentInner);

export { Tabs, TabsList, TabsTrigger, TabsContent };