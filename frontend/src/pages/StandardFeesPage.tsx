import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Button,
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Grid,
  Box,
  CircularProgress,
  SelectChangeEvent
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';

import { RootState } from '../store';
import { financeService } from '../services/financeService';
import { academicService } from '../services/academicService';

interface StandardFee {
  id: number;
  course_id: number;
  semester_id: number;
  amount: number;
  name: string;
  description?: string;
  course?: {
    id: number;
    name: string;
    institute?: {
      id: number;
      name: string;
    };
  };
  semester?: {
    id: number;
    name: string;
  };
}

interface Course {
  id: number;
  name: string;
  institute?: {
    id: number;
    name: string;
  };
}

interface Semester {
  id: number;
  name: string;
  course_id: number;
}

const StandardFeesPage: React.FC = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state: RootState) => state.auth);
  
  const [standardFees, setStandardFees] = useState<StandardFee[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [semesters, setSemesters] = useState<Semester[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentFeeId, setCurrentFeeId] = useState<number | null>(null);
  
  const [feeData, setFeeData] = useState({
    course_id: 0,
    semester_id: 0,
    amount: 0,
    name: '',
    description: ''
  });
  
  const [filteredSemesters, setFilteredSemesters] = useState<Semester[]>([]);
  
  // Check if user has admin role
  const isAdmin = user?.roles.some((role: { name: string }) => role.name === 'admin');
  
  useEffect(() => {
    fetchStandardFees();
    fetchCourses();
    fetchSemesters();
  }, []);
  
  // Filter semesters based on selected course
  useEffect(() => {
    if (feeData.course_id) {
      const filtered = semesters.filter((semester: Semester) => semester.course_id === feeData.course_id);
      setFilteredSemesters(filtered);
      
      // Reset semester selection if current selection doesn't belong to the selected course
      if (feeData.semester_id) {
        const semesterBelongsToCourse = filtered.some((s: Semester) => s.id === feeData.semester_id);
        if (!semesterBelongsToCourse) {
          setFeeData({
            ...feeData,
            semester_id: 0
          });
        }
      }
    } else {
      setFilteredSemesters([]);
    }
  }, [feeData.course_id, semesters]);
  
  const fetchStandardFees = async () => {
    try {
      setLoading(true);
      const response = await financeService.getStandardFees();
      setStandardFees(response);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching standard fees:', err);
      setError('Failed to fetch standard fees');
      setLoading(false);
    }
  };
  
  const fetchCourses = async () => {
    try {
      const response = await academicService.getCourses();
      setCourses(response);
    } catch (err) {
      console.error('Error fetching courses:', err);
    }
  };
  
  const fetchSemesters = async () => {
    try {
      const response = await financeService.getSemesters();
      setSemesters(response);
    } catch (err) {
      console.error('Error fetching semesters:', err);
    }
  };
  
  const handleDialogOpen = (fee: StandardFee | null = null) => {
    if (fee) {
      // Edit mode
      setEditMode(true);
      setCurrentFeeId(fee.id);
      setFeeData({
        course_id: fee.course_id,
        semester_id: fee.semester_id,
        amount: fee.amount,
        name: fee.name,
        description: fee.description || ''
      });
    } else {
      // Create mode
      setEditMode(false);
      setCurrentFeeId(null);
      setFeeData({
        course_id: 0,
        semester_id: 0,
        amount: 0,
        name: '',
        description: ''
      });
    }
    setDialogOpen(true);
  };
  
  const handleDialogClose = () => {
    setDialogOpen(false);
    setError(null);
  };
  
  const handleTextFieldChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = e.target;
    
    if (name === 'use_standard_fee') {
      setFeeData({
        ...feeData,
        use_standard_fee: checked
      });
    } else {
      setFeeData({
        ...feeData,
        [name as keyof typeof feeData]: value
      });
    }
  };
  
  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setFeeData({
      ...feeData,
      [name as keyof typeof feeData]: name === 'course_id' || name === 'semester_id' ? Number(value) : value
    });
  };
  
  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      if (!feeData.course_id || !feeData.semester_id || !feeData.amount || !feeData.name) {
        setError('Please fill all required fields');
        setLoading(false);
        return;
      }
      
      if (editMode && currentFeeId) {
        // Update existing fee
        await financeService.updateStandardFee(currentFeeId, feeData);
        setSuccess('Standard fee updated successfully!');
      } else {
        // Create new fee
        await financeService.createStandardFee(feeData);
        setSuccess('Standard fee created successfully!');
      }
      
      // Refresh the list
      fetchStandardFees();
      handleDialogClose();
      setLoading(false);
    } catch (error: any) {
      console.error('Failed to save standard fee:', error);
      setError(error.response?.data?.detail || 'Failed to save standard fee');
      setLoading(false);
    }
  };
  
  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this standard fee?')) {
      try {
        setLoading(true);
        await financeService.deleteStandardFee(id);
        setSuccess('Standard fee deleted successfully!');
        fetchStandardFees();
        setLoading(false);
      } catch (error: any) {
        console.error('Failed to delete standard fee:', error);
        setError(error.response?.data?.detail || 'Failed to delete standard fee');
        setLoading(false);
      }
    }
  };
  
  // If user is not admin, redirect or show access denied
  if (!isAdmin) {
    return (
      <Container>
        <Typography variant="h4" component="h1" gutterBottom>
          Access Denied
        </Typography>
        <Typography>
          You do not have permission to access this page.
        </Typography>
      </Container>
    );
  }
  
  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Standard Fees Management
      </Typography>
      
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      <Box sx={{ mb: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleDialogOpen()}
        >
          Add Standard Fee
        </Button>
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : standardFees.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Institute</TableCell>
                <TableCell>Course</TableCell>
                <TableCell>Semester</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {standardFees.map((fee: StandardFee) => (
                <TableRow key={fee.id}>
                  <TableCell>{fee.course?.institute?.name || 'N/A'}</TableCell>
                  <TableCell>{fee.course?.name || 'N/A'}</TableCell>
                  <TableCell>{fee.semester?.name || 'N/A'}</TableCell>
                  <TableCell>{fee.name}</TableCell>
                  <TableCell>${fee.amount.toFixed(2)}</TableCell>
                  <TableCell>{fee.description || 'N/A'}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={() => handleDialogOpen(fee)}
                      sx={{ mr: 1 }}
                    >
                      Edit
                    </Button>
                    <Button
                      size="small"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => handleDelete(fee.id)}
                    >
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Typography variant="body1">No standard fees found.</Typography>
      )}
      
      {/* Standard Fee Dialog */}
      <Dialog open={dialogOpen} onClose={handleDialogClose}>
        <DialogTitle>{editMode ? 'Edit Standard Fee' : 'Add Standard Fee'}</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="dense">
            <InputLabel>Course</InputLabel>
            <Select
              name="course_id"
              value={String(feeData.course_id)}
              onChange={handleSelectChange}
              required
            >
              <MenuItem value={0}>Select Course</MenuItem>
              {courses.map((course: Course) => (
                <MenuItem key={course.id} value={course.id}>
                  {course.institute?.name} - {course.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="dense">
            <InputLabel>Semester</InputLabel>
            <Select
              name="semester_id"
              value={String(feeData.semester_id)}
              onChange={handleSelectChange}
              required
              disabled={!feeData.course_id}
            >
              <MenuItem value={0}>Select Semester</MenuItem>
              {filteredSemesters.map((semester: Semester) => (
                <MenuItem key={semester.id} value={semester.id}>
                  {semester.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            margin="dense"
            label="Fee Name"
            type="text"
            fullWidth
            name="name"
            value={feeData.name}
            onChange={handleTextFieldChange}
            required
          />
          
          <TextField
            margin="dense"
            label="Amount"
            type="number"
            fullWidth
            name="amount"
            value={feeData.amount}
            onChange={handleTextFieldChange}
            required
          />
          
          <TextField
            margin="dense"
            label="Description"
            type="text"
            fullWidth
            name="description"
            value={feeData.description}
            onChange={handleTextFieldChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default StandardFeesPage;
