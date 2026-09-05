import { cn } from "@/lib/utils";

export function PageHeader({
  kicker,
  title,
  description,
  action,
}: {
  kicker?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0 space-y-1.5">
        {kicker ? <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-teal-700">{kicker}</p> : null}
        <h1 className="font-display text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">{title}</h1>
        {description ? <p className="max-w-2xl text-sm text-slate-500 sm:text-[15px]">{description}</p> : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}

export function Panel({
  children,
  className,
  title,
  description,
}: {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
}) {
  return (
    <section className={cn("surface-card p-4 sm:p-6", className)}>
      {title ? (
        <div className="mb-4 space-y-1 border-b border-border pb-4">
          <h2 className="section-title">{title}</h2>
          {description ? <p className="section-desc">{description}</p> : null}
        </div>
      ) : null}
      {children}
    </section>
  );
}

export function LivePill({ live, label }: { live: boolean; label: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium",
        live ? "border-teal-200 bg-teal-50 text-teal-800" : "border-slate-200 bg-slate-50 text-slate-500",
      )}
    >
      <span className={cn("status-dot", live ? "bg-teal-600 text-teal-600" : "bg-slate-400 text-slate-400")} />
      {label}
    </span>
  );
}

export function Field({
  label,
  children,
  className,
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("field", className)}>
      <label className="field-label">{label}</label>
      {children}
    </div>
  );
}
