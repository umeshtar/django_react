import { configureStore } from '@reduxjs/toolkit'
import departmentReducer from '../slices/main/employee/departmentSlice'
import employeeReducer from '../slices/main/employee/employeeSlice'
import loaderReducer from '../slices/global/loaderSlice'

export default configureStore({
    reducer: {
        'loader': loaderReducer,
        'department': departmentReducer,
        'employee': employeeReducer,
    },
})



