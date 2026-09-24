export default function Label({htmlfor, children, required}) {
    return (
        <label htmlFor={htmlFor} className="block text-sm font-medium text-slate-700 mb-1">
            {children}
            {required && <span className="text-red-600 ml-0.5" aria-hidden="true">*</span>}
            </label>
    );
}