import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { financeService } from '../../services/financeService';

interface Semester {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
}

interface StudentFee {
  id: number;
  student_id: number;
  semester_id: number;
  amount: number;
  description: string;
  created_at: string;
  updated_at: string;
  semester: Semester;
}

interface Receipt {
  id: number;
  payment_id: number;
  receipt_number: string;
  generated_at: string;
  pdf_path: string;
}

interface Payment {
  id: number;
  student_id: number;
  student_fee_id: number;
  amount: number;
  payment_date: string;
  payment_method: string;
  transaction_id: string | null;
  notes: string | null;
  receipt: Receipt | null;
}

interface FinanceSummary {
  total_fees: number;
  total_paid: number;
  total_pending: number;
  student_count: number;
  payment_count: number;
}

interface FinanceState {
  semesters: Semester[];
  studentFees: StudentFee[];
  payments: Payment[];
  summary: FinanceSummary | null;
  loading: boolean;
  error: string | null;
}

const initialState: FinanceState = {
  semesters: [],
  studentFees: [],
  payments: [],
  summary: null,
  loading: false,
  error: null,
};

export const fetchSemesters = createAsyncThunk(
  'finance/fetchSemesters',
  async (_, { rejectWithValue }) => {
    try {
      return await financeService.getSemesters();
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch semesters');
    }
  }
);

export const fetchStudentFees = createAsyncThunk(
  'finance/fetchStudentFees',
  async (params: { student_id?: number; semester_id?: number } = {}, { rejectWithValue }) => {
    try {
      return await financeService.getStudentFees(params);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch student fees');
    }
  }
);

export const fetchPayments = createAsyncThunk(
  'finance/fetchPayments',
  async (params: { 
    student_id?: number; 
    student_fee_id?: number;
    start_date?: string;
    end_date?: string;
  } = {}, { rejectWithValue }) => {
    try {
      return await financeService.getPayments(params);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch payments');
    }
  }
);

export const createPayment = createAsyncThunk(
  'finance/createPayment',
  async (paymentData: {
    student_id: number;
    student_fee_id: number;
    amount: number;
    payment_method: string;
    transaction_id?: string;
    notes?: string;
  }, { rejectWithValue }) => {
    try {
      return await financeService.createPayment(paymentData);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create payment');
    }
  }
);

export const fetchFinanceSummary = createAsyncThunk(
  'finance/fetchFinanceSummary',
  async (params: {
    student_id?: number;
    semester_id?: number;
    start_date?: string;
    end_date?: string;
  } = {}, { rejectWithValue }) => {
    try {
      return await financeService.getFinanceSummary(params);
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch finance summary');
    }
  }
);

const financeSlice = createSlice({
  name: 'finance',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Semesters
      .addCase(fetchSemesters.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSemesters.fulfilled, (state, action) => {
        state.loading = false;
        state.semesters = action.payload;
      })
      .addCase(fetchSemesters.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch Student Fees
      .addCase(fetchStudentFees.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchStudentFees.fulfilled, (state, action) => {
        state.loading = false;
        state.studentFees = action.payload;
      })
      .addCase(fetchStudentFees.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch Payments
      .addCase(fetchPayments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPayments.fulfilled, (state, action) => {
        state.loading = false;
        state.payments = action.payload;
      })
      .addCase(fetchPayments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Create Payment
      .addCase(createPayment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createPayment.fulfilled, (state, action) => {
        state.loading = false;
        state.payments = [action.payload, ...state.payments];
      })
      .addCase(createPayment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch Finance Summary
      .addCase(fetchFinanceSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFinanceSummary.fulfilled, (state, action) => {
        state.loading = false;
        state.summary = action.payload;
      })
      .addCase(fetchFinanceSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = financeSlice.actions;
export default financeSlice.reducer;
