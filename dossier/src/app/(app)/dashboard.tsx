import Link from "next/link";
import type { ReactNode } from "react";
import { ArrowUpRight, BriefcaseBusiness, CheckCheck, MessagesSquare, Search, Sparkles } from "lucide-react";

import { CareerArt } from "@/components/career-art";
import { Reveal, WorkspaceMotion } from "@/components/workspace-motion";
import { PageHeader } from "@/components/page-header";
import { buttonClassName } from "@/components/ui/button";
import { StatusDot } from "@/components/ui/status-dot";
import type { ApplicationStatus } from "@/generated/prisma/enums";
import { DASHBOARD_PERIODS, DEFAULT_QUIET_DAYS, type DashboardFigures, type DashboardPeriod } from "@/lib/dashboard";
import type { DayPeriod } from "@/lib/greeting";
import { STATUSES } from "@/lib/status";

import { ActivityChart } from "./activity-chart";
import { FunnelChart } from "./funnel-chart";
import { Greeting } from "./greeting";
import { PeriodFilter, PeriodScoped } from "./period-filter";
import { QuietDays } from "./quiet-days";

const card = "dashboard-card flex flex-col rounded-panel border border-line-card bg-card";
const plural = (count: number, one: string, many: string) => `${count} ${count === 1 ? one : many}`;

/** The dashboard (DSH-1 to DSH-6): the funnel, where things stand, what's worth a look, and the calendar. */
export function Dashboard({
  figures,
  firstName,
  period,
  range = "all",
  quietDays = DEFAULT_QUIET_DAYS,
  empty,
  calendar,
}: {
  figures: DashboardFigures;
  firstName: string;
  period: DayPeriod;
  /** The time filter (E9-8). */
  range?: DashboardPeriod;
  /** Days without news before a follow-up is suggested (E9-9). */
  quietDays?: number;
  /** No applications at all yet. */
  empty: boolean;
  /** The calendar (E15-6), which the time filter doesn't scope. */
  calendar?: ReactNode;
}) {
  const { sent, heardBack } = figures;
  // The summary follows the time filter, so it says which period it covers.
  const within = range === "all" ? null : DASHBOARD_PERIODS.find((entry) => entry.value === range)?.label.toLowerCase();
  return (
    <WorkspaceMotion className="flex min-w-0 flex-1 flex-col">
      <PageHeader
        title={<Greeting name={firstName} serverPeriod={period} />}
        description={
          sent > 0
            ? `${within ? `In the ${within} you've` : "You've"} sent ${plural(sent, "application", "applications")} and heard back from ${heardBack}. That's a solid run. Keep it going.`
            : within
              ? `Nothing sent in the ${within}. Your next application is only a paste away.`
              : "Nothing sent yet. Your first application is only a paste away."
        }
        actions={
          <Link href="/new?fresh=1" className={buttonClassName("primary", "md", "hover:text-on-primary")}>
            + New application
          </Link>
        }
      />

      {empty ? (
        <Columns calendar={calendar}>
          <Welcome />
        </Columns>
      ) : (
        <PeriodFilter period={range}>
          <Columns calendar={calendar}>
            <PeriodScoped className="grid max-w-[1200px] grid-cols-[repeat(auto-fit,minmax(min(100%,380px),1fr))] items-start gap-5">
              <Reveal className="col-span-full">
                <section className="dashboard-hero flex items-center justify-between rounded-panel px-8 py-7" aria-labelledby="next-move-heading">
                  <div className="max-w-[500px]">
                    <p className="workspace-eyebrow mb-3 flex items-center gap-2"><Sparkles size={14} aria-hidden="true" /> Your career, with intention</p>
                    <h2 id="next-move-heading" className="font-serif text-[clamp(28px,3vw,38px)] leading-[1.15] tracking-tight">Make your next move count.</h2>
                    <p className="mt-3 max-w-[380px] text-sm leading-relaxed text-muted">Find a role that fits. Bring your experience to life. Keep every opportunity moving, all in one place.</p>
                    <Link href="/jobs" className={buttonClassName("primary", "md", "mt-5 min-h-10 hover:text-on-primary")}><Search size={15} aria-hidden="true" /> Explore opportunities <ArrowUpRight size={15} aria-hidden="true" /></Link>
                  </div>
                  <CareerArt className="w-[32%] max-w-[310px] shrink-0" />
                </section>
              </Reveal>
              <Metrics figures={figures} range={range} />
              <Funnel figures={figures} />
              <ActivityChart weeks={figures.weeks} />
              <WhereThingsStand byStatus={figures.byStatus} />
              <WorthALook items={figures.attention} quietDays={quietDays} />
            </PeriodScoped>
          </Columns>
        </PeriodFilter>
      )}
    </WorkspaceMotion>
  );
}

/**
 * The cards, with the calendar beside them where there's room for both.
 * Where there isn't, it comes after them, as wide as one card.
 */
function Columns({ calendar, children }: { calendar?: ReactNode; children: ReactNode }) {
  return (
    <div className="dashboard-columns @container px-10 pb-[72px]">
      <div className="grid grid-cols-[minmax(0,1fr)] items-start gap-6 @min-[1100px]:grid-cols-[minmax(0,1200px)_340px]">
        {children}
        {calendar && <div className="min-w-0 @min-[780px]:max-w-[calc(50%-10px)] @min-[1100px]:max-w-none">{calendar}</div>}
      </div>
    </div>
  );
}

/** All figures use the same server-calculated period as the funnel. */
function Metrics({ figures, range }: { figures: DashboardFigures; range: DashboardPeriod }) {
  const count = Object.values(figures.byStatus).reduce((sum, value) => sum + value, 0);
  const entries = [
    { label: "Applications in view", value: count, detail: range === "all" ? "Across your entire search" : DASHBOARD_PERIODS.find((entry) => entry.value === range)?.label, icon: BriefcaseBusiness },
    { label: "Response rate", value: figures.heardBackPercent === null ? "—" : `${figures.heardBackPercent}%`, detail: `${plural(figures.heardBack, "response", "responses")} from ${figures.sent} sent`, icon: MessagesSquare },
    { label: "Interviews reached", value: figures.reachedInterview, detail: "Including completed applications", icon: CheckCheck },
  ];
  return (
    <dl className="col-span-full grid grid-cols-1 gap-4 min-[620px]:grid-cols-3" aria-label="Search overview">
      {entries.map(({ label, value, detail, icon: Icon }) => (
        <div key={label} className="metric-card rounded-panel border border-line-card bg-card p-5">
          <dt className="flex items-center justify-between gap-2 text-meta text-muted">{label}<span className="grid size-8 place-items-center rounded-control bg-accent-soft text-accent"><Icon size={16} aria-hidden="true" /></span></dt>
          <dd className="mt-2 font-serif text-[36px] leading-tight tabular-nums">{value}</dd>
          <div className="mt-1 text-xs text-muted">{detail}</div>
        </div>
      ))}
    </dl>
  );
}

/** "Your funnel" (DSH-2): how far every sent application got, closed ones included, as a Sankey diagram. */
function Funnel({ figures }: { figures: DashboardFigures }) {
  const { funnel, sent, heardBackPercent, reachedInterview } = figures;
  return (
    <section aria-labelledby="funnel-heading" className={`${card} col-span-full gap-6 p-7`}>
      <div className="flex flex-wrap items-baseline justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h2 id="funnel-heading" className="font-serif text-section">
            Your funnel
          </h2>
          <p className="text-control text-muted">How far each application you&apos;ve sent has made it, and where the ones that stopped are now.</p>
        </div>
        <dl className="flex gap-7">
          <Figure value={String(sent)} label="sent" />
          <Figure value={heardBackPercent === null ? "None yet" : `${heardBackPercent}%`} label="heard back" />
          <Figure value={String(reachedInterview)} label="reached interview" />
        </dl>
      </div>
      <FunnelChart funnel={funnel} />
    </section>
  );
}

function Figure({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex flex-col-reverse gap-0.5">
      <dt className="text-label text-muted">{label}</dt>
      <dd className="font-serif text-[32px] leading-none tabular-nums">{value}</dd>
    </div>
  );
}

/** "Where things stand" (DSH-4): every application by its status now. */
function WhereThingsStand({ byStatus }: { byStatus: Record<ApplicationStatus, number> }) {
  const present = STATUSES.filter(({ value }) => byStatus[value] > 0);
  return (
    <section aria-labelledby="standing-heading" className={`${card} gap-[18px] px-7 py-[26px]`}>
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="standing-heading" className="text-[15px] font-medium">
          Where things stand
        </h2>
        <Link href="/applications?view=board" className="text-meta text-muted underline underline-offset-3 hover:text-ink">
          Open board
        </Link>
      </div>
      {/* The legend below says the same in words. */}
      <div aria-hidden="true" className="flex h-3 gap-0.5 overflow-hidden rounded-[6px] bg-hover">
        {present.map(({ value, color }) => (
          <span key={value} style={{ flex: byStatus[value], backgroundColor: color }} />
        ))}
      </div>
      <ul className="grid grid-cols-2 gap-x-5 gap-y-1">
        {STATUSES.map(({ value, label }) => (
          <li key={value} className={`flex items-center gap-[9px] py-1.5 text-sm ${byStatus[value] > 0 ? "text-ink" : "text-muted"}`}>
            <StatusDot status={value} />
            <span className="flex-1">{label}</span>
            <span className="tabular-nums">{byStatus[value]}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/** "Worth a look" (DSH-5): offers, drafts, quiet applications and interviews. */
function WorthALook({ items, quietDays }: { items: DashboardFigures["attention"]; quietDays: number }) {
  return (
    <section aria-labelledby="attention-heading" className={`${card} px-7 pt-[26px] pb-3.5`}>
      <div className="flex items-baseline justify-between gap-3 pb-3">
        <h2 id="attention-heading" className="text-[15px] font-medium">
          Worth a look
        </h2>
        {items.length > 0 && <span className="text-meta text-muted">{plural(items.length, "thing", "things")}</span>}
      </div>
      {items.length === 0 ? (
        <p className="border-t border-line py-5 text-sm text-muted">All caught up. Nice.</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.id} className="-mx-2.5 border-t border-line">
              <Link href={`/applications/${item.id}${item.tab ? `?tab=${item.tab}` : ""}`} className="flex items-start gap-3 rounded-control px-2.5 py-[13px] text-ink hover:bg-hover">
                <StatusDot status={item.status} className="mt-1.5" />
                <span className="flex min-w-0 flex-1 flex-col gap-0.5">
                  <span className="text-field font-medium">
                    {[item.company, item.role].filter(Boolean).join(", ")}
                    {item.soon && <span className="ml-2 rounded-[6px] bg-warning-surface px-2 py-[3px] align-[1px] text-xs font-normal text-warning">Soon</span>}
                  </span>
                  <span className="text-meta leading-[1.45] text-muted">{item.reason}</span>
                </span>
                <span className="mt-px flex-none text-meta text-muted">{item.action} →</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
      <QuietDays days={quietDays} />
    </section>
  );
}

/** Before the first application: where to begin. */
function Welcome() {
  return (
    <Panel>
      <p className="workspace-eyebrow">Your next chapter</p>
      <h2 className="font-serif text-section">Welcome to FrontierPilot</h2>
      <p className="text-sm text-muted">
        Start with your profile: your roles, skills and education are what every tailored resume and cover letter is built from.
        Then paste a job posting, and your funnel and next steps will show up here.
      </p>
      <CareerArt className="self-center w-full max-w-[300px]" />
      <div className="flex flex-wrap items-center gap-4 pt-1">
        <Link href="/profile" className={buttonClassName("secondary")}>
          Fill in your profile
        </Link>
        <Link href="/new?fresh=1" className={buttonClassName("primary", "md", "hover:text-on-primary")}>
          + New application
        </Link>
        <Link href="/welcome" className="text-sm text-muted underline underline-offset-2 hover:text-ink">
          Open the setup guide
        </Link>
      </div>
    </Panel>
  );
}

function Panel({ children }: { children: ReactNode }) {
  return <div className={`${card} dashboard-hero max-w-[760px] items-start gap-3 p-8`}>{children}</div>;
}
