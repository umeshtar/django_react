import { createCrudSlice } from "../../crud/crudSlice"

const name = 'module_configuration'

const slice = createCrudSlice({ name })
export const { resetForm: ModuleConfigurationResetForm } = slice.actions
export default slice.reducer



