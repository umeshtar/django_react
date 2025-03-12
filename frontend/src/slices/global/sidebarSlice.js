import { createSlice } from '@reduxjs/toolkit'
import { baseAsyncThunk } from '../crud/crudSlice';
import { authFetch } from '../../helpers/fetch';

export function fetchSideBarData() {
    return baseAsyncThunk({ name: 'sidebar', action: 'fetchSideBarData', func: (data) => authFetch.get('permission/sidebar/') })
}

const sidebarSlice = createSlice({
    name: 'sidebar',
    initialState: {
        data: [],
        all_modules: null,
        is_permission_manager: false,
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase('sidebar/fetchSideBarData/fulfilled', (state, action) => {
                state.data = action.payload.data
                state.all_modules = action.payload.all_modules
                state.is_permission_manager = action.payload.is_permission_manager
            })
    }
})

export default sidebarSlice.reducer


