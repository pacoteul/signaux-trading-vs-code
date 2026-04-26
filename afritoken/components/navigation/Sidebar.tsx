"use client";

import Link from "next/link";
import { cn } from "@/lib/cn";

export type SidebarItem = {
  href: string;
  label: string;
  icon?: React.ReactNode;
};

export function Sidebar({
  title,
  items,
  activeHash,
}: {
  title: string;
  items: SidebarItem[];
  activeHash?: string;
}) {
  return (
    <aside className="hidden lg:block w-60 flex-shrink-0">
      <div className="sticky top-24 space-y-1">
        <div className="px-3 mb-4">
          <p className="text-[10px] uppercase tracking-[0.2em] text-accent/80">
            {title}
          </p>
        </div>
        {items.map((item) => {
          const active = activeHash === item.href.replace("#", "");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                active
                  ? "bg-accent/10 text-accent"
                  : "text-neutral-light/70 hover:bg-white/5 hover:text-white"
              )}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
