import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Alert from '../components/ui/Alert';
import AssessmentSubmissionForm from '../features/submissions/AssessmentSubmissionForm';
import { getAssignment } from '../api/assignments';

export default function StudentAssignmentPage() {
  const { assignmentId } = useParams();
  const [assignment, setAssignment] = useState(null);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState(null);

  useEffect(() => {
    getAssignment(assignmentId)
      .then((data) => { setAssignment(data); setStatus('success'); })
      .catch((err) => { setError(err.message); setStatus('error'); });
  }, [assignmentId]);

  if (status === 'loading') return <p className="text-sm text-slate-500">Loading assignment...</p>;
  if (status === 'error') return <Alert variant="error">{error}</Alert>;

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 sm:p-8">
      <h2 className="text-xl font-semibold mb-1">{assignment.assessment.title}</h2>
      <p className="text-sm text-slate-500 mb-6">{assignment.assessment.questions.length} question(s)</p>
      <AssessmentSubmissionForm assignmentId={assignmentId} questions={assignment.assessment.questions} />
    </div>
  );
}