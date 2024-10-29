import {
    createCrudSlice,
    createCrudAsyncThunk
} from "../../crud/crudSlice"

const name = 'employee'
const url = 'employee/'

export const api = createCrudAsyncThunk({ name, url })
const slice = createCrudSlice({ name })
export const { resetForm } = slice.actions
export default slice.reducer



