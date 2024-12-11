import { configureStore } from '@reduxjs/toolkit'
import departmentReducer from '../slices/main/employee/departmentSlice'
import loaderReducer from '../slices/loader/loaderSlice'

export default configureStore({
    reducer: {
        'loader': loaderReducer,
        'department': departmentReducer,
    },
})



