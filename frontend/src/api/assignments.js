import { apiRequest } from './httpClient';

export function createAssignment({ assessmentId, classId, dueAt }) {
  return apiRequest('/assignments', {
    method: 'POST',
    body: { assessment_id: assessmentId, class_id: classId, due_at: dueAt || null },
  });
}

export function getAssignment(assignmentId) {
  return apiRequest(`/assignments/${assignmentId}`);
}