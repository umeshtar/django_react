import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authFetch } from '../../helpers/fetch'

export const fetchEmployees = createAsyncThunk('employee/fetchEmployees', async () => {
    const res = await authFetch.get('/employee/', { params: { get_crud_configs: true } })
    return res.data
})

export const employeeSlice = createSlice({
    name: 'employee',
    initialState: {
        data: [],
        fields: [],
    },
    reducers: {
        addEmployee: (state, action) => {
            state.data.push(action.payload)
        }
    },
    extraReducers: (builder) => {
        builder.addCase(fetchEmployees.fulfilled, (state, action) => {
            state.data = action.payload.data
            state.fields = action.payload.fields
        })
    }
})

export const { addEmployee } = employeeSlice.actions
export default employeeSlice.reducer



