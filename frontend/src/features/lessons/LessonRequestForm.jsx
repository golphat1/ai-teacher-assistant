import TextInput from '../../components/ui/TextInput';
import Select from '../../components/ui/Select';
import TextArea from '../../components/ui/TextArea';
import Button from '../../components/ui/Button';
import Alert from '../../components/ui/Alert';
import { useLessonRequestForm } from './useLessonRequestForm';

export default function LessonRequestForm({ onSubmit }) {
  const { values, errors, touched, status, submitError, setField, handleBlur, handleSubmit, reset, options } =
    useLessonRequestForm({ onSubmit });

  const errorFor = (name) => (touched[name] ? errors[name] : undefined);
  const fieldProps = (name) => ({
    value: values[name],
    onChange: (e) => setField(name, e.target.value),
    onBlur: () => handleBlur(name),
    error: errorFor(name),
  });

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-6" aria-label="Lesson request form">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Generate a lesson</h2>
        <p className="mt-1 text-sm text-slate-500">
          Fill in the details below and the AI Teacher Assistant will generate a full lesson package.
        </p>
      </div>

      {status === 'success' && (
        <Alert variant="success">
          Lesson request submitted successfully.{' '}
          <button type="button" onClick={reset} className="underline font-medium">
            Create another
          </button>
        </Alert>
      )}

      {status === 'error' && submitError && <Alert variant="error">{submitError}</Alert>}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <Select id="grade" label="Grade" required options={options.grade} placeholder="Select grade" {...fieldProps('grade')} />
        <Select id="subject" label="Subject" required options={options.subject} placeholder="Select subject" {...fieldProps('subject')} />
      </div>

      <TextInput
        id="topic"
        label="Topic"
        required
        placeholder="e.g. Poetry"
        hint="The specific topic within the subject for this lesson."
        {...fieldProps('topic')}
      />

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <TextInput
          id="numberOfStudents"
          label="Number of students"
          required
          type="number"
          min="1"
          max="200"
          inputMode="numeric"
          placeholder="e.g. 40"
          {...fieldProps('numberOfStudents')}
        />
        <TextInput
          id="durationMinutes"
          label="Lesson duration (minutes)"
          required
          type="number"
          min="1"
          max="300"
          inputMode="numeric"
          placeholder="e.g. 60"
          {...fieldProps('durationMinutes')}
        />
      </div>

      <TextInput
        id="curriculum"
        label="Curriculum"
        placeholder="e.g. Common Core, CBSE, IB (optional)"
        hint="Leave blank if not applicable."
        {...fieldProps('curriculum')}
      />

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <Select
          id="abilityLevel"
          label="Student ability level"
          required
          options={options.abilityLevel}
          placeholder="Select ability level"
          {...fieldProps('abilityLevel')}
        />
        <Select
          id="learningContext"
          label="Learning context"
          required
          options={options.learningContext}
          placeholder="Select learning context"
          {...fieldProps('learningContext')}
        />
      </div>

      <TextArea
        id="additionalInstructions"
        label="Additional instructions"
        placeholder="e.g. Focus on iambic pentameter and include a group activity."
        hint="Optional — anything else the AI should take into account."
        {...fieldProps('additionalInstructions')}
      />

      <div className="flex items-center gap-3 pt-2">
        <Button type="submit" loading={status === 'submitting'}>
          {status === 'submitting' ? 'Submitting...' : 'Generate lesson'}
        </Button>
        <Button type="button" variant="secondary" onClick={reset} disabled={status === 'submitting'}>
          Reset
        </Button>
      </div>
    </form>
  );
}