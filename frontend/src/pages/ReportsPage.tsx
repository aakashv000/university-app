import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  CircularProgress,
  Divider,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import { RootState } from '../store';
import { fetchSemesters, fetchFinanceSummary } from '../features/finance/financeSlice';

const ReportsPage: React.FC = () => {
  const dispatch = useDispatch();
  const { semesters, summary, loading } = useSelector((state: RootState) => state.finance);
  
  const [filters, setFilters] = useState({
    student_id: '',
    semester_id: '',
    start_date: null as Date | null,
    end_date: null as Date | null,
  });
  
  useEffect(() => {
    dispatch(fetchSemesters() as any);
    dispatch(fetchFinanceSummary() as any);
  }, [dispatch]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name as string]: value,
    });
  };
  
  const handleDateChange = (name: string, date: Date | null) => {
    setFilters({
      ...filters,
      [name]: date,
    });
  };
  
  const handleGenerateReport = () => {
    const params: any = {};
    
    if (filters.student_id) {
      params.student_id = parseInt(filters.student_id);
    }
    
    if (filters.semester_id) {
      params.semester_id = parseInt(filters.semester_id as string);
    }
    
    if (filters.start_date) {
      params.start_date = filters.start_date.toISOString();
    }
    
    if (filters.end_date) {
      params.end_date = filters.end_date.toISOString();
    }
    
    dispatch(fetchFinanceSummary(params) as any);
  };
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Financial Reports
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Report Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Student ID"
              name="student_id"
              value={filters.student_id}
              onChange={handleChange}
              type="number"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Semester</InputLabel>
              <Select
                name="semester_id"
                value={filters.semester_id}
                onChange={handleChange}
                label="Semester"
              >
                <MenuItem value="">All Semesters</MenuItem>
                {semesters.map((semester) => (
                  <MenuItem key={semester.id} value={semester.id}>
                    {semester.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={filters.start_date ? new Date(filters.start_date).toISOString().split('T')[0] : ''}
              onChange={(e) => {
                const date = e.target.value ? new Date(e.target.value) : null;
                handleDateChange('start_date', date);
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="End Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={filters.end_date ? new Date(filters.end_date).toISOString().split('T')[0] : ''}
              onChange={(e) => {
                const date = e.target.value ? new Date(e.target.value) : null;
                handleDateChange('end_date', date);
              }}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Button
              variant="contained"
              onClick={handleGenerateReport}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Generate Report'}
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      <Typography variant="h5" gutterBottom>
        Financial Summary
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : summary ? (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: 'primary.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Fees
                </Typography>
                <Typography variant="h3">
                  ${summary.total_fees.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Paid
                </Typography>
                <Typography variant="h3">
                  ${summary.total_paid.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: 'warning.light', color: 'white' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Total Pending
                </Typography>
                <Typography variant="h3">
                  ${summary.total_pending.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Additional Statistics
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Student Count
                    </Typography>
                    <Typography variant="h5">
                      {summary.student_count}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Payment Count
                    </Typography>
                    <Typography variant="h5">
                      {summary.payment_count}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Collection Rate
                    </Typography>
                    <Typography variant="h5">
                      {summary.total_fees > 0
                        ? `${((summary.total_paid / summary.total_fees) * 100).toFixed(1)}%`
                        : '0%'}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Avg. Payment
                    </Typography>
                    <Typography variant="h5">
                      ${summary.payment_count > 0
                        ? (summary.total_paid / summary.payment_count).toFixed(2)
                        : '0.00'}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        <Typography variant="body1">No financial data available.</Typography>
      )}
    </Box>
  );
};

export default ReportsPage;
