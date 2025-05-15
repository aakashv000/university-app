import { configureStore } from '@reduxjs/toolkit';
import authReducer from './features/auth/authSlice';
import financeReducer from './features/finance/financeSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    finance: financeReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
