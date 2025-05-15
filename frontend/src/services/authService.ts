import apiClient from './apiClient';

export const authService = {
  async login(email: string, password: string) {
    // Convert to URLSearchParams which is the correct format for x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    
    const response = await apiClient.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  async getCurrentUser() {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
  
  async resetPassword(email: string) {
    const response = await apiClient.post('/auth/reset-password', { email });
    return response.data;
  },
};
