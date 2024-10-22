import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authFetch } from '../../helpers/fetch'

export const fetchEmployees = createAsyncThunk('employee/fetchEmployees', async () => {
    const res = await authFetch.get('/employee/', { params: { get_crud_configs: true } })
    return res.data
})

export const submitEmployeeForm = createAsyncThunk('employee/SubmitEmployeeForm', async (data) => {
    const res = await authFetch.post('/employee/', { ...data })
    return res.data
})

export const employeeSlice = createSlice({
    name: 'employee',
    initialState: {
        title: undefined,
        data: undefined,
        fields: undefined,
        formConfigs: undefined,
    },
    reducers: {
        addEmployee: (state, action) => {
            state.data.push(action.payload)
        }
    },
    extraReducers: (builder) => {
        builder.addCase(fetchEmployees.fulfilled, (state, action) => {
            state.title = action.payload.title
            state.data = action.payload.data
            state.fields = action.payload.fields
            state.formConfigs = action.payload.form_configs
        })
        builder.addCase(submitEmployeeForm.fulfilled, (state, action) => {
            state.data.push(action.payload.data)
        })
        builder.addMatcher(submitEmployeeForm.fulfilled, (state, action) => {
            action?.payload?.Success && alert(action.payload.Success)
        })
    }
})

export const { addEmployee } = employeeSlice.actions
export default employeeSlice.reducer



