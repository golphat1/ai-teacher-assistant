import { useState } from 'react';

const GRADE_OPTIONS = [
  { value: 'Grade 6', label: 'Grade 6' },
  { value: 'Grade 7', label: 'Grade 7' },
  { value: 'Grade 8', label: 'Grade 8' },
  { value: 'Grade 9', label: 'Grade 9' },
  { value: 'Grade 10', label: 'Grade 10' },
  { value: 'Grade 11', label: 'Grade 11' },
  { value: 'Grade 12', label: 'Grade 12' },
];

const SUBJECT_OPTIONS = [
  { value: 'English', label: 'English' },
  { value: 'Mathematics', label: 'Mathematics' },
  { value: 'Science', label: 'Science' },
  { value: 'History', label: 'History' },
  { value: 'Geography', label: 'Geography' },
];

const ABILITY_LEVEL_OPTIONS = [
  { value: 'mixed', label: 'Mixed ability' },
  { value: 'below_grade_level', label: 'Below grade level' },
  { value: 'at_grade_level', label: 'At grade level' },
  { value: 'above_grade_level', label: 'Above grade level' },
];

const LEARNING_CONTEXT_OPTIONS = [
  { value: 'Primary school', label: 'Primary school' },
  { value: 'Secondary school', label: 'Secondary school' },
  { value: 'Higher education', label: 'Higher education' },
  { value: 'Homeschool', label: 'Homeschool' },
];

const INITIAL_VALUES = {
  grade: '',
  subject: '',
  topic: '',
  numberOfStudents: '',
  durationMinutes: '',
  curriculum: '',
  abilityLevel: '',
  learningContext: '',
  additionalInstructions: '',
};

function validate(values) {
  const errors = {};

  if (!values.grade) errors.grade = 'Please select a grade.';
  if (!values.subject) errors.subject = 'Please select a subject.';

  if (!values.topic.trim()) {
    errors.topic = 'Please enter a topic.';
  } else if (values.topic.trim().length < 2) {
    errors.topic = 'Topic must be at least 2 characters.';
  }

  const students = Number(values.numberOfStudents);
  if (!values.numberOfStudents) {
    errors.numberOfStudents = 'Please enter the number of students.';
  } else if (!Number.isInteger(students) || students <= 0) {
    errors.numberOfStudents = 'Enter a whole number greater than 0.';
  } else if (students > 200) {
    errors.numberOfStudents = 'Enter a realistic class size (200 or fewer).';
  }

  const duration = Number(values.durationMinutes);
  if (!values.durationMinutes) {
    errors.durationMinutes = 'Please enter the lesson duration.';
  } else if (!Number.isInteger(duration) || duration <= 0) {
    errors.durationMinutes = 'Enter a whole number of minutes greater than 0.';
  } else if (duration > 300) {
    errors.durationMinutes = 'Enter a realistic duration (300 minutes or fewer).';
  }

  if (!values.abilityLevel) errors.abilityLevel = 'Please select a student ability level.';
  if (!values.learningContext) errors.learningContext = 'Please select a learning context.';

  return errors;
}

export function useLessonRequestForm({ onSubmit }) {
  const [values, setValues] = useState(INITIAL_VALUES);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [status, setStatus] = useState('idle'); // idle | submitting | success | error
  const [submitError, setSubmitError] = useState(null);

  const setField = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
    if (touched[name]) {
      setErrors((prev) => ({ ...validate({ ...values, [name]: value }) }));
    }
  };

  const handleBlur = (name) => {
    setTouched((prev) => ({ ...prev, [name]: true }));
    setErrors(validate(values));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const validationErrors = validate(values);
    setErrors(validationErrors);
    setTouched(
      Object.keys(INITIAL_VALUES).reduce((acc, key) => ({ ...acc, [key]: true }), {})
    );

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setStatus('submitting');
    setSubmitError(null);
    try {
      await onSubmit({
        ...values,
        numberOfStudents: Number(values.numberOfStudents),
        durationMinutes: Number(values.durationMinutes),
      });
      setStatus('success');
    } catch (err) {
      setStatus('error');
      setSubmitError(err.message || 'Something went wrong. Please try again.');
    }
  };

  const reset = () => {
    setValues(INITIAL_VALUES);
    setErrors({});
    setTouched({});
    setStatus('idle');
    setSubmitError(null);
  };

  return {
    values,
    errors,
    touched,
    status,
    submitError,
    setField,
    handleBlur,
    handleSubmit,
    reset,
    options: {
      grade: GRADE_OPTIONS,
      subject: SUBJECT_OPTIONS,
      abilityLevel: ABILITY_LEVEL_OPTIONS,
      learningContext: LEARNING_CONTEXT_OPTIONS,
    },
  };
}