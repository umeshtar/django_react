import { useDispatch, useSelector } from "react-redux";
import { fetchSingleRecordThunk, handleFormSubmit } from "../../../slices/crud/crudSlice";
import { BaseComponent, FormField, TableComponent, TitleComponent } from "../../../components/CrudComponent";
import { DepartmentResetForm } from "../../../slices/main/employee/departmentSlice";
import { useFieldArray, useForm } from "react-hook-form";
import { Navigation } from "../../dashboard/Navigation";

export function Department() {
    const name = 'department'
    const url = 'employee/department/'
    return (
        <BaseComponent {...{ name, url }}>
            <DepartmentHelper {...{ name, url }} />
        </BaseComponent>
    )
}

function DepartmentHelper({ name, url }) {
    const tableFields = { name: 'Name', employees: 'Employees' }

    const dispatch = useDispatch()

    const title = useSelector((state) => state[name].title)
    const formFields = useSelector((state) => state[name].formFields)
    const permissions = useSelector((state) => state[name].permissions)
    const mode = useSelector((state) => state[name].mode)

    const { register, control, handleSubmit, reset, setValue, setError, formState: { errors } } = useForm({
        defaultValues: formFields.defaultValues
    })
    const employees = useFieldArray({ name: 'employees', control })

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
                const { employees: employeeData, ...formData } = response.data.data
                Object.entries(formData).forEach(([k, v]) => setValue(k, v))
                employees.replace(employeeData)
            },
        }))
    }
    function handleReset() {
        reset()
        dispatch(DepartmentResetForm())
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
                            <div style={{ display: 'flex', marginBottom: '20px' }}>
                                <div>
                                    {employees.fields.map((field, index) => {
                                        return (
                                            <div key={field.id} style={{ marginBottom: '20px' }}>
                                                <div>
                                                    <FormField {...{
                                                        register, name: `employees.${index}.name`, errors,
                                                        configs: formFields.repeaters.employees.fields.name,
                                                    }} />
                                                    <button type="button" onClick={() => employees.remove(index)}>Delete</button>
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                                <div>
                                    <button type="button" onClick={() => employees.append(formFields.repeaters.employees.defaultValues)}>Add</button>
                                </div>
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





