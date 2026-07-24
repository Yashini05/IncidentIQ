import { useMemo, useState } from 'react';
import axios from 'axios';

type EvidenceItem = {
  timestamp?: string | null;
  level?: string | null;
  service?: string | null;
  message?: string | null;
};

type IncidentReport = {
  incident_id: string;
  title?: string | null;
  timestamp?: string | null;
  created_at: string;
  severity?: string | null;
  root_cause?: string | null;
  confidence?: number | null;
  affected_services: string[];
  evidence: EvidenceItem[];
  prediction?: string | null;
  recommendations: string[];
  explanation?: string | null;
};

type AnalyzeResponse = {
  incident: IncidentReport;
  metadata: Record<string, unknown>;
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? `${window.location.protocol}//${window.location.hostname}:8001`,
});

const severityTone: Record<string, string> = {
  Critical: 'border-danger/40 bg-danger/10 text-red-100',
  Medium: 'border-accent2/40 bg-amber-500/10 text-amber-100',
  Low: 'border-accent/30 bg-teal-500/10 text-teal-100',
};

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [incidentId, setIncidentId] = useState('');
  const [incident, setIncident] = useState<IncidentReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const confidenceLabel = useMemo(() => {
    if (!incident?.confidence && incident?.confidence !== 0) {
      return '—';
    }
    return `${incident.confidence.toFixed(1)}%`;
  }, [incident]);

  const submitFile = async () => {
    if (!file) {
      setError('Choose a log file before analyzing it.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const payload = new FormData();
      payload.append('file', file);

      const { data } = await api.post<AnalyzeResponse>('/analyze', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setIncident(data.incident);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  const fetchIncident = async () => {
    if (!incidentId.trim()) {
      setError('Enter an incident id to look up a saved report.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const { data } = await api.get<IncidentReport>(`/incident/${incidentId.trim()}`);
      setIncident(data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-aurora text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-3 border-b border-white/10 pb-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-teal-300/80">IncidentIQ</p>
            <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              AI incident response with evidence-first analysis.
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              Upload application logs, generate a structured incident report, and retrieve persisted incidents by id.
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300 shadow-glow backdrop-blur">
            FastAPI backend • React dashboard • PostgreSQL persistence
          </div>
        </header>

        <main className="grid flex-1 gap-6 py-6 lg:grid-cols-[1.05fr_1.25fr]">
          <section className="space-y-6 rounded-3xl border border-white/10 bg-panel p-6 shadow-glow backdrop-blur-xl">
            <div>
              <h2 className="font-display text-2xl font-semibold text-white">Analyze logs</h2>
              <p className="mt-1 text-sm text-slate-400">The backend validates the file, parses evidence, reasons over impact, and stores the incident.</p>
            </div>

            <label className="flex cursor-pointer flex-col gap-3 rounded-2xl border border-dashed border-white/15 bg-white/5 p-5 transition hover:border-teal-400/50 hover:bg-white/7">
              <span className="text-sm font-medium text-slate-200">Application log file</span>
              <span className="text-sm text-slate-400">Accepts .log or .txt files.</span>
              <input
                className="hidden"
                type="file"
                accept=".log,.txt"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
              <span className="text-sm text-teal-300">{file ? file.name : 'No file selected'}</span>
            </label>

            <button
              className="inline-flex items-center justify-center rounded-2xl bg-teal-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-teal-300 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
              onClick={submitFile}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Run analysis'}
            </button>

            <div className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-5">
              <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Lookup incident</h3>
              <div className="flex gap-3">
                <input
                  className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-teal-400/60"
                  value={incidentId}
                  onChange={(event) => setIncidentId(event.target.value)}
                  placeholder="incident id"
                />
                <button
                  className="rounded-2xl border border-white/10 px-4 py-3 text-sm font-medium text-white transition hover:border-teal-400/50 hover:bg-white/5 disabled:cursor-not-allowed disabled:text-slate-500"
                  onClick={fetchIncident}
                  disabled={loading}
                >
                  Fetch
                </button>
              </div>
            </div>

            {error ? (
              <div className="rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-sm text-red-100">{error}</div>
            ) : null}
          </section>

          <section className="space-y-6 rounded-3xl border border-white/10 bg-panel p-6 shadow-glow backdrop-blur-xl">
            <div className="flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Report</p>
                <h2 className="mt-2 font-display text-2xl font-semibold text-white">Structured incident output</h2>
              </div>
              <div className="rounded-2xl border border-white/10 px-4 py-3 text-sm text-slate-300">
                Confidence {confidenceLabel}
              </div>
            </div>

            {incident ? (
              <>
                <div className="grid gap-4 md:grid-cols-2">
                  <Card title="Incident id" value={incident.incident_id} />
                  <Card title="Title" value={incident.title ?? 'Untitled incident'} />
                  <Card title="Severity" value={incident.severity ?? 'Unknown'} tone={severityTone[incident.severity ?? ''] ?? undefined} />
                  <Card title="Root cause" value={incident.root_cause ?? 'Unclassified'} />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <Panel title="Affected services" items={incident.affected_services} emptyLabel="No services identified." />
                  <Panel title="Recommendations" items={incident.recommendations} emptyLabel="No recommendations available." />
                </div>

                <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Evidence</h3>
                  <div className="mt-4 space-y-3">
                    {incident.evidence.length > 0 ? incident.evidence.map((item, index) => (
                      <article key={`${item.timestamp ?? 'evidence'}-${index}`} className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                        <div className="flex flex-wrap gap-2 text-xs text-slate-400">
                          <span>{item.timestamp ?? 'unknown time'}</span>
                          <span>{item.level ?? 'unknown level'}</span>
                          <span>{item.service ?? 'unknown service'}</span>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-slate-200">{item.message ?? 'No message captured.'}</p>
                      </article>
                    )) : (
                      <p className="text-sm text-slate-400">No evidence captured.</p>
                    )}
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <Card title="Prediction" value={incident.prediction ?? 'No prediction available.'} />
                  <Card title="Explanation" value={incident.explanation ?? 'No explanation available.'} />
                </div>
              </>
            ) : (
              <div className="flex min-h-[28rem] flex-col items-start justify-center rounded-3xl border border-dashed border-white/10 bg-white/5 p-8 text-slate-400">
                <p className="text-lg font-medium text-slate-200">No incident loaded yet.</p>
                <p className="mt-2 max-w-xl text-sm leading-6">
                  Upload a log file to create a new report, or paste an incident id to retrieve a saved incident from the database.
                </p>
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}

function Card({ title, value, tone }: { title: string; value: string; tone?: string }) {
  return (
    <div className={`rounded-2xl border p-4 ${tone ?? 'border-white/10 bg-white/5'}`}>
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <p className="mt-2 break-words text-sm leading-6 text-white">{value}</p>
    </div>
  );
}

function Panel({ title, items, emptyLabel }: { title: string; items: string[]; emptyLabel: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
      <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">{title}</h3>
      <div className="mt-4 space-y-2">
        {items.length > 0 ? items.map((item) => (
          <div key={item} className="rounded-xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm leading-6 text-slate-200">
            {item}
          </div>
        )) : <p className="text-sm text-slate-400">{emptyLabel}</p>}
      </div>
    </div>
  );
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return (error.response?.data as { detail?: string } | undefined)?.detail ?? error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Unexpected error';
}
