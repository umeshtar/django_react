import React, { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';
import '../styles/style.css'
import { useForm } from 'react-hook-form';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { handleLogout } from '../pages/login/Login';
import { setFormErrors, setFormValues } from '../helpers/reactHookForm';

const FormComponent = forwardRef(({ name, formFields, createRecord, updateRecord, resetForm }, ref) => {
    console.log('Render - FormComponent');

    const mode = useSelector((state) => state[name].mode)
    const reactHookForm = useForm({ mode: 'all', defaultValues: formFields.defaultValues })
    const { register, handleSubmit, reset, formState: { errors } } = reactHookForm

    useImperativeHandle(ref, () => ({ reactHookForm }));

    const dispatch = useDispatch()
    const handleFormSubmit = (data) => {
        if (mode === 'Update' && data.rec_id) {
            dispatch(updateRecord({
                ...data,
                successCallBack: (response) => { reset() },
                errorCallBack: (err) => setFormErrors({ reactHookForm, err })
            }))
        } else if (mode === 'Create') {
            dispatch(createRecord({
                ...data,
                successCallBack: (response) => { reset() },
                errorCallBack: (err) => setFormErrors({ reactHookForm, err })
            }))
        }
    }

    const handleReset = () => {
        reset()
        dispatch(resetForm())
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
            <button>{mode === 'Create' ? 'Submit' : 'Update'}</button>
            <button type='button' onClick={handleReset} style={{ marginLeft: 10 }}>Cancel</button>
        </form >
    )
})

const TableComponent = ({ name, tableFields, reactHookFormRef, fetchSingleRecord, deleteRecord }) => {
    console.log('Render - TableComponent');
    const data = useSelector((state) => state[name].data)

    const dispatch = useDispatch()

    const handleEdit = (rec_id) => {
        const { reactHookForm } = reactHookFormRef.current
        dispatch(fetchSingleRecord({
            rec_id,
            successCallBack: (response) => setFormValues({ reactHookForm, response })
        }))
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

export function CrudComponent({ name, fetchData, fetchSingleRecord, createRecord, updateRecord, deleteRecord, resetForm }) {
    console.log('Render - CrudComponent');

    const reactHookFormRef = useRef({})

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
            {formFields && <FormComponent ref={reactHookFormRef} {...{ name, formFields, createRecord, updateRecord, resetForm }} />}
            <hr />
            {tableFields && <TableComponent {...{ name, tableFields, reactHookFormRef, fetchSingleRecord, deleteRecord }} />}
        </>
    )
}

