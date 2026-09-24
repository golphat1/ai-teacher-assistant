import Label from './Label';
import FieldError from './FieldError';

export default function TextArea({ id, label, required, error, hint, ...textareaProps }) {
  const errorId = error ? `${id}-error` : undefined;
  const hintId = hint ? `${id}-hint` : undefined;

  return (
    <div>
      <Label htmlFor={id} required={required}>
        {label}
      </Label>
      <textarea
        id={id}
        required={required}
        aria-required={required || undefined}
        aria-invalid={Boolean(error) || undefined}
        aria-describedby={[errorId, hintId].filter(Boolean).join(' ') || undefined}
        rows={4}
        className={`w-full rounded-md border px-3 py-2 text-sm shadow-sm transition-colors
          focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-y
          ${error ? 'border-red-400' : 'border-slate-300'}`}
        {...textareaProps}
      />
      {hint && !error && <p id={hintId} className="mt-1 text-sm text-slate-500">{hint}</p>}
      <FieldError id={errorId} message={error} />
    </div>
  );
}