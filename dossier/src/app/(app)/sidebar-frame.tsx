"use client";

import { Menu, PanelLeftClose, PanelLeftOpen, X } from "lucide-react";
import { Dialog } from "radix-ui";
import { createContext, use, useEffect, useState, type ReactNode } from "react";

import { cn } from "@/lib/cn";
import { rememberPreference, SIDEBAR_COOKIE } from "@/lib/ui-preferences";

const CollapsedContext = createContext<{ collapsed: boolean; expand: () => void }>({ collapsed: false, expand: () => {} });
export function useSidebarCollapsed(): boolean { return use(CollapsedContext).collapsed; }
export function useExpandSidebar(): () => void { return use(CollapsedContext).expand; }

/** Desktop collapse is remembered. Mobile navigation is a modal with focus trapping and Escape. */
export function SidebarFrame({ initialCollapsed, brand, children }: { initialCollapsed: boolean; brand: ReactNode; children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(initialCollapsed);
  const [mobileOpen, setMobileOpen] = useState(false);
  const change = (next: boolean) => {
    setCollapsed(next);
    rememberPreference(SIDEBAR_COOKIE, next ? "collapsed" : "expanded");
  };
  const Icon = collapsed ? PanelLeftOpen : PanelLeftClose;
  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)");
    const close = () => { if (media.matches) setMobileOpen(false); };
    media.addEventListener("change", close);
    return () => media.removeEventListener("change", close);
  }, []);
  return (
    <>
      <Dialog.Root open={mobileOpen} onOpenChange={setMobileOpen}>
        <div className="flex h-16 w-full items-center justify-between border-b border-line bg-sidebar px-5 md:hidden">
          <div className="flex items-center gap-2">{brand}</div>
          <Dialog.Trigger className="grid size-11 place-items-center rounded-control border border-line-field bg-card text-ink" aria-label="Open navigation"><Menu size={20} aria-hidden="true" /></Dialog.Trigger>
        </div>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-40 bg-black/35 backdrop-blur-sm" />
          <Dialog.Content className="group/sidebar fixed inset-y-0 left-0 z-50 flex w-[min(300px,85vw)] flex-col overflow-y-auto bg-sidebar shadow-dialog" onClick={(event) => { if ((event.target as HTMLElement).closest("a[href]")) setMobileOpen(false); }}>
            <Dialog.Title className="sr-only">Workspace navigation</Dialog.Title>
            <Dialog.Description className="sr-only">Navigate your job search workspace.</Dialog.Description>
            <div className="flex items-center justify-between border-b border-line px-4 py-5"><div className="flex items-center gap-2">{brand}</div><Dialog.Close className="grid size-10 place-items-center rounded-control text-muted hover:bg-hover" aria-label="Close navigation"><X size={20} aria-hidden="true" /></Dialog.Close></div>
            <CollapsedContext value={{ collapsed: false, expand: () => {} }}>{children}</CollapsedContext>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
      <CollapsedContext value={{ collapsed, expand: () => change(false) }}>
        <aside data-collapsed={collapsed || undefined} className={cn("group/sidebar sticky top-0 hidden h-dvh shrink-0 flex-col self-start overflow-x-hidden overflow-y-auto border-r border-line bg-sidebar motion-safe:transition-[width] motion-safe:duration-200 md:flex", collapsed ? "w-16" : "w-[248px]")}>
          <div className={cn("group/header relative flex items-center gap-2 border-b border-line", collapsed ? "justify-center px-1 py-5" : "px-4 py-6")}>
            <div className={cn("flex min-w-0 flex-1 items-center gap-2", collapsed && "flex-none group-hover/header:opacity-0 group-has-[button:focus-visible]/header:opacity-0 motion-safe:transition-opacity")}>{brand}</div>
            <button type="button" onClick={() => change(!collapsed)} aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} title={collapsed ? "Expand sidebar" : "Collapse sidebar"} className={cn("grid size-8 shrink-0 place-items-center rounded-control text-muted hover:bg-hover hover:text-ink", collapsed && "absolute inset-0 m-auto bg-surface opacity-0 group-hover/header:opacity-100 focus-visible:opacity-100 motion-safe:transition-opacity")}><Icon size={16} aria-hidden="true" /></button>
          </div>
          {!mobileOpen && children}
        </aside>
      </CollapsedContext>
    </>
  );
}
