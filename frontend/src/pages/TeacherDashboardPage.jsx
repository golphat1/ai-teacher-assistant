import { useState } from 'react';
import LessonRequestForm from '../features/lessons/LessonRequestForm';
import LessonPlanResult from '../features/lessons/LessonPlanResult';
import { generateLessonPlan } from '../api/lessons';

export default function TeacherDashboardPage() {
  const [result, setResult] = useState(null);

  const handleSubmit = async (formValues) => {
    const response = await generateLessonPlan(formValues);
    // ApiError thrown here propagates up to the form's own error handling —
    // this function intentionally does NOT catch it.
    setResult(response);
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <LessonRequestForm onSubmit={handleSubmit} />
      </div>

      {result && <LessonPlanResult result={result} />}
    </div>
  );
}