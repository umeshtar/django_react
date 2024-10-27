import React, { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';
import '../styles/style.css'
import { useForm } from 'react-hook-form';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { handleLogout } from '../pages/login/Login';

const FormComponent = forwardRef(({ formFields, createRecord, updateRecord }, ref) => {
    console.log('Render - FormComponent');
    const [action, setAction] = useState('Create')

    const { register, handleSubmit, setValue, setError, clearErrors, reset, formState: { errors }, } = useForm({ mode: 'all', defaultValues: formFields.defaultValues })

    useImperativeHandle(ref, () => ({ setValue, clearErrors, setAction }));

    const dispatch = useDispatch()
    const handleFormSubmit = (data) => {
        if (data.rec_id) {
            dispatch(updateRecord({ ...data, setError, reset, setAction }))
        } else {
            dispatch(createRecord({ ...data, setError, reset }))
        }
    }

    const handleReset = () => {
        reset()
        setAction('Create')
    }
    return (
        <form onSubmit={handleSubmit(handleFormSubmit)} noValidate>
            {Object.entries(formFields.fields).map(([name, configs], index) => {
                const required = configs.rules.required ? 'required' : ''
                const errorMsg = errors[name]?.message
                return (
                    <React.Fragment key={index}>
                        <p>
                            {configs.type === 'select' ? (
                                <select {...register(name, configs.rules)} required={required} >
                                    <option value="" disabled>{`Select ${configs.name}`}</option>
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
            <button>{action === 'Create' ? 'Submit' : 'Update'}</button>
            <button type='button' onClick={handleReset} style={{ marginLeft: 10 }}>Cancel</button>
        </form >
    )
})

const TableComponent = ({ name, tableFields, formMethodsRef, fetchSingleRecord, deleteRecord }) => {
    console.log('Render - TableComponent');
    const data = useSelector((state) => state[name].data)

    const dispatch = useDispatch()

    const handleEdit = (rec_id) => {
        const { setValue, clearErrors, setAction } = formMethodsRef.current
        dispatch(fetchSingleRecord({ rec_id, setValue, clearErrors, setAction }))
    }

    const handleDelete = (rec_id) => {
        const isDelete = confirm('Are you Sure?')
        if (isDelete) dispatch(deleteRecord({ rec_id }))
    }

    return (
        <table>
            <thead>
                <tr>
                    {Object.values(tableFields).map((label, headerIndex) => {
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
                            {Object.keys(tableFields).map((key, dataIndex) => {
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

const TitleComponent = ({ title }) => {
    console.log('Render - TitleComponent');
    return (
        <h4>{title}</h4>
    )
}

export function CrudComponent({ name, fetchData, fetchSingleRecord, createRecord, updateRecord, deleteRecord }) {
    console.log('Render - CrudComponent');

    const formMethodsRef = useRef({})

    const title = useSelector((state) => state[name].title)
    const formFields = useSelector((state) => state[name].formFields)
    const tableFields = useSelector((state) => state[name].tableFields)

    const dispatch = useDispatch()
    useEffect(() => {
        dispatch(fetchData())
    }, [dispatch])

    return (
        <>
            <div>
                <Link to="/dashboard">Dashboard</Link>
            </div>
            <div>
                <button onClick={handleLogout}>Log out</button>
            </div>
            {title && <TitleComponent {...{ title }} />}
            {formFields && <FormComponent ref={formMethodsRef} {...{ formFields, createRecord, updateRecord }} />}
            <hr />
            {tableFields && <TableComponent {...{ name, tableFields, formMethodsRef, fetchSingleRecord, deleteRecord }} />}
        </>
    )
}

