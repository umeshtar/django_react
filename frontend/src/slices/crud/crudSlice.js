import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authFetch } from '../../helpers/fetch'
import { set } from 'react-hook-form'

export const FetchDataAsyncThunk = ({ name, url }) => {
    return createAsyncThunk(`${name}/fetchData`, async ({ successCallBack, errorCallBack, ...extraParams } = {}, { rejectWithValue }) => {
        try {
            const response = await authFetch.get(url, { params: { get_crud_configs: true, ...extraParams } })
            if (successCallBack) successCallBack(response)
            return response.data
        } catch (err) {
            if (errorCallBack) errorCallBack(err)
            return rejectWithValue(err)
        }
    })
}

export const FetchSingleRecordAsyncThunk = ({ name, url }) => {
    return createAsyncThunk(`${name}/fetchSingleRecord`, async ({ setAction, setValue, clearErrors, successCallBack, errorCallBack, ...extraParams } = {}, { rejectWithValue }) => {
        try {
            const response = await authFetch.get(url, { params: { action: 'fetch_record', is_form: true, ...extraParams } })
            if (clearErrors) clearErrors()
            if (setValue) {
                Object.entries(response.data.data).forEach(([key, value]) => {
                    setValue(key, value)
                })
            }
            if (setAction) setAction('Update')
            if (successCallBack) successCallBack(response)
            return response.data
        } catch (err) {
            if (errorCallBack) errorCallBack(err)
            return rejectWithValue(err)
        }
    })
}

export const createRecordAsyncThunk = ({ name, url }) => {
    return createAsyncThunk(`${name}/createRecord`, async ({ reset, setError, successCallBack, errorCallBack, ...data } = {}, { rejectWithValue }) => {
        try {
            const response = await authFetch.post(url, data)
            if (response.data.message) alert(response.data.message)
            if (reset) reset()
            if (successCallBack) successCallBack(response.data)
            return response.data
        } catch (err) {
            if (err.name === "AxiosError") {
                if (setError && err.response.data.form_errors) {
                    Object.entries(err.response.data.form_errors).forEach(([key, value]) => {
                        setError(key, { type: 'custom', message: value })
                    })
                }
            }
            if (errorCallBack) errorCallBack(err)
            return rejectWithValue(err.message)
        }
    })
}

export const updateRecordAsyncThunk = ({ name, url }) => {
    return createAsyncThunk(`${name}/updateRecord`, async ({ reset, setError, setAction, successCallBack, errorCallBack, ...data } = {}, { rejectWithValue }) => {
        try {
            const response = await authFetch.put(url, data)
            if (response.data.message) alert(response.data.message)
            if (reset) reset()
            if (setAction) setAction('Create')
            if (successCallBack) successCallBack(response)
            return response.data
        } catch (err) {
            if (err.name === "AxiosError") {
                if (setError && err.response.data.form_errors) {
                    Object.entries(err.response.data.form_errors).forEach(([key, value]) => {
                        setError(key, { type: 'custom', message: value })
                    })
                }
            }
            if (errorCallBack) errorCallBack(err)
            return rejectWithValue(err)
        }
    })
}

export const deleteRecordAsyncThunk = ({ name, url }) => {
    return createAsyncThunk(`${name}/deleteRecord`, async ({ successCallBack, errorCallBack, ...extraParams } = {}, { rejectWithValue }) => {
        try {
            const response = await authFetch.delete(url, { params: extraParams })
            if (successCallBack) successCallBack(response)
            return response.data
        } catch (err) {
            if (errorCallBack) errorCallBack(err)
            return rejectWithValue(err)
        }
    })
}

export const createCrudSlice = ({ name, initialState = {}, reducers = {}, extraReducerCases = {}, extraReducerMatches = {} }) => {
    return createSlice({
        name,
        initialState: {
            title: '',
            data: [],
            tableFields: undefined,
            formFields: undefined,
            ...initialState,
        },
        reducers: { ...reducers },
        extraReducers: (builder) => {
            builder
                .addCase(`${name}/fetchData/fulfilled`, (state, action) => {
                    state.title = action.payload.title
                    state.data = action.payload.data
                    state.tableFields = action.payload.fields
                    state.formFields = action.payload.form_configs
                })
                .addCase(`${name}/createRecord/fulfilled`, (state, action) => {
                    state.data.push(action.payload.data)
                })
                .addCase(`${name}/updateRecord/fulfilled`, (state, action) => {
                    const newData = action.payload.data
                    state.data = state.data.map(obj => obj.rec_id === newData.rec_id ? newData : obj)
                })
                .addCase(`${name}/deleteRecord/fulfilled`, (state, action) => {
                    state.data = state.data.filter(obj => !action.payload.ids.includes(obj.rec_id))
                })
            Object.entries(extraReducerCases).forEach(([type, reducer]) => {
                builder.addCase(type, reducer);
            });
            Object.entries(extraReducerMatches).forEach(([type, reducer]) => {
                builder.addMatcher(type, reducer);
            });
        }
    })
}




