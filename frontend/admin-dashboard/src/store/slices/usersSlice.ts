import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { usersAPI } from '../../services/api';

interface User {
  id: number;
  employee_id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  department: string;
  face_enrolled: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string;
}

interface UsersState {
  users: User[];
  loading: boolean;
  error: string | null;
  totalCount: number;
}

const initialState: UsersState = {
  users: [],
  loading: false,
  error: null,
  totalCount: 0,
};

export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (params?: any) => {
    const response = await usersAPI.getUsers(params);
    return response.data;
  }
);

export const createUser = createAsyncThunk(
  'users/createUser',
  async (userData: any) => {
    const response = await usersAPI.createUser(userData);
    return response.data;
  }
);

export const updateUser = createAsyncThunk(
  'users/updateUser',
  async ({ id, userData }: { id: string; userData: any }) => {
    const response = await usersAPI.updateUser(id, userData);
    return response.data;
  }
);

export const deleteUser = createAsyncThunk(
  'users/deleteUser',
  async (id: string) => {
    await usersAPI.deleteUser(id);
    return id;
  }
);

const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch users
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload.results;
        state.totalCount = action.payload.count;
        state.error = null;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch users';
      })
      // Create user
      .addCase(createUser.fulfilled, (state, action) => {
        state.users.unshift(action.payload);
        state.totalCount += 1;
      })
      // Update user
      .addCase(updateUser.fulfilled, (state, action) => {
        const index = state.users.findIndex(user => user.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
      })
      // Delete user
      .addCase(deleteUser.fulfilled, (state, action) => {
        state.users = state.users.filter(user => user.id.toString() !== action.payload);
        state.totalCount -= 1;
      });
  },
});

export const { clearError } = usersSlice.actions;
export default usersSlice.reducer;
