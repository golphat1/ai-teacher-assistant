// frontend/src/features/analytics/ClassAnalyticsDashboard.jsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function ClassAnalyticsDashboard({ data }) {
  const misconceptionData = data.common_misconceptions.map(([concept, count]) => ({ concept, count }));

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <p className="text-sm text-slate-500">Class average</p>
        <p className="text-3xl font-semibold text-slate-900">
          {data.average_score?.toFixed(1) ?? '—'} / 10
        </p>
        <p className="text-xs text-slate-400 mt-1">{data.submission_count} submissions analyzed</p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="text-sm font-semibold mb-3">Most common misconceptions</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={misconceptionData} layout="vertical">
            <XAxis type="number" allowDecimals={false} />
            <YAxis type="category" dataKey="concept" width={160} />
            <Tooltip />
            <Bar dataKey="count" fill="#2563eb" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}