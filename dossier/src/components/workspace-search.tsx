"use client";

import { ArrowUpRight, Search, X } from "lucide-react";
import Link from "next/link";
import { Dialog } from "radix-ui";
import { useEffect, useState } from "react";

import { NAV } from "@/lib/nav";

/** A keyboard-accessible command menu, backed by real routes and application search. */
export function WorkspaceSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const items = NAV.flatMap((group) => group.items).filter((item) => item.label.toLowerCase().includes(query.trim().toLowerCase()));
  const changeOpen = (next: boolean) => { setOpen(next); if (!next) setQuery(""); };
  useEffect(() => {
    const shortcut = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((current) => !current);
      }
    };
    window.addEventListener("keydown", shortcut);
    return () => window.removeEventListener("keydown", shortcut);
  }, []);
  return (
    <Dialog.Root open={open} onOpenChange={changeOpen}>
      <Dialog.Trigger className="mb-3 flex min-h-10 w-full items-center gap-2 rounded-control border border-line-field bg-input px-3 text-sm text-muted hover:border-accent-line hover:text-ink group-data-collapsed/sidebar:justify-center group-data-collapsed/sidebar:px-1" aria-label="Search workspace" title="Search workspace (Ctrl or Command K)">
        <Search size={16} aria-hidden="true" />
        <span className="group-data-collapsed/sidebar:hidden">Quick search</span>
        <kbd className="ml-auto rounded border border-line-field px-1 text-[10px] group-data-collapsed/sidebar:hidden">⌘ K</kbd>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/35 backdrop-blur-sm" />
        <Dialog.Content className="fixed top-[15%] left-1/2 z-50 w-[min(520px,calc(100vw-32px))] -translate-x-1/2 overflow-hidden rounded-dialog border border-line-popover bg-card shadow-dialog">
          <Dialog.Title className="sr-only">Search workspace</Dialog.Title>
          <Dialog.Description className="sr-only">Find a screen or search your applications. Use Tab to select a result and Enter to open it.</Dialog.Description>
          <div className="flex items-center gap-3 border-b border-line p-4">
            <Search size={18} className="text-accent" aria-hidden="true" />
            <input type="search" aria-label="Search screens or applications" placeholder="Where would you like to go?" value={query} onChange={(event) => setQuery(event.target.value)} className="min-w-0 flex-1 bg-transparent text-sm outline-none" />
            <Dialog.Close className="grid size-8 place-items-center rounded-control text-muted hover:bg-hover" aria-label="Close search"><X size={16} aria-hidden="true" /></Dialog.Close>
          </div>
          <nav aria-label="Search results" className="max-h-[50dvh] overflow-y-auto p-2">
            {query.trim() && <Link href={`/applications?view=table&q=${encodeURIComponent(query.trim())}`} onClick={() => changeOpen(false)} className="flex items-center gap-3 rounded-control px-3 py-3 text-sm text-accent hover:bg-accent-soft"><Search size={16} aria-hidden="true" /><span className="min-w-0 flex-1 break-words">Search applications for “{query.trim()}”</span><ArrowUpRight size={15} aria-hidden="true" /></Link>}
            {items.map(({ href, label, icon: Icon }) => <Link key={href} href={href} onClick={() => changeOpen(false)} className="flex items-center gap-3 rounded-control px-3 py-3 text-sm hover:bg-hover"><Icon size={16} className="text-muted" aria-hidden="true" />{label}<ArrowUpRight size={14} className="ml-auto text-muted" aria-hidden="true" /></Link>)}
          </nav>
          <div className="border-t border-line px-4 py-3 text-xs text-muted">Tab to navigate · Enter to open · Esc to close</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
