import {
    createCrudSlice,
    createCrudAsyncThunk
} from "../../crud/crudSlice"

const name = 'employee'
const url = 'employee/'

const slice = createCrudSlice({
    name
})
export const api = { ...createCrudAsyncThunk({ name, url }), ...slice.actions }
export default slice.reducer



