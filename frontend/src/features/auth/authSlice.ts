import { createSlice, createAsyncThunk, PayloadAction, ActionReducerMapBuilder } from '@reduxjs/toolkit';
import { authService } from '../../services/authService';

interface User {
  id: number;
  email: string;
  full_name: string;
  roles: { id: number; name: string }[];
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: localStorage.getItem('token'),
  loading: false,
  error: null,
};

export const login = createAsyncThunk<any, { email: string; password: string }>(
  'auth/login',
  async ({ email, password }, { rejectWithValue, dispatch }) => {
    try {
      const response = await authService.login(email, password);
      localStorage.setItem('token', response.access_token);
      
      // Immediately fetch user data after successful login
      try {
        const user = await authService.getCurrentUser();
        return { ...response, user };
      } catch (userError: any) {
        console.error('Error fetching user data after login:', userError);
        return response;
      }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const logout = createAsyncThunk<null>(
  'auth/logout', 
  async () => {
  localStorage.removeItem('token');
  return null;
});

export const checkAuth = createAsyncThunk<any, void>(
  'auth/checkAuth', 
  async (_, { rejectWithValue }) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      return rejectWithValue('No token found');
    }
    const user = await authService.getCurrentUser();
    return { user, token };
  } catch (error) {
    localStorage.removeItem('token');
    return rejectWithValue('Session expired');
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state: AuthState) => {
      state.error = null;
    },
  },
  extraReducers: (builder: ActionReducerMapBuilder<AuthState>) => {
    builder
      // Login
      .addCase(login.pending, (state: AuthState) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state: AuthState, action: PayloadAction<any>) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
        // Set user data if it was fetched successfully
        if (action.payload.user) {
          state.user = action.payload.user;
        }
      })
      .addCase(login.rejected, (state: AuthState, action: PayloadAction<unknown>) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Logout
      .addCase(logout.fulfilled, (state: AuthState) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })
      
      // Check Auth
      .addCase(checkAuth.pending, (state: AuthState) => {
        state.loading = true;
      })
      .addCase(checkAuth.fulfilled, (state: AuthState, action: PayloadAction<any>) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
      })
      .addCase(checkAuth.rejected, (state: AuthState) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
