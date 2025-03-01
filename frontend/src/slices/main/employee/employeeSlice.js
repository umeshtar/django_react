import { createCrudSlice } from "../../crud/crudSlice"

const name = 'employee'

const slice = createCrudSlice({ name })
export const { resetForm } = slice.actions
export default slice.reducer



