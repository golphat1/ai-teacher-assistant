import { apiRequest } from './httpClient';

export function listClasses() {
  return apiRequest('/classes');
}