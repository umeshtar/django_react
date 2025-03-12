import { useDispatch, useSelector } from "react-redux"
import { BaseComponent, FormField, TableComponent, TitleComponent } from "../../components/CrudComponent"
import { fetchSingleRecordThunk, handleFormSubmit } from "../../slices/crud/crudSlice"
import { DynamicResetForm } from "../../slices/dynamic/dynamicSlice"
import { useForm } from "react-hook-form"
import { Navigation } from "../dashboard/Navigation"

export function DynamicModule() {
    const all_modules = useSelector((state) => state.sidebar.all_modules) || []
    const link = window.location.origin + window.location.pathname
    const formId = all_modules.find(obj => obj.link === link)?.dynamic_form
    const name = 'dynamic'
    const url = `permission/dynamic_modules/${formId}/`
    return (
        <BaseComponent {...{ name, url }}>
            <DynamicModuleHelper {...{ name, url }} />
        </BaseComponent>
    )
}

function DynamicModuleHelper({ name, url }) {
    // const tableFields = { name: 'Name', employees: 'Employees' }

    const dispatch = useDispatch()

    const title = useSelector((state) => state[name].title)
    const tableFields = useSelector((state) => state[name].tableFields)
    const formFields = useSelector((state) => state[name].formFields)
    const permissions = useSelector((state) => state[name].permissions)
    const mode = useSelector((state) => state[name].mode)

    const { register, handleSubmit, reset, setValue, setError, formState: { errors } } = useForm({
        defaultValues: formFields.defaultValues
    })
    const { __view = false, __add = false, __change = false } = permissions || {}
    const showForm = formFields && (__add || __change) ? true : false
    const showTable = tableFields && (__view) ? true : false

    function onSubmit(data) {
        console.log({ data });
        if ((mode === 'Update' && data.rec_id && __change) || (mode === 'Create' && __add)) {
            console.log('Update');
            handleFormSubmit({ name, url, data, reset, setError, dispatch })
        }
    }
    function handleEdit(rec_id) {
        let api = fetchSingleRecordThunk({ name, url })
        dispatch(api({
            rec_id,
            successCallBack: (response) => {
                reset()
                Object.entries(response.data.data).forEach(([k, v]) => setValue(k, v))
            },
        }))
    }
    function handleReset() {
        reset()
        dispatch(DynamicResetForm())
    }
    return (
        <>
            {title && <TitleComponent {...{ title }} />}
            <div className="container">
                <div className="sidebar">
                    <Navigation />
                </div>
                <div className="main-content">
                    {showForm && (
                        <form style={{ gap: 3 }} onSubmit={handleSubmit(onSubmit)} noValidate>
                            {Object.entries(formFields.fields).map(([name, configs], index) => (
                                <div style={{ marginBottom: '20px' }} key={index}>
                                    <FormField {...{ register, name, configs, errors }} />
                                </div>
                            ))}
                            <button>{mode === 'Create' ? 'Submit' : 'Update'}</button>
                            <button type='button' onClick={handleReset} style={{ marginLeft: 10 }}>Cancel</button>
                        </form >
                    )}
                    <hr />
                    {showTable && <TableComponent {...{ name, url, tableFields, permissions, handleEdit, dynamic: true }} />}
                </div>
            </div>
        </>
    )
}





