import { configureStore } from '@reduxjs/toolkit'
import employeeReducer from '../slices/main/employee/employeeSlice'
import loaderReducer from '../slices/loader/loaderSlice'

export default configureStore({
    reducer: {
        'loader': loaderReducer,
        'employee': employeeReducer,
    },
})



