import React from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Badge,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { notificationsAPI } from '../../services/api';

const Notifications: React.FC = () => {
  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsAPI.getNotifications(),
  });

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'success':
        return <CheckCircleIcon color="success" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  if (isLoading) {
    return <Typography>Loading notifications...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        System Notifications
      </Typography>
      
      <Paper>
        <List>
          {notifications?.data.map((notification: any) => (
            <ListItem key={notification.id} divider>
              <ListItemIcon>
                {getNotificationIcon(notification.notification_type)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="subtitle1">
                      {notification.title}
                    </Typography>
                    <Chip
                      label={notification.priority}
                      color={getPriorityColor(notification.priority) as any}
                      size="small"
                    />
                    {!notification.is_read && (
                      <Badge color="primary" variant="dot" />
                    )}
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      {notification.message}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {new Date(notification.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default Notifications;
