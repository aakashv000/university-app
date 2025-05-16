import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardActions,
  SelectChangeEvent
} from '@mui/material';
import { Download as DownloadIcon, Print as PrintIcon } from '@mui/icons-material';

import { RootState } from '../store';
import { fetchPayments, fetchStudentFees, createPayment } from '../features/finance/financeSlice';
import { financeService } from '../services/financeService';

const PaymentsPage: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  const { payments, studentFees, loading } = useSelector((state: RootState) => state.finance);
  
  // State for all student fees (for admin dropdown)
  const [allStudentFees, setAllStudentFees] = useState<any[]>([]);
  const [loadingFees, setLoadingFees] = useState(false);
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [paymentData, setPaymentData] = useState({
    student_id: 0,
    student_fee_id: 0,
    amount: 0,
    payment_method: '',
    transaction_id: '',
    notes: '',
  });
  
  // Add state for error and success messages
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(false);
  
  const isStudent = user?.roles.some(role => role.name === 'student');
  const isAdmin = user?.roles.some(role => role.name === 'admin');
  
  useEffect(() => {
    if (isStudent) {
      dispatch(fetchPayments({ student_id: user.id }) as any);
      dispatch(fetchStudentFees({ student_id: user.id }) as any);
    } else {
      dispatch(fetchPayments() as any);
      
      // For admin, fetch all student fees
      if (isAdmin) {
        const fetchAllStudentFees = async () => {
          try {
            setLoadingFees(true);
            console.log('Fetching all student fees for admin...');
            const response = await financeService.getStudentFees();
            console.log('Student fees response:', response);
            setAllStudentFees(response);
          } catch (err) {
            console.error('Error fetching all student fees:', err);
          } finally {
            setLoadingFees(false);
          }
        };
        fetchAllStudentFees();
      }
    }
  }, [dispatch, user, isStudent, isAdmin]);
  
  const handleDialogOpen = () => {
    setDialogOpen(true);
    if (isStudent) {
      setPaymentData({
        ...paymentData,
        student_id: user.id,
      });
    }
  };
  
  const handleDialogClose = () => {
    setDialogOpen(false);
    setPaymentData({
      student_id: 0,
      student_fee_id: 0,
      amount: 0,
      payment_method: '',
      transaction_id: '',
      notes: '',
    });
  };
  
  const handleTextFieldChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPaymentData({
      ...paymentData,
      [name as string]: value,
    });
  };
  
  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setPaymentData({
      ...paymentData,
      [name as string]: value,
    });
    
    // If student fee is selected, set the amount
    if (name === 'student_fee_id') {
      // For students, use studentFees; for admins, use allStudentFees
      const feesToSearch = isStudent ? studentFees : allStudentFees;
      const selectedFee = feesToSearch.find((fee: any) => fee.id === Number(value));
      if (selectedFee) {
        setPaymentData({
          ...paymentData,
          student_fee_id: selectedFee.id,
          amount: selectedFee.amount,
        });
      }
    }
  };
  
  // Function to open receipt in new tab and trigger print dialog
  const openAndPrintReceipt = async (receiptId: number) => {
    try {
      const blob = await financeService.downloadReceipt(receiptId);
      const url = window.URL.createObjectURL(blob);
      
      // Open in new tab
      const newTab = window.open(url, '_blank');
      
      // Trigger print dialog after the PDF is loaded
      if (newTab) {
        newTab.addEventListener('load', () => {
          setTimeout(() => {
            newTab.print();
          }, 1000); // Small delay to ensure PDF is fully loaded
        });
      }
    } catch (error) {
      console.error('Failed to open and print receipt:', error);
      setError('Failed to open receipt for printing. Please download it manually.');
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const resultAction = await dispatch(createPayment(paymentData) as any);
      
      if (createPayment.fulfilled.match(resultAction)) {
        // Always refresh payments list for all user types
        if (isStudent) {
          dispatch(fetchPayments({ student_id: user.id }) as any);
        } else {
          // For admin and faculty, fetch all payments
          dispatch(fetchPayments() as any);
          
          // For admin and faculty, automatically open and print the receipt
          if (resultAction.payload && resultAction.payload.receipt) {
            openAndPrintReceipt(resultAction.payload.receipt.id);
          }
        }
        
        // Refresh student fees data
        if (paymentData.student_id) {
          dispatch(fetchStudentFees({ student_id: paymentData.student_id }) as any);
        }
        
        setSuccess('Payment created successfully! A receipt has been generated and opened for printing.');
        handleDialogClose();
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to create payment:', error);
      setError('Failed to create payment. Please try again.');
      setLoading(false);
    }
  };
  
  const handleDownloadReceipt = async (receiptId: number) => {
    try {
      setLoading(true);
      const blob = await financeService.downloadReceipt(receiptId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `receipt-${receiptId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setLoading(false);
    } catch (error) {
      console.error('Failed to download receipt:', error);
      setError('Failed to download receipt. Please try again.');
      setLoading(false);
    }
  };

  // Function to view and print receipt
  const handleViewAndPrintReceipt = async (receiptId: number) => {
    try {
      setLoading(true);
      await openAndPrintReceipt(receiptId);
      setLoading(false);
    } catch (error) {
      console.error('Failed to view and print receipt:', error);
      setError('Failed to open receipt for printing. Please try again.');
      setLoading(false);
    }
  };
  
  const handlePrintAllReceipts = async () => {
    try {
      setLoading(true);
      const response = await financeService.getAllStudentReceipts(user.id);
      
      if (!response.receipt_ids || response.receipt_ids.length === 0) {
        setError('No receipts found to print.');
        setLoading(false);
        return;
      }
      
      // Download each receipt one by one
      const receiptCount = response.receipt_ids.length;
      setSuccess(`Found ${receiptCount} receipts. Downloading...`);
      
      // Process receipts sequentially to avoid overwhelming the browser
      for (let i = 0; i < receiptCount; i++) {
        const receiptId = response.receipt_ids[i];
        try {
          const blob = await financeService.downloadReceipt(receiptId);
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `receipt-${receiptId}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
          
          // Update progress message
          setSuccess(`Downloaded ${i + 1} of ${receiptCount} receipts...`);
        } catch (receiptError) {
          console.error(`Failed to download receipt ${receiptId}:`, receiptError);
        }
      }
      
      setSuccess(`Successfully downloaded ${receiptCount} receipts.`);
      setLoading(false);
    } catch (error) {
      console.error('Failed to get all receipts:', error);
      setError('Failed to get receipts. Please try again.');
      setLoading(false);
    }
  };
  
  if (loading || isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Payments
        </Typography>
        <Box>
          {isStudent && (
            <Button 
              variant="outlined" 
              sx={{ mr: 2 }}
              onClick={handlePrintAllReceipts}
            >
              Print All Receipts
            </Button>
          )}
          <Button 
            variant="contained" 
            onClick={handleDialogOpen}
            disabled={isStudent && studentFees.length === 0}
          >
            Make Payment
          </Button>
        </Box>
      </Box>
      
      {error && (
        <Box sx={{ mb: 2 }}>
          <Paper sx={{ p: 2, bgcolor: '#ffebee' }}>
            <Typography color="error">{error}</Typography>
          </Paper>
        </Box>
      )}
      
      {success && (
        <Box sx={{ mb: 2 }}>
          <Paper sx={{ p: 2, bgcolor: '#e8f5e9' }}>
            <Typography color="primary">{success}</Typography>
          </Paper>
        </Box>
      )}
      
      {isStudent && studentFees.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            My Fees
          </Typography>
          <Grid container spacing={2}>
            {studentFees.map((fee) => (
              <Grid item xs={12} md={6} key={fee.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{fee.semester.name}</Typography>
                    <Typography variant="body1">Amount: ${fee.amount.toFixed(2)}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {fee.description}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      onClick={() => {
                        setPaymentData({
                          ...paymentData,
                          student_id: user.id,
                          student_fee_id: fee.id,
                          amount: fee.amount,
                        });
                        setDialogOpen(true);
                      }}
                    >
                      Pay Now
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      <Typography variant="h6" gutterBottom>
        Payment History
      </Typography>
      
      {payments.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                {!isStudent && <TableCell>Student</TableCell>}
                <TableCell>Amount</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Semester</TableCell>
                <TableCell>Course</TableCell>
                <TableCell>Institute</TableCell>
                <TableCell>Method</TableCell>
                <TableCell>Transaction ID</TableCell>
                <TableCell>Receipt</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {payments.map((payment) => (
                <TableRow key={payment.id}>
                  <TableCell>{payment.id}</TableCell>
                  {!isStudent && <TableCell>{payment.student_id}</TableCell>}
                  <TableCell>${payment.amount.toFixed(2)}</TableCell>
                  <TableCell>{new Date(payment.payment_date).toLocaleDateString()}</TableCell>
                  <TableCell>{payment.student_fee?.semester?.name || 'N/A'}</TableCell>
                  <TableCell>{payment.student_fee?.course?.name || 'N/A'}</TableCell>
                  <TableCell>{payment.student_fee?.course?.institute?.name || 'N/A'}</TableCell>
                  <TableCell>{payment.payment_method}</TableCell>
                  <TableCell>{payment.transaction_id || 'N/A'}</TableCell>
                  <TableCell>
                    {payment.receipt && (
                      <>
                        <Button
                          size="small"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownloadReceipt(payment.receipt.id)}
                          style={{ marginRight: '8px' }}
                        >
                          Download
                        </Button>
                        <Button
                          size="small"
                          startIcon={<PrintIcon />}
                          onClick={() => handleViewAndPrintReceipt(payment.receipt.id)}
                          color="secondary"
                        >
                          View & Print
                        </Button>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Typography variant="body1">No payment records found.</Typography>
      )}
      
      {/* Payment Dialog */}
      <Dialog open={dialogOpen} onClose={handleDialogClose}>
        <DialogTitle>Make a Payment</DialogTitle>
        <DialogContent>
          {!isStudent && (
            <TextField
              margin="dense"
              label="Student ID"
              type="number"
              fullWidth
              name="student_id"
              value={paymentData.student_id}
              onChange={handleTextFieldChange}
              required
            />
          )}
          
          {isStudent ? (
            <FormControl fullWidth margin="dense">
              <InputLabel>Fee</InputLabel>
              <Select
                name="student_fee_id"
                value={paymentData.student_fee_id}
                onChange={handleSelectChange}
                required
              >
                {studentFees.map((fee) => (
                  <MenuItem key={fee.id} value={fee.id}>
                    {fee.semester.name} - ${fee.amount.toFixed(2)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          ) : (
            <FormControl fullWidth margin="dense">
              <InputLabel>Student Fee</InputLabel>
              <Select
                name="student_fee_id"
                value={paymentData.student_fee_id}
                onChange={handleSelectChange}
                required
              >
                {loadingFees ? (
                  <MenuItem disabled value="">
                    Loading student fees...
                  </MenuItem>
                ) : allStudentFees.length > 0 ? (
                  allStudentFees.map((fee) => (
                    <MenuItem key={fee.id} value={fee.id}>
                      {fee.student?.full_name || `Student ID: ${fee.student_id}`} | 
                      {fee.course?.name || 'No Course'} | 
                      {fee.semester?.name || 'No Semester'} | 
                      ${fee.amount.toFixed(2)}
                    </MenuItem>
                  ))
                ) : (
                  <MenuItem disabled value="">
                    No student fees available
                  </MenuItem>
                )}
              </Select>
            </FormControl>
          )}
          
          <TextField
            margin="dense"
            label="Amount"
            type="number"
            fullWidth
            name="amount"
            value={paymentData.amount}
            onChange={handleTextFieldChange}
            required
          />
          
          <FormControl fullWidth margin="dense">
            <InputLabel>Payment Method</InputLabel>
            <Select
              name="payment_method"
              value={paymentData.payment_method}
              onChange={handleSelectChange}
              required
            >
              <MenuItem value="Credit Card">Credit Card</MenuItem>
              <MenuItem value="Debit Card">Debit Card</MenuItem>
              <MenuItem value="Bank Transfer">Bank Transfer</MenuItem>
              <MenuItem value="Cash">Cash</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            label="Transaction ID"
            fullWidth
            name="transaction_id"
            value={paymentData.transaction_id}
            onChange={handleTextFieldChange}
          />
          
          <TextField
            margin="dense"
            label="Notes"
            fullWidth
            multiline
            rows={2}
            name="notes"
            value={paymentData.notes}
            onChange={handleTextFieldChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button 
            onClick={handleSubmit}
            variant="contained"
            disabled={
              !paymentData.student_id ||
              !paymentData.student_fee_id ||
              !paymentData.amount ||
              !paymentData.payment_method
            }
          >
            Submit Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PaymentsPage;
