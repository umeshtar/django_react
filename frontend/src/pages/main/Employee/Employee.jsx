import { useDispatch, useSelector } from "react-redux";
import { fetchSingleRecordThunk, handleFormSubmit } from "../../../slices/crud/crudSlice";
import { BaseComponent, FormField, TableComponent, TitleComponent } from "../../../components/CrudComponent";
import { useForm } from "react-hook-form";
import { EmployeeResetForm } from "../../../slices/main/employee/employeeSlice";
import { Navigation } from "../../dashboard/Navigation";

export function Employee() {
    const name = 'employee'
    const url = 'employee/'
    return (
        <BaseComponent {...{ name, url }}>
            <EmployeeHelper {...{ name, url }} />
        </BaseComponent>
    )
}

function EmployeeHelper({ name, url }) {
    const tableFields = { name: 'Name', department: 'Department' }

    const dispatch = useDispatch()

    const title = useSelector((state) => state[name].title)
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
        if ((mode === 'Update' && data.rec_id && __change) || (mode === 'Create' && __add)) {
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
        dispatch(EmployeeResetForm())
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
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'name', configs: formFields.fields.name, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'department', configs: formFields.fields.department, errors }} />
                            </div>
                            <button>{mode === 'Create' ? 'Submit' : 'Update'}</button>
                            <button type='button' onClick={handleReset} style={{ marginLeft: 10 }}>Cancel</button>
                        </form >
                    )}
                    <hr />
                    {showTable && <TableComponent {...{ name, url, tableFields, permissions, handleEdit }} />}
                </div>
            </div>
        </>
    )
}





