import React from 'react';
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
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { attendanceAPI } from '../../services/api';

const Attendance: React.FC = () => {
  const { data: attendance, isLoading, error } = useQuery({
    queryKey: ['attendance-logs'],
    queryFn: () => attendanceAPI.getAttendanceLogs(),
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load attendance data. Please try again later.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Attendance Logs
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell>Employee ID</TableCell>
              <TableCell>Timestamp</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Camera</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Confidence</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {attendance?.data.results.map((log: any) => (
              <TableRow key={log.id}>
                <TableCell>{log.user_name}</TableCell>
                <TableCell>{log.user}</TableCell>
                <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                <TableCell>
                  <Chip
                    label={log.attendance_type}
                    color="primary"
                    size="small"
                  />
                </TableCell>
                <TableCell>{log.camera_id || 'N/A'}</TableCell>
                <TableCell>{log.location || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={`${(log.confidence * 100).toFixed(1)}%`}
                    color={log.confidence > 0.8 ? 'success' : log.confidence > 0.6 ? 'warning' : 'error'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Attendance;
