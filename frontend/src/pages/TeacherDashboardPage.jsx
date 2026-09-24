import LessonRequestForm from '../features/lessons/LessonRequestForm';

// Mock submit handler — simulates a network call so the form's loading/error/success
// states are all exercised locally, with no backend call yet.
async function mockSubmitLessonRequest(payload) {
  console.log('Lesson request payload:', payload);
  await new Promise((resolve) => setTimeout(resolve, 1200));

  // Uncomment to test the error state:
  // throw new Error('Could not reach the server. Please try again.');
}

export default function TeacherDashboardPage() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <LessonRequestForm onSubmit={mockSubmitLessonRequest} />
    </div>
  );
}