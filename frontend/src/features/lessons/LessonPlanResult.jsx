function Section({ title, children }) {
  return (
    <div className="border-t border-slate-200 pt-4 first:border-t-0 first:pt-0">
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      <div className="mt-2">{children}</div>
    </div>
  );
}

export default function LessonPlanResult({ result }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900">
          {result.subject}: {result.topic}
        </h2>
        {result.is_mock && (
          <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800">
            Mock content — AI generation not yet connected
          </span>
        )}
      </div>
      <p className="mt-1 text-sm text-slate-500">
        {result.grade} &middot; {result.student_count} students &middot; {result.duration_minutes} minutes
      </p>

      <div className="mt-6 space-y-5">
        <Section title="Learning objectives">
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            {result.learning_objectives.map((obj, i) => (
              <li key={i}>{obj}</li>
            ))}
          </ul>
        </Section>

        <Section title="Teaching activities">
          <ul className="space-y-2 text-sm text-slate-700">
            {result.teaching_activities.map((activity, i) => (
              <li key={i}>
                <span className="font-medium">{activity.title}</span> ({activity.duration_minutes} min) —{' '}
                {activity.description}
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Differentiated activities">
          <ul className="space-y-2 text-sm text-slate-700">
            {result.differentiated_activities.map((activity, i) => (
              <li key={i}>
                <span className="font-medium capitalize">{activity.target_group.replace('_', ' ')}:</span>{' '}
                {activity.description}
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Assessment questions">
          <ul className="space-y-2 text-sm text-slate-700">
            {result.assessment_questions.map((q, i) => (
              <li key={i}>
                {q.question_text}{' '}
                <span className="text-slate-400">
                  ({q.question_type}, {q.max_score} pts)
                </span>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Marking rubric">
          <ul className="space-y-1 text-sm text-slate-700">
            {result.marking_rubric.map((c, i) => (
              <li key={i}>
                <span className="font-medium">{c.criterion}</span> ({c.max_points} pts) — {c.description}
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Homework">
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            {result.homework.map((h, i) => (
              <li key={i}>{h}</li>
            ))}
          </ul>
        </Section>

        <Section title="Revision questions">
          <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
            {result.revision_questions.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </Section>
      </div>
    </div>
  );
}