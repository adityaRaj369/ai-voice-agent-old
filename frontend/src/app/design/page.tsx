import { PageHeader, Panel } from "@/components/page-shell";

export default function DesignPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        kicker="Assignment Q3"
        title="Attendance without smartphones"
        description="If smartphones and apps do not exist — but LLMs, telephony, landlines, RFID, and SMS do — how would HR track 1,000 people across 100 locations every day?"
      />

      <Panel title="Operating model">
        <div className="space-y-4 text-sm leading-relaxed text-slate-700 sm:text-[15px]">
          <p>
            <strong className="text-teal-800">One shared landline per site</strong>. Workers use the site phone or RFID
            badge. A Hunar Voice AI clerk verifies employee code + spoken PIN and writes attendance to a central ledger.
          </p>
          <p>
            <strong className="text-teal-800">Primary:</strong> landline ↔ Voice AI.{" "}
            <strong className="text-teal-800">Secondary:</strong> RFID gate.{" "}
            <strong className="text-teal-800">Tertiary:</strong> supervisor SMS.{" "}
            <strong className="text-teal-800">Quaternary:</strong> USSD on feature phones.
          </p>
          <p>
            Scale: 100 sites × ~10 workers = 1,000. With concurrency, the network can be marked in minutes. This app
            prototypes that model with a seeded workforce and live Voice AI check-in.
          </p>
        </div>
      </Panel>

      <Panel title="Workflow">
        <pre className="overflow-auto rounded-xl border border-border bg-slate-50 p-4 font-mono text-xs leading-6 text-slate-700 sm:text-sm">{`Worker arrives
  → RFID badge OR shared landline / IVR
  → Hunar Voice AI verifies name + code + PIN
  → ledger updates present / late / leave
  → control tower shows missing by site
  → outbound AI call to supervisor if needed
  → end of day payroll-ready export`}</pre>
      </Panel>
    </div>
  );
}
