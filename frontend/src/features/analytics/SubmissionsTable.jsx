import { Link } from 'react-router-dom';
import ReviewStatusBadge from '../../components/ui/ReviewStatusBadge';

export default function SubmissionsTable({ rows }) {
  if (rows.length === 0) return <p className="text-sm text-slate-500">No submissions yet for this class.</p>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-slate-500">
            <th scope="col" className="py-2 pr-4 font-medium">Student</th>
            <th scope="col" className="py-2 pr-4 font-medium">Assignment</th>
            <th scope="col" className="py-2 pr-4 font-medium">Score</th>
            <th scope="col" className="py-2 pr-4 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.submission_id} className="border-b border-slate-100">
              <td className="py-2 pr-4">
                <Link to={`/teacher/submissions/${row.submission_id}`} className="text-brand-600 hover:underline">
                  {row.student_name}
                </Link>
              </td>
              <td className="py-2 pr-4">{row.assignment_title}</td>
              <td className="py-2 pr-4">{row.overall_score ?? '—'}</td>
              <td className="py-2 pr-4"><ReviewStatusBadge status={row.review_status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}