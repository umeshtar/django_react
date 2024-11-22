import {
    createCrudSlice,
    createCrudAsyncThunk
} from "../../crud/crudSlice"

const name = 'department'
const url = 'employee/department/'

const slice = createCrudSlice({ name })
export const api = { ...createCrudAsyncThunk({ name, url }), ...slice.actions }
export default slice.reducer



