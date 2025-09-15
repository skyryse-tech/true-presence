import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { camerasAPI } from '../../services/api';

interface Camera {
  id: string;
  name: string;
  location: string;
  camera_type: string;
  ip_address: string;
  rtsp_url: string;
  status: string;
  is_active: boolean;
  last_seen: string;
  created_at: string;
  updated_at: string;
  stream_url: string;
  is_online: boolean;
}

interface CamerasState {
  cameras: Camera[];
  loading: boolean;
  error: string | null;
  statistics: any;
}

const initialState: CamerasState = {
  cameras: [],
  loading: false,
  error: null,
  statistics: null,
};

export const fetchCameras = createAsyncThunk(
  'cameras/fetchCameras',
  async () => {
    const response = await camerasAPI.getCameras();
    return response.data;
  }
);

export const createCamera = createAsyncThunk(
  'cameras/createCamera',
  async (cameraData: any) => {
    const response = await camerasAPI.createCamera(cameraData);
    return response.data;
  }
);

export const updateCamera = createAsyncThunk(
  'cameras/updateCamera',
  async ({ id, cameraData }: { id: string; cameraData: any }) => {
    const response = await camerasAPI.updateCamera(id, cameraData);
    return response.data;
  }
);

export const deleteCamera = createAsyncThunk(
  'cameras/deleteCamera',
  async (id: string) => {
    await camerasAPI.deleteCamera(id);
    return id;
  }
);

export const testCamera = createAsyncThunk(
  'cameras/testCamera',
  async (id: string) => {
    const response = await camerasAPI.testCamera(id);
    return { id, result: response.data };
  }
);

export const fetchCameraStatistics = createAsyncThunk(
  'cameras/fetchStatistics',
  async () => {
    const response = await camerasAPI.getCameraStatistics();
    return response.data;
  }
);

const camerasSlice = createSlice({
  name: 'cameras',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch cameras
      .addCase(fetchCameras.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCameras.fulfilled, (state, action) => {
        state.loading = false;
        state.cameras = action.payload.results;
        state.error = null;
      })
      .addCase(fetchCameras.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch cameras';
      })
      // Create camera
      .addCase(createCamera.fulfilled, (state, action) => {
        state.cameras.push(action.payload);
      })
      // Update camera
      .addCase(updateCamera.fulfilled, (state, action) => {
        const index = state.cameras.findIndex(camera => camera.id === action.payload.id);
        if (index !== -1) {
          state.cameras[index] = action.payload;
        }
      })
      // Delete camera
      .addCase(deleteCamera.fulfilled, (state, action) => {
        state.cameras = state.cameras.filter(camera => camera.id !== action.payload);
      })
      // Test camera
      .addCase(testCamera.fulfilled, (state, action) => {
        const index = state.cameras.findIndex(camera => camera.id === action.payload.id);
        if (index !== -1) {
          state.cameras[index].status = action.payload.result.camera_status;
        }
      })
      // Fetch statistics
      .addCase(fetchCameraStatistics.fulfilled, (state, action) => {
        state.statistics = action.payload;
      });
  },
});

export const { clearError } = camerasSlice.actions;
export default camerasSlice.reducer;
