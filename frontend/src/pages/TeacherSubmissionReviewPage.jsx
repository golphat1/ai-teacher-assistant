import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Alert from '../components/ui/Alert';
import Button from '../components/ui/Button';
import TextInput from '../components/ui/TextInput';
import { getSubmissionDetail } from '../api/submissions';
import { overrideScore, markReviewed } from '../api/review';

export default function TeacherSubmissionReviewPage() {
  const { submissionId } = useParams();
  const [submission, setSubmission] = useState(null);
  const [scores, setScores] = useState({});
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState(null);
  const [savingId, setSavingId] = useState(null);
  const [reviewing, setReviewing] = useState(false);

  const load = () => {
    getSubmissionDetail(submissionId)
      .then((data) => {
        setSubmission(data);
        setScores(Object.fromEntries(data.answers.map((a) => [a.id, a.score ?? ''])));
        setStatus('success');
      })
      .catch((err) => { setError(err.message); setStatus('error'); });
  };

  useEffect(load, [submissionId]);

  const handleSaveOverride = async (answerId) => {
    setSavingId(answerId);
    setError(null);
    try {
      await overrideScore(submissionId, answerId, Number(scores[answerId]));
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingId(null);
    }
  };

  const handleMarkReviewed = async () => {
    setReviewing(true);
    setError(null);
    try {
      await markReviewed(submissionId);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setReviewing(false);
    }
  };

  if (status === 'loading') return <p className="text-sm text-slate-500">Loading submission...</p>;
  if (status === 'error') return <Alert variant="error">{error}</Alert>;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 sm:p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">{submission.student_name}'s submission</h2>
          <p className="text-sm text-slate-500">
            {submission.reviewed_at ? `Reviewed ${new Date(submission.reviewed_at).toLocaleString()}` : 'Not yet reviewed'}
          </p>
        </div>
        <Button onClick={handleMarkReviewed} loading={reviewing} disabled={Boolean(submission.reviewed_at)}>
          {submission.reviewed_at ? 'Already reviewed' : 'Mark as reviewed'}
        </Button>
      </div>

      {error && <Alert variant="error">{error}</Alert>}

      <div className="space-y-5">
        {submission.answers.map((answer) => (
          <div key={answer.id} className="border-t border-slate-100 pt-4 first:border-t-0 first:pt-0">
            <p className="text-sm font-medium mb-1">{answer.question_text} <span className="text-slate-400 font-normal">(max {answer.max_score})</span></p>
            <p className="text-sm text-slate-600 mb-2">{answer.answer_text}</p>
            <div className="flex items-end gap-3 max-w-xs">
              <TextInput
                id={`score-${answer.id}`}
                label="Score"
                type="number"
                min="0"
                max={answer.max_score}
                value={scores[answer.id]}
                onChange={(e) => setScores((prev) => ({ ...prev, [answer.id]: e.target.value }))}
              />
              <Button
                variant="secondary"
                onClick={() => handleSaveOverride(answer.id)}
                loading={savingId === answer.id}
              >
                Save
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}