import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login/', credentials),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/auth/profile/'),
  refreshToken: (refresh: string) => api.post('/auth/token/refresh/', { refresh }),
};

// Users API
export const usersAPI = {
  getUsers: (params?: any) => api.get('/users/', { params }),
  getUser: (id: string) => api.get(`/users/${id}/`),
  createUser: (userData: any) => api.post('/users/', userData),
  updateUser: (id: string, userData: any) => api.put(`/users/${id}/`, userData),
  deleteUser: (id: string) => api.delete(`/users/${id}/`),
};

// Attendance API
export const attendanceAPI = {
  getAttendanceLogs: (params?: any) => api.get('/attendance/logs/', { params }),
  getAttendanceStats: (params?: any) => api.get('/attendance/stats/', { params }),
  getTodayAttendance: () => api.get('/attendance/today/'),
  markManualAttendance: (data: any) => api.post('/attendance/mark/', data),
};

// Face Recognition API
export const faceRecognitionAPI = {
  enrollFace: (data: { employee_id: string; images: string[]; quality_check: boolean }) =>
    api.post('/face/enroll/', data),
  getEnrollmentStatus: (taskId: string) => api.get(`/face/enroll/status/${taskId}/`),
  verifyFace: (data: { image: string; camera_id?: string; location?: string }) =>
    api.post('/face/verify/', data),
  getVerificationStatus: (taskId: string) => api.get(`/face/verify/status/${taskId}/`),
  bulkVerify: (data: { images: any[]; options?: any }) => api.post('/face/bulk-verify/', data),
};

// Cameras API
export const camerasAPI = {
  getCameras: () => api.get('/cameras/'),
  getCamera: (id: string) => api.get(`/cameras/${id}/`),
  createCamera: (cameraData: any) => api.post('/cameras/', cameraData),
  updateCamera: (id: string, cameraData: any) => api.put(`/cameras/${id}/`, cameraData),
  deleteCamera: (id: string) => api.delete(`/cameras/${id}/`),
  testCamera: (id: string) => api.post(`/cameras/${id}/test/`),
  getCameraHealth: (id: string) => api.get(`/cameras/${id}/health/`),
  getCameraStream: (id: string) => api.get(`/cameras/${id}/stream/`),
  getCameraStatistics: () => api.get('/cameras/statistics/'),
};

// Reports API
export const reportsAPI = {
  getAttendanceReport: (params?: any) => api.get('/reports/attendance/', { params }),
  getRealTimeAnalytics: () => api.get('/reports/analytics/real-time/'),
  getPatternAnalysis: () => api.get('/reports/patterns/'),
  exportReport: (params?: any) => api.get('/reports/export/', { params }),
};

// Notifications API
export const notificationsAPI = {
  getNotifications: () => api.get('/notifications/'),
  markNotificationRead: (id: number) => api.post(`/notifications/${id}/read/`),
  markAllNotificationsRead: () => api.post('/notifications/mark-all-read/'),
  getUnreadCount: () => api.get('/notifications/unread-count/'),
};

// Admin Dashboard API
export const adminAPI = {
  getDashboardStats: () => api.get('/admin/stats/'),
  getSystemHealth: () => api.get('/admin/health/'),
  getRecentActivity: () => api.get('/admin/activity/'),
  triggerMaintenance: (data: any) => api.post('/admin/maintenance/', data),
};

export default api;
