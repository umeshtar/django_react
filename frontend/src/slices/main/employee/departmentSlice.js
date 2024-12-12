import { createCrudSlice } from "../../crud/crudSlice"

const name = 'department'

const slice = createCrudSlice({ name })
export const { resetForm } = slice.actions
export default slice.reducer



