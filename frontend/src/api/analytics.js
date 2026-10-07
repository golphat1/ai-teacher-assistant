import { apiRequest } from './httpClient';

export function getClassAnalytics(classId, { refresh = false } = {}) {
  return apiRequest(`/classes/${classId}/analytics${refresh ? '?refresh=true' : ''}`);
}

export function getSubmissionsTable(classId) {
  return apiRequest(`/classes/${classId}/submissions-table`);
}

export function generateReteachRecommendations(classId) {
  return apiRequest(`/classes/${classId}/reteach-recommendations`, { method: 'POST' });
}