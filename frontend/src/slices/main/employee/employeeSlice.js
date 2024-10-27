import {
    createCrudSlice,
    createRecordAsyncThunk,
    deleteRecordAsyncThunk,
    FetchDataAsyncThunk,
    FetchSingleRecordAsyncThunk,
    updateRecordAsyncThunk
} from "../../crud/crudSlice"

const name = 'employee'
const url = '/employee/'

export const fetchEmployees = FetchDataAsyncThunk({ name, url })
export const fetchSingleEmployee = FetchSingleRecordAsyncThunk({ name, url })
export const createEmployee = createRecordAsyncThunk({ name, url })
export const updateEmployee = updateRecordAsyncThunk({ name, url })
export const deleteEmployee = deleteRecordAsyncThunk({ name, url })
export const employeeSlice = createCrudSlice({ name })
export default employeeSlice.reducer



