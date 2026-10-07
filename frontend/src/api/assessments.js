import { apiRequest } from './httpClient';

export function createAssessmentFromLessonPlan(lessonPlanId) {
  return apiRequest(`/assessments/from-lesson-plan/${lessonPlanId}`, { method: 'POST' });
}