import { createSlice } from '@reduxjs/toolkit'

const isPending = (action) => action.type.endsWith('/pending')
const isFulfilled = (action) => action.type.endsWith('/fulfilled')
const isRejected = (action) => action.type.endsWith('/rejected')

const loaderSlice = createSlice({
    name: 'loader',
    initialState: {
        activeRequests: []
    },
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addMatcher(isPending, (state, action) => {
                console.log({ leaderPending: action });
                const actionType = action.type.split('/pending')[0]
                state.activeRequests.push(actionType)
            })
            .addMatcher(isFulfilled, (state, action) => {
                console.log({ loaderFulfilled: action });
                const actionType = action.type.split('/fulfilled')[0]
                state.activeRequests = state.activeRequests.filter(req => !req === actionType)
            })
            .addMatcher(isRejected, (state, action) => {
                console.log({ loaderRejected: action });
                const actionType = action.type.split('/rejected')[0]
                state.activeRequests = state.activeRequests.filter(req => !req === actionType)
            })
    }
})

export default loaderSlice.reducer



