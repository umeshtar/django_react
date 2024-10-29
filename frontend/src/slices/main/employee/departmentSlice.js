import {
    createCrudSlice,
    createCrudAsyncThunk
} from "../../crud/crudSlice"

const name = 'department'
const url = 'employee/department/'

export const api = createCrudAsyncThunk({ name, url })
const slice = createCrudSlice({ name })
export default slice.reducer



