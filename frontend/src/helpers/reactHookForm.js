export const setFormErrors = ({ reactHookForm, err }) => {
    const { setError } = reactHookForm
    const { form_errors: formErrors } = err.response.data

    if (err.name === "AxiosError" && formErrors) {
        Object.entries(formErrors).forEach(([key, value]) => {
            setError(key, { type: 'custom', message: value })
        })
    }
}


export const setFormValues = ({ reactHookForm, response }) => {
    const { clearErrors, setValue } = reactHookForm

    clearErrors()
    Object.entries(response.data.data).forEach(([key, value]) => {
        setValue(key, value)
    })
}


