import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import { RootState } from '../store';
import { fetchStudentFees } from '../features/finance/financeSlice';
import { fetchPayments } from '../features/finance/financeSlice';
import { fetchFinanceSummary } from '../features/finance/financeSlice';

const DashboardPage: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { studentFees, payments, summary, loading } = useSelector((state: RootState) => state.finance);
  
  const isStudent = user?.roles.some(role => role.name === 'student');
  const isAdminOrFaculty = user?.roles.some(role => ['admin', 'faculty'].includes(role.name));
  
  useEffect(() => {
    if (isStudent) {
      dispatch(fetchStudentFees({ student_id: user.id }) as any);
      dispatch(fetchPayments({ student_id: user.id }) as any);
    } else if (isAdminOrFaculty) {
      dispatch(fetchFinanceSummary() as any);
    }
  }, [dispatch, user, isStudent, isAdminOrFaculty]);
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Typography variant="h6" gutterBottom>
        Welcome, {user?.full_name}!
      </Typography>
      
      {isStudent ? (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="My Fees" />
              <Divider />
              <CardContent>
                {studentFees.length > 0 ? (
                  <List>
                    {studentFees.map((fee) => (
                      <ListItem key={fee.id} divider>
                        <ListItemText
                          primary={`${fee.semester.name} - $${fee.amount.toFixed(2)}`}
                          secondary={fee.description}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No fees found.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Recent Payments" />
              <Divider />
              <CardContent>
                {payments.length > 0 ? (
                  <List>
                    {payments.slice(0, 5).map((payment) => (
                      <ListItem key={payment.id} divider>
                        <ListItemText
                          primary={`$${payment.amount.toFixed(2)} - ${payment.payment_method}`}
                          secondary={`Date: ${new Date(payment.payment_date).toLocaleDateString()}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No payments found.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 140,
                bgcolor: 'primary.light',
                color: 'white',
              }}
            >
              <Typography variant="h6" gutterBottom>
                Total Fees
              </Typography>
              <Typography variant="h3">
                ${summary?.total_fees.toFixed(2) || '0.00'}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 140,
                bgcolor: 'success.light',
                color: 'white',
              }}
            >
              <Typography variant="h6" gutterBottom>
                Total Paid
              </Typography>
              <Typography variant="h3">
                ${summary?.total_paid.toFixed(2) || '0.00'}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 140,
                bgcolor: 'warning.light',
                color: 'white',
              }}
            >
              <Typography variant="h6" gutterBottom>
                Total Pending
              </Typography>
              <Typography variant="h3">
                ${summary?.total_pending.toFixed(2) || '0.00'}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Summary" />
              <Divider />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body1">
                      Total Students: {summary?.student_count || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1">
                      Total Payments: {summary?.payment_count || 0}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default DashboardPage;
