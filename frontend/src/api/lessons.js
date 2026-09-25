import { apiRequest } from './httpClient';

export function generateLessonPlan(formValues) {
  const payload = {
    grade: formValues.grade,
    subject: formValues.subject,
    topic: formValues.topic,
    student_count: formValues.numberOfStudents,
    duration_minutes: formValues.durationMinutes,
    curriculum: formValues.curriculum || null,
    ability_level: formValues.abilityLevel,
    learning_context: formValues.learningContext || null,
    additional_instructions: formValues.additionalInstructions || null,
  };

  return apiRequest('/api/v1/lesson-plans/generate', { method: 'POST', body: payload });
}