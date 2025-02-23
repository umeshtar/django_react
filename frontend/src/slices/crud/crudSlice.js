import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { authFetch } from '../../helpers/fetch'

export function baseAsyncThunk({ name, action, func }) {
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

export function fetchDataThunk({ name, url }) {
    let params = { action: 'get_data', get_form_configs: true, get_perms: true }
    return baseAsyncThunk({ name, action: 'fetchData', func: (data) => authFetch.get(url, { params: { ...params, ...data } }) })
}

export function fetchSingleRecordThunk({ name, url }) {
    let params = { action: 'fetch_record', is_form: true }
    return baseAsyncThunk({ name, action: 'fetchSingleRecord', func: (data) => authFetch.get(url, { params: { ...params, ...data } }) })
}

export function createRecordThunk({ name, url }) {
    return baseAsyncThunk({ name, action: 'createRecord', func: (data) => authFetch.post(url, data) })
}

export function updateRecordThunk({ name, url }) {
    return baseAsyncThunk({ name, action: 'updateRecord', func: (data) => authFetch.put(url, data) })
}

export function deleteRecordThunk({ name, url }) {
    return baseAsyncThunk({ name, action: 'deleteRecord', func: (data) => authFetch.delete(url, { params: { ...data } }) })
}

export function handleFormEdit({ name, url, data, reset, setValue, dispatch, successCallBack, errorCallBack }) {
    let api = fetchSingleRecordThunk({ name, url })
    dispatch(api({
        rec_id,
        successCallBack: (response) => {
            if (reset) reset()
            if(setValue){
                console.log({data});
            }
            if (successCallBack) successCallBack(response)
        },
        errorCallBack: (err) => {
            if (errorCallBack) errorCallBack(err)
        }
    }))
}

export function handleFormSubmit({ name, url, data, reset, setError, dispatch, successCallBack, errorCallBack }) {
    let api = data.rec_id ? updateRecordThunk({ name, url }) : createRecordThunk({ name, url })
    dispatch(api({
        ...data,
        successCallBack: (response) => {
            if (reset) reset()
            if (successCallBack) successCallBack(response)
        },
        errorCallBack: (err) => {
            if (err.name === "AxiosError" && setError) {
                const { form_errors: formErrors } = err.response.data
                if (formErrors) {
                    Object.entries(formErrors).forEach(([key, value]) => {
                        setError(key, { type: 'custom', message: value })
                    })
                }
            }
            if (errorCallBack) errorCallBack(err)
        }
    }))
}

export function createCrudSlice({ name, initialState = {}, reducers = {}, extraReducerCases = [], extraReducerMatches = [] }) {
    return createSlice({
        name,
        initialState: {
            title: '',
            data: [],
            record: undefined,
            formFields: undefined,
            permissions: {},
            mode: 'Create',
            ...initialState,
        },
        reducers: {
            resetForm: (state, action) => {
                state.mode = 'Create'
                state.record = undefined
            },
            ...reducers
        },
        extraReducers: (builder) => {
            builder
                .addCase(`${name}/fetchData/fulfilled`, (state, action) => {
                    state.title = action.payload.title
                    state.data = action.payload.data
                    state.formFields = action.payload.form_configs
                    state.permissions = action.payload.permissions
                })
                .addCase(`${name}/fetchSingleRecord/fulfilled`, (state, action) => {
                    state.mode = 'Update'
                    state.record = action.payload.data
                })
                .addCase(`${name}/createRecord/fulfilled`, (state, action) => {
                    state.data.push(action.payload.data)
                })
                .addCase(`${name}/updateRecord/fulfilled`, (state, action) => {
                    const newData = action.payload.data
                    state.data = state.data.map(obj => obj.rec_id === newData.rec_id ? newData : obj)
                    state.mode = 'Create'
                    state.record = undefined
                })
                .addCase(`${name}/deleteRecord/fulfilled`, (state, action) => {
                    state.data = state.data.filter(obj => !action.payload.ids.includes(obj.rec_id))
                })
            extraReducerCases.forEach((obj) => {
                builder.addCase(obj.case, obj.reducer)
            })
            extraReducerMatches.forEach((obj) => {
                builder.addMatcher(obj.match, obj.reducer)
            })
        }
    })
}




