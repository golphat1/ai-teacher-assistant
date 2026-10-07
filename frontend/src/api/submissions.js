import { apiRequest } from './httpClient';

export function submitAssignment(assignmentId, payload) {
  return apiRequest(`/assignments/${assignmentId}/submissions`, {
    method: 'POST',
    body: payload,
  });
}

export function listSubmissions(assignmentId) {
  return apiRequest(`/assignments/${assignmentId}/submissions`, { method: 'GET' });
}

export function getSubmissionDetail(submissionId) {
  return apiRequest(`/assignments/${submissionId}/detail`, { method: 'GET' });
}