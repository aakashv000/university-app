import apiClient from './apiClient';

export const financeService = {
  async getSemesters() {
    const response = await apiClient.get('/finance/semesters');
    return response.data;
  },
  
  async getStudentFees(params = {}) {
    const response = await apiClient.get('/finance/student-fees', { params });
    return response.data;
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
    const response = await apiClient.get(`/finance/receipts/${receiptId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
  
  async getAllStudentReceipts(studentId: number) {
    const response = await apiClient.get(`/finance/students/${studentId}/receipts`);
    return response.data;
  },
  
  async getFinanceSummary(params = {}) {
    const response = await apiClient.get('/finance/summary', { params });
    return response.data;
  },
};
