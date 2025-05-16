import apiClient from './apiClient';

export const academicService = {
  async getCourses() {
    const response = await apiClient.get('/academic/courses');
    return response.data;
  },
  
  async getInstitutes() {
    const response = await apiClient.get('/academic/institutes');
    return response.data;
  },
  
  async getCoursesByInstitute(instituteId: number) {
    const response = await apiClient.get(`/academic/institutes/${instituteId}/courses`);
    return response.data;
  },
};
