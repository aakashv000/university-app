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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
} from '@mui/material';

import { RootState } from '../store';
import { fetchSemesters, fetchStudentFees } from '../features/finance/financeSlice';
import apiClient from '../services/apiClient';

interface StudentFeeFormData {
  student_id: number;
  semester_id: number;
  amount: number;
  description: string;
}

const FeesPage: React.FC = () => {
  const dispatch = useDispatch();
  const { semesters, studentFees, loading } = useSelector((state: RootState) => state.finance);
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [feeData, setFeeData] = useState<StudentFeeFormData>({
    student_id: 0,
    semester_id: 0,
    amount: 0,
    description: '',
  });
  
  useEffect(() => {
    dispatch(fetchSemesters() as any);
    dispatch(fetchStudentFees() as any);
  }, [dispatch]);
  
  const handleDialogOpen = () => {
    setDialogOpen(true);
  };
  
  const handleDialogClose = () => {
    setDialogOpen(false);
    setFeeData({
      student_id: 0,
      semester_id: 0,
      amount: 0,
      description: '',
    });
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>) => {
    const { name, value } = e.target;
    setFeeData({
      ...feeData,
      [name as string]: value,
    });
  };
  
  const handleSubmit = async () => {
    try {
      await apiClient.post('/finance/student-fees', feeData);
      dispatch(fetchStudentFees() as any);
      handleDialogClose();
    } catch (error) {
      console.error('Failed to create fee:', error);
    }
  };
  
  if (loading) {
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
          Student Fees
        </Typography>
        <Button variant="contained" onClick={handleDialogOpen}>
          Assign Fee
        </Button>
      </Box>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {semesters.map((semester) => (
          <Grid item xs={12} md={6} key={semester.id}>
            <Card>
              <CardHeader title={semester.name} />
              <Divider />
              <CardContent>
                <Typography variant="body1">
                  Start Date: {new Date(semester.start_date).toLocaleDateString()}
                </Typography>
                <Typography variant="body1">
                  End Date: {new Date(semester.end_date).toLocaleDateString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      <Typography variant="h5" gutterBottom>
        Assigned Fees
      </Typography>
      
      {studentFees.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Student ID</TableCell>
                <TableCell>Semester</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Created At</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {studentFees.map((fee) => (
                <TableRow key={fee.id}>
                  <TableCell>{fee.id}</TableCell>
                  <TableCell>{fee.student_id}</TableCell>
                  <TableCell>{fee.semester.name}</TableCell>
                  <TableCell>${fee.amount.toFixed(2)}</TableCell>
                  <TableCell>{fee.description || 'N/A'}</TableCell>
                  <TableCell>{new Date(fee.created_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Typography variant="body1">No student fees found.</Typography>
      )}
      
      {/* Assign Fee Dialog */}
      <Dialog open={dialogOpen} onClose={handleDialogClose}>
        <DialogTitle>Assign Fee to Student</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Student ID"
            type="number"
            fullWidth
            name="student_id"
            value={feeData.student_id}
            onChange={handleChange}
            required
          />
          
          <FormControl fullWidth margin="dense">
            <InputLabel>Semester</InputLabel>
            <Select
              name="semester_id"
              value={feeData.semester_id}
              onChange={handleChange}
              required
            >
              {semesters.map((semester) => (
                <MenuItem key={semester.id} value={semester.id}>
                  {semester.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            label="Amount"
            type="number"
            fullWidth
            name="amount"
            value={feeData.amount}
            onChange={handleChange}
            required
          />
          
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={2}
            name="description"
            value={feeData.description}
            onChange={handleChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button 
            onClick={handleSubmit}
            variant="contained"
            disabled={
              !feeData.student_id ||
              !feeData.semester_id ||
              !feeData.amount
            }
          >
            Assign Fee
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FeesPage;
