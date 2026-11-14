import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { BrandMark } from "@/components/brand-mark";
import { CareerArt } from "@/components/career-art";
import { safeNextPath } from "@/lib/auth/next-path";
import { getSession } from "@/lib/auth/session";
import { isDesktopApp } from "@/lib/desktop";

import { DesktopBrowserWait } from "./desktop-browser-wait";
import { LoginForm } from "./login-form";

export const metadata: Metadata = { title: "Sign in" };

/** Password-only sign-in, outside the app shell (PRD AUTH-1, AUTH-8). */
export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  if (await getSession()) redirect("/");
  const { next, link } = await searchParams;
  // On this computer, in the desktop app, there's no password: the app signs a browser in (#365).
  const desktop = isDesktopApp();

  return (
    // The form on the panel's colour, a warm wash on the right.
    <main className="grid min-h-screen bg-surface min-[960px]:grid-cols-2">
      <div className="flex items-center justify-center px-8 py-12">
      <div className="flex w-full max-w-[400px] flex-col gap-8">
        <div className="flex flex-col items-start gap-2">
          <BrandMark className="size-10" />
          <div className="flex flex-col">
            <div className="font-serif text-[30px] font-medium tracking-[-0.01em]">FrontierPilot</div>
            <div className="text-sm text-muted">Autonomous Career Radar & AI Cockpit | Orbitron AI</div>
          </div>
        </div>
        {desktop ? (
          <DesktopBrowserWait next={safeNextPath(typeof next === "string" ? next : null)} expired={link === "expired"} />
        ) : (
          <>
            <LoginForm next={typeof next === "string" ? next : undefined} />
            <p className="text-meta leading-[1.6] text-pretty text-muted">
              Your password is set on the server, as a hash in{" "}
              <code className="font-mono text-label">FRONTIERPILOT_PASSWORD</code>. Forgot it? Make a new hash with{" "}
              <code className="font-mono text-label">hash-password</code> and restart.
            </p>
          </>
        )}
      </div>
      </div>
      <div
        aria-hidden="true"
        className="dashboard-hero hidden border-0 min-[960px]:flex min-[960px]:flex-col min-[960px]:items-center min-[960px]:justify-center min-[960px]:gap-6 min-[960px]:p-12"
      >
        <CareerArt className="w-full max-w-[430px]" />
        <div className="max-w-[390px] text-center">
          <p className="workspace-eyebrow mb-4">A little clarity. A world of possibility.</p>
          <p className="font-serif text-[42px] leading-[1.15] tracking-tight">Your experience deserves<br />a next chapter.</p>
          <p className="mt-4 text-sm leading-relaxed text-muted">One profile. Thoughtful applications. Every opportunity in its place.</p>
        </div>
      </div>
    </main>
  );
}
