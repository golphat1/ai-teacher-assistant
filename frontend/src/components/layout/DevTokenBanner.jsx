import { useState } from 'react';
import { getAccessToken, setAccessToken, clearAccessToken } from '../../api/httpClient';

// TEMPORARY: remove once a real login page exists.
export default function DevTokenBanner() {
  const [tokenInput, setTokenInput] = useState('');
  const [hasToken, setHasToken] = useState(Boolean(getAccessToken()));

  const save = () => {
    if (!tokenInput.trim()) return;
    setAccessToken(tokenInput.trim());
    setHasToken(true);
    setTokenInput('');
  };

  const clear = () => {
    clearAccessToken();
    setHasToken(false);
  };

  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-xs text-amber-900 flex items-center gap-2">
      <span className="font-medium">Dev only:</span>
      {hasToken ? (
        <>
          <span>Access token is set.</span>
          <button onClick={clear} className="underline">Clear token</button>
        </>
      ) : (
        <>
          <input
            type="text"
            value={tokenInput}
            onChange={(e) => setTokenInput(e.target.value)}
            placeholder="Paste JWT access token from /docs login response"
            className="flex-1 rounded border border-amber-300 px-2 py-1"
          />
          <button onClick={save} className="rounded bg-amber-600 px-2 py-1 text-white">
            Save token
          </button>
        </>
      )}
    </div>
  );
}