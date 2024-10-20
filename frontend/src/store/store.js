import { configureStore } from '@reduxjs/toolkit'
import employeeReducer from '../features/Employee/employeeSlice'

export default configureStore({
    reducer: {
        'employee': employeeReducer,
    },
})



