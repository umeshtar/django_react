import React, { useEffect } from 'react';
import '../styles/crudTable.css'
import { useForm } from 'react-hook-form';
import { useDispatch, useSelector } from 'react-redux';
import { fetchEmployees, fetchSingleEmployee, formResetDone, createEmployee, updateEmployee, deleteEmployee } from '../features/Employee/employeeSlice';

const FormComponent = () => {
    const formConfigs = useSelector((state) => state.employee.formConfigs)

    const { register, handleSubmit, setValue, setError, reset, formState: { errors }, } = useForm({ mode: 'all', defaultValues: formConfigs.defaultValues })

    const formErrors = useSelector((state) => state.employee.formErrors)
    const resetForm = useSelector((state) => state.employee.resetForm)
    const fetchedRecord = useSelector((state) => state.employee.fetchedRecord)

    const dispatch = useDispatch()

    useEffect(() => {
        if (formErrors) {
            for (let [name, error] of Object.entries(formErrors)) {
                setError(name, { type: 'custom', message: error })
            }
        }
    }, [formErrors, setError])

    useEffect(() => {
        if (resetForm === true) {
            reset()
            dispatch(formResetDone())
        }
    }, [resetForm, reset, dispatch])

    useEffect(() => {
        if (fetchedRecord) {
            for (let [key, value] of Object.entries(fetchedRecord)) {
                setValue(key, value)
            }
        }
    }, [fetchedRecord, setValue, dispatch])

    const handleFormSubmit = (data) => {
        if (fetchedRecord) {
            dispatch(updateEmployee(data))
        } else {
            dispatch(createEmployee(data))
        }
    }

    const handleReset = () => {
        reset()
        dispatch(formResetDone())
    }

    return (
        <form onSubmit={handleSubmit(handleFormSubmit)} noValidate>
            {Object.entries(formConfigs.fields).map(([name, configs], index) => {
                const required = configs.rules.required ? 'required' : ''
                const errorMsg = errors[name]?.message
                return (
                    <React.Fragment key={index}>
                        <p>
                            {configs.type === 'select' ? (
                                <select {...register(name, configs.rules)} placeholder={`Select ${configs.name}`} required={required} >
                                    {configs.options.map((opt, i) => <option key={i} value={opt.value}>{opt.label}</option>)}
                                </select>
                            ) : (
                                <input {...register(name, configs.rules)} placeholder={`Enter ${configs.name}`} required={required} />
                            )}
                        </p>
                        {errorMsg && <p style={{ color: 'red' }}> {errorMsg} </p>}
                    </ React.Fragment>
                )
            })}
            <button> {fetchedRecord ? 'Update' : 'Submit'}</button>
            <button type='button' onClick={handleReset} style={{ marginLeft: 10 }}>Cancel</button>
        </form >
    )
}

const TableComponent = () => {
    const data = useSelector((state) => state.employee.data)
    const fields = useSelector((state) => state.employee.fields)

    const dispatch = useDispatch()

    const handleEdit = (rec_id) => {
        dispatch(fetchSingleEmployee({ rec_id }))
    }

    const handleDelete = (rec_id) => {
        const isDelete = confirm('Are you Sure?')
        if (isDelete) dispatch(deleteEmployee({ rec_id }))
    }

    return (
        <table>
            <thead>
                <tr>
                    {Object.values(fields).map((label, headerIndex) => {
                        return (
                            <th key={headerIndex}>{label}</th>
                        )
                    })}
                    <th colSpan={2}>Actions</th>
                </tr>
            </thead>
            <tbody>
                {data.map((obj, rowIndex) => {
                    return (
                        <tr key={rowIndex}>
                            {Object.keys(fields).map((key, dataIndex) => {
                                return (
                                    <td key={dataIndex}>{obj[key]}</td>
                                )
                            })}
                            <td><button onClick={() => handleEdit(obj.rec_id)}>edit</button></td>
                            <td><button onClick={() => handleDelete(obj.rec_id)}>delete</button></td>
                        </tr>
                    )
                })}
            </tbody>
        </table>
    )
}

const TitleComponent = () => {
    const title = useSelector((state) => state.employee.title)
    return (
        <h4>{title}</h4>
    )
}

export function CrudComponent() {
    const title = useSelector((state) => state.employee.title)
    const formConfigs = useSelector((state) => state.employee.formConfigs)
    const fields = useSelector((state) => state.employee.fields)

    const dispatch = useDispatch()
    useEffect(() => {
        dispatch(fetchEmployees())
    }, [dispatch])

    return (
        <>
            {title && <TitleComponent />}
            {formConfigs && <FormComponent />}
            <hr />
            {fields && <TableComponent />}
        </>
    )
}

