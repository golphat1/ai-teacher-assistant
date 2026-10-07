import { useState } from 'react';
import TextArea from '../../components/ui/TextArea';
import Button from '../../components/ui/Button';
import Alert from '../../components/ui/Alert';
import { submitAssignment } from '../../api/submissions';

export default function AssessmentSubmissionForm({ assignmentId, questions }) {
  const [answers, setAnswers] = useState({});
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  const setAnswer = (questionId, value) => setAnswers((prev) => ({ ...prev, [questionId]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const missing = questions.some((q) => !answers[q.id]?.trim());
    if (missing) {
      setError('Please answer every question before submitting.');
      return;
    }

    setStatus('submitting');
    setError(null);
    try {
      await submitAssignment(
        assignmentId,
        questions.map((q) => ({ question_id: q.id, answer_text: answers[q.id] }))
      );
      setStatus('success');
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  if (status === 'success') {
    return <Alert variant="success">Submitted. Your teacher will grade this and results will appear once released.</Alert>;
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-6" aria-label="Assessment submission form">
      {error && <Alert variant="error">{error}</Alert>}
      {questions.map((q, i) => (
        <div key={q.id}>
          <p className="text-sm font-medium mb-2">
            {i + 1}. {q.question_text} <span className="text-slate-400 font-normal">({q.max_score} pts)</span>
          </p>
          {q.question_type === 'mcq' && q.options ? (
            <fieldset>
              <legend className="sr-only">Answer options for question {i + 1}</legend>
              {q.options.map((opt) => (
                <label key={opt} className="flex items-center gap-2 text-sm mb-1">
                  <input
                    type="radio"
                    name={`q-${q.id}`}
                    value={opt}
                    checked={answers[q.id] === opt}
                    onChange={(e) => setAnswer(q.id, e.target.value)}
                  />
                  {opt}
                </label>
              ))}
            </fieldset>
          ) : (
            <TextArea
              id={`answer-${q.id}`}
              label={`Your answer to question ${i + 1}`}
              value={answers[q.id] || ''}
              onChange={(e) => setAnswer(q.id, e.target.value)}
            />
          )}
        </div>
      ))}
      <Button type="submit" loading={status === 'submitting'}>Submit assignment</Button>
    </form>
  );
}