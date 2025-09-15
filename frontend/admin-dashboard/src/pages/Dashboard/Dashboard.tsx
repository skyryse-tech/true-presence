import React, { useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  People as PeopleIcon,
  AccessTime as AccessTimeIcon,
  Videocam as VideocamIcon,
  Face as FaceIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '../../services/api';

const Dashboard: React.FC = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => adminAPI.getDashboardStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const StatCard: React.FC<{
    title: string;
    value: number | string;
    icon: React.ReactNode;
    color: string;
  }> = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

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
        Failed to load dashboard data. Please try again later.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard Overview
      </Typography>
      
      <Grid container spacing={3}>
        {/* User Statistics */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats?.data.users.total || 0}
            icon={<PeopleIcon sx={{ color: 'white' }} />}
            color="#1976d2"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Face Enrolled"
            value={stats?.data.users.face_enrolled || 0}
            icon={<FaceIcon sx={{ color: 'white' }} />}
            color="#2e7d32"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Attendance"
            value={stats?.data.attendance.today || 0}
            icon={<AccessTimeIcon sx={{ color: 'white' }} />}
            color="#ed6c02"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Online Cameras"
            value={`${stats?.data.cameras.online || 0}/${stats?.data.cameras.total || 0}`}
            icon={<VideocamIcon sx={{ color: 'white' }} />}
            color="#9c27b0"
          />
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Health
            </Typography>
            <Box>
              <Typography variant="body2" color="textSecondary">
                Enrollment Success Rate: {stats?.data.face_recognition.enrollments.success_rate?.toFixed(1) || 0}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Verification Success Rate: {stats?.data.face_recognition.verifications.success_rate?.toFixed(1) || 0}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Camera Uptime: {stats?.data.cameras.uptime_percentage?.toFixed(1) || 0}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Recent Errors (24h): {stats?.data.system.recent_errors || 0}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Box>
              <Typography variant="body2" color="textSecondary">
                Recent Attendance (24h): {stats?.data.attendance.recent_24h || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Unread Notifications: {stats?.data.system.unread_notifications || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Face Enrollment Rate: {stats?.data.users.enrollment_rate?.toFixed(1) || 0}%
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
