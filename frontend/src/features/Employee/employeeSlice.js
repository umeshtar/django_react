import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authFetch } from '../../helpers/fetch'
import { AxiosError } from 'axios'

export const fetchEmployees = createAsyncThunk('employee/fetchEmployees', async () => {
    const res = await authFetch.get('/employee/', { params: { get_crud_configs: true } })
    return res.data
})

export const fetchSingleEmployee = createAsyncThunk('employee/fetchSingleEmployee', async (data) => {
    const res = await authFetch.get('/employee/', { params: { action: 'fetch_record', is_form: true, ...data } })
    return res.data
})

export const createEmployee = createAsyncThunk('employee/createEmployee', async (data, { rejectWithValue }) => {
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

export const updateEmployee = createAsyncThunk('employee/updateEmployee', async (data, { rejectWithValue }) => {
    try {
        const res = await authFetch.put('/employee/', { ...data })
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

export const deleteEmployee = createAsyncThunk('employee/deleteEmployee', async (data, { rejectWithValue }) => {
    try {
        const res = await authFetch.delete('/employee/', { params: { ...data } })
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

const isPending = (action) => action.type.endsWith('pending')
const isFulfilled = (action) => action.type.endsWith('fulfilled')
const isRejected = (action) => action.type.endsWith('rejected')

export const employeeSlice = createSlice({
    name: 'employee',
    initialState: {
        isLoading: false,
        title: undefined,
        data: undefined,
        fields: undefined,
        formConfigs: undefined,
        formErrors: undefined,
        resetForm: undefined,
        fetchedRecord: undefined,
    },
    reducers: {
        formResetDone: (state, action) => {
            state.formErrors = undefined
            state.resetForm = undefined
            state.fetchedRecord = undefined
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchEmployees.pending, (state, action) => {
                console.log('fetchEmployees.pending')
            })
            .addCase(fetchEmployees.fulfilled, (state, action) => {
                state.title = action.payload.title
                state.data = action.payload.data
                state.fields = action.payload.fields
                state.formConfigs = action.payload.form_configs
            })
            .addCase(fetchEmployees.rejected, (state, action) => {
                console.log('fetchEmployees.rejected')
            })

            .addCase(createEmployee.pending, (state, action) => {
                console.log('createEmployee.pending')
            })
            .addCase(createEmployee.fulfilled, (state, action) => {
                if (action.payload.message) alert(action.payload.message)
                if (action.payload.data) state.data.push(action.payload.data)
                state.resetForm = true
                state.formErrors = undefined
            })
            .addCase(createEmployee.rejected, (state, action) => {
                if (action.payload.error) alert(action.payload.error)
                if (action.payload.form_errors) state.formErrors = action.payload.form_errors
            })

            .addCase(fetchSingleEmployee.pending, (state, action) => {
                console.log('fetchSingleEmployee.pending')
            })
            .addCase(fetchSingleEmployee.fulfilled, (state, action) => {
                state.fetchedRecord = action.payload.data
                state.formErrors = undefined
            })
            .addCase(fetchSingleEmployee.rejected, (state, action) => {
                console.log('fetchSingleEmployee.rejected')
            })

            .addCase(updateEmployee.pending, (state, action) => {
                console.log('updateEmployee.pending')
            })
            .addCase(updateEmployee.fulfilled, (state, action) => {
                if (action.payload.message) alert(action.payload.message)
                if (action.payload.data) {
                    state.data = state.data.map(obj => obj.rec_id === action.payload.data.rec_id ? action.payload.data : obj)
                }
                state.resetForm = true
                state.fetchedRecord = undefined
                state.formErrors = undefined
            })
            .addCase(updateEmployee.rejected, (state, action) => {
                if (action.payload.error) alert(action.payload.error)
                if (action.payload.form_errors) state.formErrors = action.payload.form_errors
            })

            .addCase(deleteEmployee.pending, (state, action) => {
                console.log('deleteEmployee.pending')
            })
            .addCase(deleteEmployee.fulfilled, (state, action) => {
                state.data = state.data.filter(obj => !action.payload.ids.includes(obj.rec_id))
            })
            .addCase(deleteEmployee.rejected, (state, action) => {
                if (action.payload.error) alert(action.payload.error)
            })

            .addMatcher(isPending, (state, action) => {
                console.log('Matched Actions for Pending')
                console.log(action.type)
            })
            .addMatcher(isFulfilled, (state, action) => {
                console.log('Matched Actions for Fulfilled')
                console.log(action.type)
            })
            .addMatcher(isRejected, (state, action) => {
                console.log('Matched Actions for Rejected')
                console.log(action.type)
            })
    }
})

export const { formResetDone } = employeeSlice.actions
export default employeeSlice.reducer



