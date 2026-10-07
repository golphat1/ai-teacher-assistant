import { useState } from 'react';
import Button from '../../components/ui/Button';
import Alert from '../../components/ui/Alert';
import { generateReteachRecommendations } from '../../api/analytics';

export default function ReteachRecommendationsPanel({ classId }) {
  const [status, setStatus] = useState('idle');
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setStatus('loading');
    setError(null);
    try {
      const result = await generateReteachRecommendations(classId);
      setItems(result);
      setStatus('success');
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Reteach recommendations</h3>
        <Button onClick={handleGenerate} loading={status === 'loading'} variant="secondary">
          Generate
        </Button>
      </div>

      {status === 'error' && <Alert variant="error">{error}</Alert>}
      {status === 'success' && items.length === 0 && (
        <p className="text-sm text-slate-500">No analyzed submissions yet — nothing to prioritize.</p>
      )}

      <div className="space-y-4">
        {items.map((item, i) => (
          <div key={i} className="border-t border-slate-100 pt-3 first:border-t-0 first:pt-0">
            <p className="text-sm font-medium">
              {item.concept} <span className="text-slate-400 font-normal">({item.frequency} students)</span>
            </p>
            {item.recommendation && (
              <dl className="mt-1 text-sm text-slate-600 space-y-1">
                <div><dt className="inline font-medium text-slate-500">Why it matters: </dt><dd className="inline">{item.recommendation.why_it_matters}</dd></div>
                <div><dt className="inline font-medium text-slate-500">Activity: </dt><dd className="inline">{item.recommendation.suggested_activity}</dd></div>
                <div><dt className="inline font-medium text-slate-500">Check understanding: </dt><dd className="inline">{item.recommendation.check_for_understanding}</dd></div>
                <div><dt className="inline font-medium text-slate-500">Follow-up: </dt><dd className="inline">{item.recommendation.follow_up_resource}</dd></div>
              </dl>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}