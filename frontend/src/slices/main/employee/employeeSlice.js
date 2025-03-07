import { createCrudSlice } from "../../crud/crudSlice"

const name = 'employee'

const slice = createCrudSlice({ name })
export const { resetForm: EmployeeResetForm } = slice.actions
export default slice.reducer



