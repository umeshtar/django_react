import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authFetch } from '../../helpers/fetch'

export const baseAsyncThunk = ({ name, action, func }) => {
    return createAsyncThunk(`${name}/${action}`, async ({ successCallBack, errorCallBack, ...data } = {}, { rejectWithValue }) => {
        try {
            const response = await func(data)
            if (response.data.message) alert(response.data.message)
            if (successCallBack) successCallBack(response)
            return response.data
        } catch (err) {
            if (err.name === 'AxiosError' && err.response.data.message) alert(err.response.data.message)
            if (errorCallBack) errorCallBack(err)
            return rejectWithValue(err.message)
        }
    })
}

export const createCrudAsyncThunk = ({ name, url }) => {
    return {
        fetchData: baseAsyncThunk({
            name, action: 'fetchData',
            func: (data) => authFetch.get(url, { params: { get_crud_configs: true, ...data } })
        }),
        fetchSingleRecord: baseAsyncThunk({
            name, action: 'fetchSingleRecord',
            func: (data) => authFetch.get(url, { params: { action: 'fetch_record', is_form: true, ...data } })
        }),
        createRecord: baseAsyncThunk({
            name, action: 'createRecord',
            func: (data) => authFetch.post(url, data)
        }),
        updateRecord: baseAsyncThunk({
            name, action: 'updateRecord',
            func: (data) => authFetch.put(url, data)
        }),
        deleteRecord: baseAsyncThunk({
            name, action: 'deleteRecord',
            func: (data) => authFetch.delete(url, { params: { ...data } })
        }),
    }
}

export const createCrudSlice = ({ name, initialState = {}, reducers = {}, extraReducerCases = {}, extraReducerMatches = {} }) => {
    return createSlice({
        name,
        initialState: {
            title: '',
            data: [],
            tableFields: undefined,
            formFields: undefined,
            mode: 'Create',
            ...initialState,
        },
        reducers: {
            resetForm: (state, action) => {
                state.mode = 'Create'
            },
            ...reducers
        },
        extraReducers: (builder) => {
            builder
                .addCase(`${name}/fetchData/fulfilled`, (state, action) => {
                    state.title = action.payload.title
                    state.data = action.payload.data
                    state.tableFields = action.payload.fields
                    state.formFields = action.payload.form_configs
                })
                .addCase(`${name}/fetchSingleRecord/fulfilled`, (state, action) => {
                    state.mode = 'Update'
                })
                .addCase(`${name}/createRecord/fulfilled`, (state, action) => {
                    state.data.push(action.payload.data)
                })
                .addCase(`${name}/updateRecord/fulfilled`, (state, action) => {
                    const newData = action.payload.data
                    state.data = state.data.map(obj => obj.rec_id === newData.rec_id ? newData : obj)
                    state.mode = 'Create'
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




