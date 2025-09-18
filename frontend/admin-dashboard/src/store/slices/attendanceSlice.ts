import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { attendanceAPI } from '../../services/api';

interface AttendanceLog {
  id: number;
  user: string;
  user_name: string;
  timestamp: string;
  attendance_type: string;
  camera_id: string;
  location: string;
  confidence: number;
  verification_time: number;
  face_position: any;
  photo_path: string;
  notes: string;
}

interface AttendanceState {
  logs: AttendanceLog[];
  stats: any;
  todayAttendance: AttendanceLog[];
  loading: boolean;
  error: string | null;
  totalCount: number;
}

const initialState: AttendanceState = {
  logs: [],
  stats: null,
  todayAttendance: [],
  loading: false,
  error: null,
  totalCount: 0,
};

export const fetchAttendanceLogs = createAsyncThunk(
  'attendance/fetchLogs',
  async (params?: any) => {
    const response = await attendanceAPI.getAttendanceLogs(params);
    return response.data;
  }
);

export const fetchAttendanceStats = createAsyncThunk(
  'attendance/fetchStats',
  async (params?: any) => {
    const response = await attendanceAPI.getAttendanceStats(params);
    return response.data;
  }
);

export const fetchTodayAttendance = createAsyncThunk(
  'attendance/fetchToday',
  async () => {
    const response = await attendanceAPI.getTodayAttendance();
    return response.data;
  }
);

export const markManualAttendance = createAsyncThunk(
  'attendance/markManual',
  async (data: any) => {
    const response = await attendanceAPI.markManualAttendance(data);
    return response.data;
  }
);

const attendanceSlice = createSlice({
  name: 'attendance',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch attendance logs
      .addCase(fetchAttendanceLogs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAttendanceLogs.fulfilled, (state, action) => {
        state.loading = false;
        state.logs = action.payload.results;
        state.totalCount = action.payload.count;
        state.error = null;
      })
      .addCase(fetchAttendanceLogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch attendance logs';
      })
      // Fetch attendance stats
      .addCase(fetchAttendanceStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      })
      // Fetch today's attendance
      .addCase(fetchTodayAttendance.fulfilled, (state, action) => {
        state.todayAttendance = action.payload;
      })
      // Mark manual attendance
      .addCase(markManualAttendance.fulfilled, (state, action) => {
        state.logs.unshift(action.payload);
        state.totalCount += 1;
      });
  },
});

export const { clearError } = attendanceSlice.actions;
export default attendanceSlice.reducer;
