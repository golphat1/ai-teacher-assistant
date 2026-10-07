import { apiRequest } from './httpClient';

export function overrideScore(submissionId, answerId, newScore, reason) {
  return apiRequest(`/submissions/${submissionId}/answers/${answerId}/override-score`, {
    method: 'PATCH',
    body: { new_score: newScore, reason: reason || null },
  });
}

export function markReviewed(submissionId) {
  return apiRequest(`/submissions/${submissionId}/review`, { method: 'POST' });
}