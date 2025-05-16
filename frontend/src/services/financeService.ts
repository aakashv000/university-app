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
