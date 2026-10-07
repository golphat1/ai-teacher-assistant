import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Alert from '../components/ui/Alert';
import SubmissionsTable from '../features/analytics/SubmissionsTable';
import ReteachRecommendationsPanel from '../features/analytics/ReteachRecommendationsPanel';
import { getClassAnalytics, getSubmissionsTable } from '../api/analytics';

export default function ClassAnalyticsPage() {
  const { classId } = useParams();
  const [overview, setOverview] = useState(null);
  const [rows, setRows] = useState([]);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setStatus('loading');
      try {
        const [overviewData, tableData] = await Promise.all([getClassAnalytics(classId), getSubmissionsTable(classId)]);
        if (!cancelled) {
          setOverview(overviewData);
          setRows(tableData);
          setStatus('success');
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setStatus('error');
        }
      }
    }
    load();
    return () => { cancelled = true; };
  }, [classId]);

  if (status === 'loading') return <p className="text-sm text-slate-500">Loading analytics...</p>;
  if (status === 'error') return <Alert variant="error">{error}</Alert>;

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <p className="text-sm text-slate-500">Class average</p>
        <p className="text-3xl font-semibold text-slate-900">
          {overview.average_score !== null ? overview.average_score.toFixed(1) : '—'} / 10
        </p>
        <p className="text-xs text-slate-400 mt-1">
          {overview.submission_count} analyzed submissions{overview.is_cached && ' · cached'}
        </p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="text-sm font-semibold mb-3">Submissions</h3>
        <SubmissionsTable rows={rows} />
      </div>

      <ReteachRecommendationsPanel classId={classId} />
    </div>
  );
}