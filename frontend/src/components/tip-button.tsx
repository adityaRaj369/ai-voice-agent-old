"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type TipButtonProps = React.ComponentProps<typeof Button> & {
  tip: string;
};

/** Light, accessible hover tip without depending on portal timing. */
export function TipButton({ tip, className, children, ...props }: TipButtonProps) {
  const classNameStr = typeof className === "string" ? className : undefined;
  return (
    <span
      className={cn(
        "group/tip relative inline-flex max-w-full",
        classNameStr?.includes("w-full") && "w-full",
      )}
    >
      <Button className={cn("relative", classNameStr)} title={tip} aria-label={tip} {...props}>
        {children}
      </Button>
      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-[calc(100%+8px)] left-1/2 z-50 hidden w-max max-w-[220px] -translate-x-1/2 rounded-lg border border-border bg-slate-900 px-2.5 py-1.5 text-center text-[11px] leading-snug font-medium text-white shadow-lg group-hover/tip:block group-focus-within/tip:block"
      >
        {tip}
        <span className="absolute top-full left-1/2 -mt-px h-2 w-2 -translate-x-1/2 rotate-45 bg-slate-900" />
      </span>
    </span>
  );
}
