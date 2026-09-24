import Label from './Label';
import FieldError from './FieldError';

export default function Select({ id, label, required, error, options, placeholder, ...selectProps }) {
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div>
      <Label htmlFor={id} required={required}>
        {label}
      </Label>
      <select
        id={id}
        required={required}
        aria-required={required || undefined}
        aria-invalid={Boolean(error) || undefined}
        aria-describedby={errorId}
        className={`w-full rounded-md border px-3 py-2 text-sm shadow-sm bg-white transition-colors
          focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500
          ${error ? 'border-red-400' : 'border-slate-300'}`}
        {...selectProps}
      >
        <option value="" disabled hidden>
          {placeholder || 'Select an option'}
        </option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      <FieldError id={errorId} message={error} />
    </div>
  );
}