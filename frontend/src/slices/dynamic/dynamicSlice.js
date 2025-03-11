import { createCrudSlice } from "../crud/crudSlice"

const name = 'dynamic'

const slice = createCrudSlice({ name })
export const { resetForm: DynamicResetForm } = slice.actions
export default slice.reducer
