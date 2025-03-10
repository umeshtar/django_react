import { configureStore } from '@reduxjs/toolkit'
import departmentReducer from '../slices/main/employee/departmentSlice'
import employeeReducer from '../slices/main/employee/employeeSlice'
import moduleConfigurationReducer from '../slices/main/permission/moduleConfigurationSlice'
import loaderReducer from '../slices/global/loaderSlice'
import sidebarReducer from '../slices/global/sidebarSlice'

export default configureStore({
    reducer: {
        'loader': loaderReducer,
        'sidebar': sidebarReducer,
        'department': departmentReducer,
        'employee': employeeReducer,
        'module_configuration': moduleConfigurationReducer,
    },
})



