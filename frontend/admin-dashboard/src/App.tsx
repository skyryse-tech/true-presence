import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout/Layout';
import Login from './pages/Login/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import Users from './pages/Users/Users';
import Attendance from './pages/Attendance/Attendance';
import FaceRecognition from './pages/FaceRecognition/FaceRecognition';
import Cameras from './pages/Cameras/Cameras';
import Reports from './pages/Reports/Reports';
// import Notifications from './pages/Notifications/Notifications';
import { useAppSelector } from './store/hooks';

function App() {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  return (
    <Box sx={{ display: 'flex' }}>
      {isAuthenticated ? (
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/users" element={<Users />} />
            <Route path="/attendance" element={<Attendance />} />
            <Route path="/face-recognition" element={<FaceRecognition />} />
            <Route path="/cameras" element={<Cameras />} />
            <Route path="/reports" element={<Reports />} />
            {/* <Route path="/notifications" element={<Notifications />} /> */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      ) : (
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </Box>
  );
}

export default App;
