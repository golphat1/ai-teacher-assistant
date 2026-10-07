import { useEffect, useState } from 'react';
import Button from '../../components/ui/Button';
import Select from '../../components/ui/Select';
import Alert from '../../components/ui/Alert';
import { createAssessmentFromLessonPlan } from '../../api/assessments';
import { createAssignment } from '../../api/assignments';
import { listClasses } from '../../api/classes';

export default function CreateAssessmentPanel({ lessonPlanId }) {
  const [status, setStatus] = useState('idle'); // idle | creating | created | assigning | assigned | error
  const [assessment, setAssessment] = useState(null);
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState('');
  const [assignment, setAssignment] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    listClasses().then(setClasses).catch(() => {});
  }, []);

  const handleCreateAssessment = async () => {
    setStatus('creating');
    setError(null);
    try {
      const result = await createAssessmentFromLessonPlan(lessonPlanId);
      setAssessment(result);
      setStatus('created');
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  const handleAssign = async () => {
    if (!selectedClassId) return;
    setStatus('assigning');
    setError(null);
    try {
      const result = await createAssignment({ assessmentId: assessment.id, classId: selectedClassId });
      setAssignment(result);
      setStatus('assigned');
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <h3 className="text-sm font-semibold mb-3">Assessment</h3>

      {error && <Alert variant="error">{error}</Alert>}

      {status === 'idle' && (
        <Button onClick={handleCreateAssessment} loading={false}>Create assessment from this lesson</Button>
      )}
      {status === 'creating' && <Button loading>Creating...</Button>}

      {(status === 'created' || status === 'assigning') && assessment && (
        <div className="space-y-3">
          <p className="text-sm text-slate-600">
            Created "{assessment.title}" with {assessment.questions.length} question(s).
          </p>
          <div className="flex items-end gap-3">
            <div className="flex-1">
              <Select
                id="class-select"
                label="Assign to class"
                required
                placeholder="Select a class"
                options={classes.map((c) => ({ value: c.id, label: c.name }))}
                value={selectedClassId}
                onChange={(e) => setSelectedClassId(e.target.value)}
              />
            </div>
            <Button onClick={handleAssign} loading={status === 'assigning'} disabled={!selectedClassId}>
              Assign
            </Button>
          </div>
        </div>
      )}

      {status === 'assigned' && assignment && (
        <Alert variant="success">
          Assigned. Students in that class can now submit at{' '}
          <span className="font-mono text-xs">/student/assignments/{assignment.id}</span>
        </Alert>
      )}
    </div>
  );
}