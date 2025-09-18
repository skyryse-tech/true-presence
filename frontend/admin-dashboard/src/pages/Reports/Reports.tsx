import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  AccessTime as AccessTimeIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { reportsAPI } from '../../services/api';

const Reports: React.FC = () => {
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['real-time-analytics'],
    queryFn: () => reportsAPI.getRealTimeAnalytics(),
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
        Failed to load reports. Please try again later.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports & Analytics
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Current Occupancy
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {analytics?.data.current_occupancy || 0}
                  </Typography>
                </Box>
                <AssessmentIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Today's Attendance
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {analytics?.data.today_attendance || 0}
                  </Typography>
                </Box>
                <TrendingUpIcon sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Peak Hour
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {analytics?.data.peak_hour || 'N/A'}
                  </Typography>
                </Box>
                <AccessTimeIcon sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Avg Processing Time
                  </Typography>
                  <Typography variant="h4" component="h2">
                    {analytics?.data.avg_processing_time?.toFixed(2) || 0}s
                  </Typography>
                </Box>
                <PeopleIcon sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Health
            </Typography>
            <Box>
              <Typography variant="body2" color="textSecondary">
                API Response Time: {analytics?.data.system_health?.api_response_time || 0}ms
              </Typography>
              <Typography variant="body2" color="textSecondary">
                AI Worker Status: {analytics?.data.system_health?.ai_worker_status || 'Unknown'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Database Connections: {analytics?.data.system_health?.database_connections || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Queue Size: {analytics?.data.system_health?.queue_size || 0}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Camera Status
            </Typography>
            <Box>
              <Typography variant="body2" color="textSecondary">
                Online: {analytics?.data.camera_status?.online || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Offline: {analytics?.data.camera_status?.offline || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Errors: {analytics?.data.camera_status?.errors || 0}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Reports;
