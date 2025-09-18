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
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { camerasAPI } from '../../services/api';

const Cameras: React.FC = () => {
  const { data: cameras, isLoading, error } = useQuery({
    queryKey: ['cameras'],
    queryFn: () => camerasAPI.getCameras(),
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
        Failed to load cameras. Please try again later.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Camera Management
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Camera ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>IP Address</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Last Seen</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {cameras?.data.results.map((camera: any) => (
              <TableRow key={camera.id}>
                <TableCell>{camera.id}</TableCell>
                <TableCell>{camera.name}</TableCell>
                <TableCell>{camera.location}</TableCell>
                <TableCell>{camera.camera_type}</TableCell>
                <TableCell>{camera.ip_address}</TableCell>
                <TableCell>
                  <Chip
                    label={camera.status}
                    color={camera.is_online ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {camera.last_seen ? new Date(camera.last_seen).toLocaleString() : 'Never'}
                </TableCell>
                <TableCell>
                  <IconButton color="primary">
                    <PlayIcon />
                  </IconButton>
                  <IconButton color="secondary">
                    <SettingsIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Cameras;
