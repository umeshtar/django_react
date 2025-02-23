import { useDispatch, useSelector } from "react-redux";
import { fetchDataThunk, handleFormSubmit } from "../../../slices/crud/crudSlice";
import { FormField, Navigation, TableComponent, TitleComponent } from "../../../components/CrudComponent";
import { useEffect } from "react";
import { resetForm } from "../../../slices/main/employee/departmentSlice";
import { useFieldArray, useForm } from "react-hook-form";

function DepartmentForm({ name, url, formFields, permissions }) {
    console.log('Render - FormComponent');

    const mode = useSelector((state) => state[name].mode)
    const record = useSelector((state) => state[name].record)
    const { __add = false, __change = false } = permissions || {}

    const { register, control, handleSubmit, reset, setError, formState: { errors } } = useForm({
        defaultValues: formFields.defaultValues
    })
    const employees = useFieldArray({ name: 'employees', control })

    const dispatch = useDispatch()
    function onSubmit(data) {
        if ((mode === 'Update' && data.rec_id && __change) || (mode === 'Create' && __add)) {
            handleFormSubmit({ name, url, data, reset, setError, dispatch })
        }
    }
    function handleReset() {
        reset()
        dispatch(resetForm())
    }
    return (
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
    )
}

export function Department() {
    const name = 'department'
    const url = 'employee/department/'
    const title = useSelector((state) => state[name].title)
    const formFields = useSelector((state) => state[name].formFields)
    const permissions = useSelector((state) => state[name].permissions)
    const tableFields = { name: 'Name', employees: 'Employees' }
    const { __view = false, __add = false, __change = false } = permissions || {}

    const dispatch = useDispatch()

    useEffect(() => {
        let api = fetchDataThunk({ name, url })
        dispatch(api())
    }, [])

    const showForm = formFields && (__add || __change) ? true : false
    const showTable = tableFields && (__view) ? true : false
    return (
        <>
            <Navigation />
            {title && <TitleComponent {...{ title }} />}
            {showForm && <DepartmentForm {...{ name, url, formFields, permissions }} />}
            <hr />
            {showTable && <TableComponent {...{ name, url, tableFields, permissions }} />}
        </>
    )
}





