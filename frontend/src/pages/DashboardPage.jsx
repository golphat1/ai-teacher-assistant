import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../api/client";
import ReviewStatusBadge from "../components/ReviewStatusBadge";

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [pending, setPending] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.get("/analytics/class/1/overview"),
      api.get("/submissions?status=pending_review&limit=5"),
    ])
      .then(([statsRes, pendingRes]) => {
        setStats(statsRes.data);
        setPending(pendingRes.data.items ?? pendingRes.data ?? []);
      })
      .catch(() => setError("Analytics couldn't load. Refresh to try again."));
  }, []);

  if (error) return <p className="text-red-700">{error}</p>;
  if (!stats) return <p className="text-slate-500">Loading dashboard…</p>;

  const chartData = stats.concept_scores ?? [];

  return (
    <section className="space-y-6 sm:space-y-8">
      {/* Header row: stacks on mobile, sits side by side from sm up */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-xl font-medium sm:text-2xl">Class overview</h1>
        <div className="flex flex-wrap gap-2">
          <Link
            to="/roster"
            className="rounded-md border border-slate-300 px-4 py-2 text-center text-sm hover:bg-slate-50"
          >
            View roster
          </Link>
          <Link
            to="/generate"
            className="rounded-md bg-brand-600 px-4 py-2 text-center text-sm text-white hover:bg-brand-700"
          >
            Generate lesson
          </Link>
        </div>
      </div>

      {/* Metrics: 2 columns on mobile, 4 from sm up */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
        <Metric label="Students" value={stats.student_count} />
        <Metric label="Average score" value={`${Math.round(stats.average_score)}%`} />
        <Metric label="Submissions" value={stats.submission_count} />
        <Metric label="Needs review" value={stats.pending_review} />
      </div>

      {/* Chart + pending reviews: stacked on mobile/tablet, side by side on large screens */}
      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr] lg:gap-8">
        <div className="rounded-xl bg-white p-4 shadow-sm sm:p-6">
          <h2 className="mb-4 text-base font-medium sm:text-lg">Score by concept</h2>
          <div className="h-56 sm:h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="concept" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} width={32} />
                <Tooltip />
                <Bar dataKey="average" fill="#3b62d9" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl bg-white p-4 shadow-sm sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-medium sm:text-lg">Needs review</h2>
            <Link to="/reviews" className="text-sm text-brand-600 hover:underline">
              View all
            </Link>
          </div>
          {pending.length === 0 ? (
            <p className="text-sm text-slate-500">Nothing waiting on you right now.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {pending.map((item) => (
                <li key={item.id} className="flex items-center justify-between gap-2 py-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{item.student_name}</p>
                    <p className="truncate text-xs text-slate-500">{item.assessment_title}</p>
                  </div>
                  <ReviewStatusBadge status={item.status} />
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl bg-white p-3 shadow-sm sm:p-4">
      <p className="text-xs text-slate-500 sm:text-sm">{label}</p>
      <p className="mt-1 text-lg font-medium sm:text-2xl">{value}</p>
    </div>
  );
}