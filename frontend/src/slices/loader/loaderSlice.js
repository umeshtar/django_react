import { createSlice } from '@reduxjs/toolkit'

const isPending = (action) => action.type.endsWith('/pending')
const isFulfilledOrRejected = (action) => action.type.endsWith('/fulfilled') || action.type.endsWith('/rejected')

const loaderSlice = createSlice({
    name: 'loader',
    initialState: {
        activeRequests: []
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addMatcher(isPending, (state, action) => {
                console.log({ loaderStart: action });
                state.activeRequests.push(action.type)
            })
            .addMatcher(isFulfilledOrRejected, (state, action) => {
                console.log({ loaderEnd: action });
                state.activeRequests.pop(action.type)
            })
    }
})

export default loaderSlice.reducer



