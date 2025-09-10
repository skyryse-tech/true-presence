# 🚀 **Face Attendance System API Documentation**

## 📋 **API Overview**

Base URL: `https://yourdomain.com/api/v1/`
Authentication: JWT Bearer Token
Content-Type: `application/json`

---

## 🔐 **Authentication Endpoints**

### POST `/auth/login/`
Login user and get JWT token
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "faculty",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### POST `/auth/refresh/`
Refresh JWT token
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### POST `/auth/logout/`
Logout user (blacklist token)
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 👥 **User Management Endpoints**

### GET `/users/`
List all users (Admin only)
**Query Parameters:**
- `role`: Filter by role (faculty, student, admin)
- `department`: Filter by department
- `search`: Search by name or email
- `page`: Page number
- `page_size`: Items per page (default: 20)

**Response:**
```json
{
  "count": 4250,
  "next": "https://yourdomain.com/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "employee_id": "FAC001",
      "email": "john.doe@college.edu",
      "first_name": "John",
      "last_name": "Doe",
      "role": "faculty",
      "department": "Computer Science",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-03-15T08:45:00Z",
      "face_enrolled": true
    }
  ]
}
```

### POST `/users/`
Create new user
```json
{
  "employee_id": "STU1234",
  "email": "jane.smith@student.college.edu",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "student",
  "department": "Computer Science",
  "password": "secure_password123"
}
```

### GET `/users/{id}/`
Get user details

### PUT `/users/{id}/`
Update user information

### DELETE `/users/{id}/`
Deactivate user

---

## 👤 **Face Recognition Endpoints**

### POST `/face/enroll/`
Enroll user's face with 3 photos
```json
{
  "employee_id": "FAC001",
  "images": [
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
  ],
  "quality_check": true
}
```
**Response:**
```json
{
  "task_id": "enroll_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "message": "Face enrollment task queued successfully"
}
```

### GET `/face/enroll/status/{task_id}/`
Check enrollment status
**Response:**
```json
{
  "task_id": "enroll_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "result": {
    "success": true,
    "faces_detected": 3,
    "quality_scores": [0.92, 0.89, 0.94],
    "template_created": true,
    "message": "Face template created successfully"
  },
  "processing_time": 2.34
}
```

### POST `/face/verify/`
Verify face for attendance
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "camera_id": "CAM001",
  "location": "Main Building Entrance"
}
```
**Response:**
```json
{
  "task_id": "verify_b2c3d4e5-f6g7-8901-bcde-f23456789012",
  "status": "queued",
  "estimated_time": 1.5
}
```

### GET `/face/verify/status/{task_id}/`
Check verification status
**Response:**
```json
{
  "task_id": "verify_b2c3d4e5-f6g7-8901-bcde-f23456789012",
  "status": "completed",
  "result": {
    "recognized": true,
    "employee_id": "FAC001",
    "name": "John Doe",
    "confidence": 0.97,
    "similarity_score": 0.92,
    "is_live": true,
    "anti_spoof_score": 0.98,
    "attendance_logged": true,
    "timestamp": "2024-03-15T08:45:23Z"
  },
  "processing_time": 0.89
}
```

### POST `/face/bulk-verify/`
Batch verification for multiple faces
```json
{
  "images": [
    {
      "id": "frame_001",
      "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
      "camera_id": "CAM001"
    }
  ],
  "options": {
    "max_faces": 10,
    "quality_threshold": 0.8,
    "similarity_threshold": 0.85
  }
}
```

---

## 📊 **Attendance Endpoints**

### GET `/attendance/logs/`
Get attendance logs
**Query Parameters:**
- `employee_id`: Filter by employee
- `date_from`: Start date (YYYY-MM-DD)
- `date_to`: End date (YYYY-MM-DD)
- `camera_id`: Filter by camera
- `department`: Filter by department
- `page`: Page number

**Response:**
```json
{
  "count": 1250,
  "results": [
    {
      "id": 12345,
      "employee": {
        "id": 1,
        "employee_id": "FAC001",
        "name": "John Doe",
        "department": "Computer Science"
      },
      "timestamp": "2024-03-15T08:45:23Z",
      "camera": {
        "id": "CAM001",
        "name": "Main Entrance",
        "location": "Building A"
      },
      "confidence": 0.97,
      "verification_time": 0.89
    }
  ]
}
```

### GET `/attendance/summary/`
Attendance summary statistics
**Query Parameters:**
- `period`: daily, weekly, monthly, yearly
- `date_from`: Start date
- `date_to`: End date
- `department`: Filter by department

**Response:**
```json
{
  "period": "daily",
  "date": "2024-03-15",
  "total_attendances": 3847,
  "unique_persons": 3521,
  "departments": {
    "Computer Science": 847,
    "Mathematics": 623,
    "Physics": 445
  },
  "hourly_distribution": {
    "08:00": 1247,
    "09:00": 892,
    "10:00": 567
  }
}
```

### POST `/attendance/mark/`
Manual attendance marking (Admin only)
```json
{
  "employee_id": "FAC001",
  "timestamp": "2024-03-15T08:45:00Z",
  "reason": "Manual entry due to system issue",
  "marked_by": "admin@college.edu"
}
```

---

## 📹 **Camera Management Endpoints**

### GET `/cameras/`
List all cameras
**Response:**
```json
{
  "results": [
    {
      "id": "CAM001",
      "name": "Main Entrance",
      "location": "Building A - Ground Floor",
      "ip_address": "192.168.1.100",
      "rtsp_url": "rtsp://192.168.1.100:554/stream",
      "status": "online",
      "last_seen": "2024-03-15T08:50:00Z",
      "resolution": "1920x1080",
      "fps": 30,
      "is_active": true
    }
  ]
}
```

### POST `/cameras/`
Add new camera
```json
{
  "id": "CAM002",
  "name": "Library Entrance",
  "location": "Library Building",
  "ip_address": "192.168.1.101",
  "rtsp_url": "rtsp://admin:password@192.168.1.101:554/stream",
  "username": "admin",
  "password": "camera_password"
}
```

### GET `/cameras/{camera_id}/stream/`
Get camera stream URL

### POST `/cameras/{camera_id}/test/`
Test camera connection

### GET `/cameras/{camera_id}/health/`
Camera health status
**Response:**
```json
{
  "camera_id": "CAM001",
  "status": "online",
  "uptime": "48 hours",
  "last_frame": "2024-03-15T08:50:15Z",
  "quality_score": 0.92,
  "bandwidth_usage": "2.3 Mbps",
  "error_count": 0
}
```

---

## 📈 **Reports & Analytics Endpoints**

### GET `/reports/attendance/`
Generate attendance report
**Query Parameters:**
- `format`: json, pdf, excel
- `period`: daily, weekly, monthly
- `date_from`: Start date
- `date_to`: End date
- `department`: Filter by department
- `employee_ids`: Comma-separated employee IDs

**Response (JSON):**
```json
{
  "report_id": "RPT_20240315_001",
  "generated_at": "2024-03-15T09:00:00Z",
  "period": "monthly",
  "date_range": "2024-02-01 to 2024-02-29",
  "total_employees": 4250,
  "attendance_rate": 0.94,
  "department_stats": {
    "Computer Science": {
      "total_employees": 1250,
      "attendance_rate": 0.96,
      "avg_daily_attendance": 1198
    }
  }
}
```

### GET `/reports/analytics/real-time/`
Real-time analytics dashboard data
**Response:**
```json
{
  "current_occupancy": 2847,
  "today_attendance": 3521,
  "peak_hour": "09:00",
  "avg_processing_time": 0.94,
  "system_health": {
    "api_response_time": 0.15,
    "ai_worker_status": "healthy",
    "database_connections": 45,
    "queue_size": 12
  },
  "camera_status": {
    "online": 28,
    "offline": 2,
    "errors": 0
  }
}
```

### GET `/reports/patterns/`
Attendance pattern analysis
**Response:**
```json
{
  "daily_patterns": {
    "monday": {"avg_attendance": 3847, "peak_hour": "09:00"},
    "tuesday": {"avg_attendance": 3921, "peak_hour": "09:00"}
  },
  "seasonal_trends": {
    "spring": 0.94,
    "summer": 0.67,
    "fall": 0.92,
    "winter": 0.89
  },
  "predictions": {
    "next_week_attendance": 18547,
    "confidence": 0.87
  }
}
```

---

## ⚙️ **System Management Endpoints**

### GET `/system/health/`
System health check
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-15T09:00:00Z",
  "services": {
    "database": {"status": "healthy", "response_time": 0.05},
    "redis": {"status": "healthy", "memory_usage": "45%"},
    "rabbitmq": {"status": "healthy", "queue_size": 12},
    "ai_workers": {"status": "healthy", "active_workers": 4}
  },
  "performance": {
    "avg_api_response_time": 0.15,
    "requests_per_minute": 342,
    "error_rate": 0.001
  }
}
```

### GET `/system/metrics/`
System performance metrics
**Response:**
```json
{
  "cpu_usage": 0.65,
  "memory_usage": 0.78,
  "disk_usage": 0.45,
  "network_io": {
    "bytes_sent": 1024000000,
    "bytes_received": 2048000000
  },
  "face_processing": {
    "total_processed": 25847,
    "avg_processing_time": 0.94,
    "success_rate": 0.997
  }
}
```

### POST `/system/maintenance/`
Trigger maintenance tasks (Admin only)
```json
{
  "task": "cleanup_old_logs",
  "parameters": {
    "days_to_keep": 30
  }
}
```

---

## 🔐 **Security Endpoints**

### GET `/security/audit-logs/`
Security audit logs (Admin only)
**Query Parameters:**
- `action`: login, logout, enrollment, verification
- `user_id`: Filter by user
- `date_from`: Start date
- `severity`: info, warning, error

**Response:**
```json
{
  "results": [
    {
      "id": 12345,
      "timestamp": "2024-03-15T08:45:23Z",
      "action": "face_verification",
      "user_id": "FAC001",
      "ip_address": "192.168.1.50",
      "user_agent": "FaceAttendance/1.0",
      "success": true,
      "details": {
        "camera_id": "CAM001",
        "confidence": 0.97,
        "processing_time": 0.89
      }
    }
  ]
}
```

### POST `/security/report-incident/`
Report security incident
```json
{
  "type": "spoofing_attempt",
  "camera_id": "CAM001",
  "timestamp": "2024-03-15T08:45:23Z",
  "description": "Multiple failed liveness checks",
  "severity": "medium",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

---

## 📱 **Mobile API Endpoints**

### GET `/mobile/profile/`
Get user profile for mobile app
**Response:**
```json
{
  "employee_id": "FAC001",
  "name": "John Doe",
  "department": "Computer Science",
  "face_enrolled": true,
  "today_attendance": "08:45",
  "this_week_days": 4,
  "attendance_rate": 0.94
}
```

### POST `/mobile/check-in/`
Mobile check-in (with selfie)
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "timestamp": "2024-03-15T08:45:23Z"
}
```

---

## 📝 **Response Codes**

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## 🔄 **Webhook Endpoints**

### POST `/webhooks/attendance/`
Real-time attendance notifications
```json
{
  "event": "attendance_logged",
  "timestamp": "2024-03-15T08:45:23Z",
  "data": {
    "employee_id": "FAC001",
    "name": "John Doe",
    "camera_id": "CAM001",
    "confidence": 0.97
  }
}
```

---

## 📊 **Rate Limiting**

| Endpoint Category | Rate Limit |
|------------------|------------|
| Authentication | 5 requests/minute |
| Face Verification | 100 requests/minute |
| Reports | 10 requests/minute |
| General API | 1000 requests/hour |

---

## 🔧 **SDKs & Integration Examples**

### Python SDK Example
```python
from face_attendance_sdk import FaceAttendanceClient

client = FaceAttendanceClient(
    base_url="https://yourdomain.com/api/v1/",
    api_key="your_api_key"
)

# Enroll face
result = client.face.enroll(
    employee_id="FAC001",
    images=[image1, image2, image3]
)

# Verify face
verification = client.face.verify(image=camera_frame)
```

### JavaScript SDK Example
```javascript
import { FaceAttendanceAPI } from 'face-attendance-js-sdk';

const api = new FaceAttendanceAPI({
  baseURL: 'https://yourdomain.com/api/v1/',
  apiKey: 'your_api_key'
});

// Real-time verification
const result = await api.face.verify({
  image: cameraFrame,
  cameraId: 'CAM001'
});
```
