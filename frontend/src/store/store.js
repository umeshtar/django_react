import { configureStore } from '@reduxjs/toolkit'
import employeeReducer from '../slices/main/employee/employeeSlice'
import departmentReducer from '../slices/main/employee/departmentSlice'
import loaderReducer from '../slices/loader/loaderSlice'

export default configureStore({
    reducer: {
        'loader': loaderReducer,
        'employee': employeeReducer,
        'department': departmentReducer,
    },
})



