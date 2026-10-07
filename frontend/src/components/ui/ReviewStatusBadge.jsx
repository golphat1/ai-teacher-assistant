const STATUS_CONFIG = {
  pending: { label: 'Pending review', className: 'bg-amber-50 text-amber-800 border-amber-200' },
  reviewed: { label: 'Reviewed by teacher', className: 'bg-green-50 text-green-800 border-green-200' },
  auto_released: { label: 'Auto-released', className: 'bg-blue-50 text-blue-800 border-blue-200' },
};

export default function ReviewStatusBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.pending;
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${config.className}`}>
      {config.label}
    </span>
  );
}