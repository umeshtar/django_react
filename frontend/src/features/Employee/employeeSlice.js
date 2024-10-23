import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authFetch } from '../../helpers/fetch'
import { AxiosError } from 'axios'

export const fetchEmployees = createAsyncThunk('employee/fetchEmployees', async () => {
    const res = await authFetch.get('/employee/', { params: { get_crud_configs: true } })
    return res.data
})

export const submitEmployeeForm = createAsyncThunk('employee/SubmitEmployeeForm', async (data, { rejectWithValue }) => {
    try {
        const res = await authFetch.post('/employee/', { ...data })
        return res.data
    } catch (error) {
        if (error.name === 'AxiosError') {
            return rejectWithValue(error.response.data)
        } else {
            console.log({ error })
            alert('Something Went Wrong!!!')
            return rejectWithValue({ error: 'Something Went Wrong!!!' })
        }
    }
})

export const employeeSlice = createSlice({
    name: 'employee',
    initialState: {
        title: undefined,
        data: undefined,
        fields: undefined,
        formConfigs: undefined,
        formErrors: undefined,
        resetForm: undefined,
    },
    reducers: {
        formResetDone: (state, action) => {
            state.resetForm = undefined
        }
    },
    extraReducers: (builder) => {
        builder.addCase(fetchEmployees.fulfilled, (state, action) => {
            state.title = action.payload.title
            state.data = action.payload.data
            state.fields = action.payload.fields
            state.formConfigs = action.payload.form_configs
        })
            .addCase(submitEmployeeForm.fulfilled, (state, action) => {
                if (action.payload.message) alert(action.payload.message)
                if (action.payload.data) state.data.push(action.payload.data)
                state.resetForm = true
            })
            .addCase(submitEmployeeForm.rejected, (state, action) => {
                if (action.payload.error) alert(action.payload.error)
                if (action.payload.form_errors) state.formErrors = action.payload.form_errors
            })
    }
})

export const { formResetDone } = employeeSlice.actions
export default employeeSlice.reducer



