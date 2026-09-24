export default function Alert({ variant = 'error', children }) {
  const styles = {
    error: 'bg-red-50 text-red-800 border-red-200',
    success: 'bg-green-50 text-green-800 border-green-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200',
  };

  return (
    <div role="alert" className={`rounded-md border px-4 py-3 text-sm ${styles[variant]}`}>
      {children}
    </div>
  );
}