import apiClient from './apiClient';

export const financeService = {
  async getSemesters() {
    const response = await apiClient.get('/finance/semesters');
    return response.data;
  },
  
  async getStudentFees(params = {}) {
    try {
      console.log('Calling student-fees endpoint with params:', params);
      const response = await apiClient.get('/finance/student-fees', { params });
      console.log('Student fees response data:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getStudentFees:', error);
      throw error;
    }
  },
  
  async getStandardFees(params: Record<string, any> = {}) {
    try {
      const response = await apiClient.get('/finance/standard-fees', { params });
      return response.data;
    } catch (error) {
      console.error('Error in getStandardFees:', error);
      throw error;
    }
  },
  
  async createStandardFee(feeData: {
    course_id: number;
    semester_id: number;
    amount: number;
    name: string;
    description?: string;
  }) {
    const response = await apiClient.post('/finance/standard-fees', feeData);
    return response.data;
  },
  
  async updateStandardFee(feeId: number, feeData: {
    course_id: number;
    semester_id: number;
    amount: number;
    name: string;
    description?: string;
  }) {
    const response = await apiClient.put(`/finance/standard-fees/${feeId}`, feeData);
    return response.data;
  },
  
  async deleteStandardFee(feeId: number) {
    await apiClient.delete(`/finance/standard-fees/${feeId}`);
    // No need to return data for a 204 response
    return;
  },
  
  async getPayments(params = {}) {
    const response = await apiClient.get('/finance/payments', { params });
    return response.data;
  },
  
  async createPayment(paymentData: {
    student_id: number;
    student_fee_id: number;
    amount: number;
    payment_method: string;
    transaction_id?: string;
    notes?: string;
  }) {
    const response = await apiClient.post('/finance/payments', paymentData);
    return response.data;
  },
  
  async downloadReceipt(receiptId: number) {
    try {
      const response = await apiClient.get(`/finance/receipts/${receiptId}/download`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Error downloading receipt:', error);
      throw error;
    }
  },
  
  async getAllStudentReceipts(studentId: number) {
    try {
      const response = await apiClient.get(`/finance/students/${studentId}/receipts`);
      return response.data;
    } catch (error) {
      console.error('Error getting all student receipts:', error);
      throw error;
    }
  },
  
  async getFinanceSummary(params = {}) {
    const response = await apiClient.get('/finance/summary', { params });
    return response.data;
  },
};
