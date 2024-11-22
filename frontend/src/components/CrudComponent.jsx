import React, { createContext, forwardRef, useCallback, useContext, useEffect, useImperativeHandle, useMemo, useRef } from 'react';
import '../styles/style.css'
import { useForm } from 'react-hook-form';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { handleLogout } from '../pages/login/Login';
import { setFormErrors, setFormValues } from '../helpers/reactHookForm';


const ApiContext = createContext(null)
const useApi = () => useContext(ApiContext)

const FormField = ({ name, register, configs, errors }) => {
    console.log('Render - FormField')
    const required = configs.rules.required ? 'required' : ''
    const errorMsg = errors[name]?.message

    let formField;
    if (configs.type === 'select') {
        formField = (
            <>
                <select {...register(name, configs.rules)} required={required} >
                    <option value="" disabled>{`Select ${configs.name}`}</option>
                    {configs.options.map((opt, i) => <option key={i} value={opt.value}>{opt.label}</option>)}
                </select>
            </>
        )

    } else {
        formField = (
            <input {...register(name, configs.rules)} placeholder={`Enter ${configs.name}`} required={required} />
        )
    }
    return (
        <React.Fragment>
            <p>{formField}</p>
            {errorMsg && <p style={{ color: 'red' }}> {errorMsg} </p>}
        </ React.Fragment>
    )
}

const FormComponent = forwardRef(({ formFields }, ref) => {
    console.log('Render - FormComponent');

    const { name, createRecord, updateRecord, resetForm } = useApi()
    const mode = useSelector((state) => state[name].mode)
    const { __add, __change } = useSelector((state) => state[name].permissions)
    const reactHookForm = useForm({ mode: 'all', defaultValues: formFields.defaultValues })
    const { register, handleSubmit, reset, formState: { errors } } = reactHookForm

    useImperativeHandle(ref, () => ({ reactHookForm }));

    const dispatch = useDispatch()
    const handleFormSubmit = (data) => {
        if (mode === 'Update' && data.rec_id && __change) {
            dispatch(updateRecord({
                ...data,
                successCallBack: (response) => { reset() },
                errorCallBack: (err) => setFormErrors({ reactHookForm, err })
            }))
        } else if (mode === 'Create' && __add) {
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
            {Object.entries(formFields.fields).map(([name, configs], index) => <FormField key={index} {...{ register, name, configs, errors }} />)}
            <button>{mode === 'Create' ? 'Submit' : 'Update'}</button>
            <button type='button' onClick={handleReset} style={{ marginLeft: 10 }}>Cancel</button>
        </form >
    )
})

const TableActions = ({ recId, reactHookFormRef }) => {
    console.log('Render - TableActions')

    const { name, fetchSingleRecord, deleteRecord } = useApi()
    const { __change, __delete } = useSelector((state) => state[name].permissions)

    const dispatch = useDispatch()
    const handleEdit = (rec_id) => {
        if (__change) {
            const { reactHookForm } = reactHookFormRef.current
            dispatch(fetchSingleRecord({
                rec_id,
                successCallBack: (response) => setFormValues({ reactHookForm, response })
            }))
        }
    }

    const handleDelete = (rec_id) => {
        if (__delete) {
            const isDelete = confirm('Are you Sure?')
            if (isDelete) dispatch(deleteRecord({ rec_id }))
        }
    }

    return <>
        {__change && <td><button onClick={() => handleEdit(recId)}>edit</button></td>}
        {__delete && <td><button onClick={() => handleDelete(recId)}>delete</button></td>}
    </>
}

const TableComponent = ({ tableFields, reactHookFormRef }) => {
    console.log('Render - TableComponent');
    const { name } = useApi()
    const data = useSelector((state) => state[name].data)
    const { __change, __delete } = useSelector((state) => state[name].permissions)

    const showActions = __change || __delete

    return (
        <table>
            <thead>
                <tr>
                    {Object.values(tableFields).map((label, headerIndex) => <th key={headerIndex}>{label}</th>)}
                    {showActions && <th colSpan={2}>Actions</th>}
                </tr>
            </thead>
            <tbody>
                {data.map((obj, rowIndex) => {
                    return (
                        <tr key={rowIndex}>
                            {Object.keys(tableFields).map((key, dataIndex) => <td key={dataIndex}>{obj[key]}</td>)}
                            {showActions && <TableActions {...{ recId: obj.rec_id, reactHookFormRef }} />}
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

const Navigation = () => {
    return <>
        <div>
            <Link to="/dashboard">Dashboard</Link>
        </div>
        <div>
            <button onClick={handleLogout}>Log out</button>
        </div>
    </>
}

export function CrudComponent({ name, api }) {
    console.log('Render - CrudComponent');

    const reactHookFormRef = useRef({})

    const title = useSelector((state) => state[name].title)
    const formFields = useSelector((state) => state[name].formFields)
    const tableFields = useSelector((state) => state[name].tableFields)
    const { __view, __add, __change } = useSelector((state) => state[name].permissions)

    const fetchSingleRecord = useCallback(api.fetchSingleRecord, [])
    const createRecord = useCallback(api.createRecord, [])
    const updateRecord = useCallback(api.updateRecord, [])
    const deleteRecord = useCallback(api.deleteRecord, [])
    const resetForm = useCallback(api.resetForm, [])
    const apiValue = useMemo(() => ({ name, fetchSingleRecord, createRecord, updateRecord, deleteRecord, resetForm }), [])

    const dispatch = useDispatch()
    useEffect(() => {
        dispatch(api.fetchData())
    }, [dispatch])

    const showForm = formFields && (__add || __change) ? true : false
    const showTable = tableFields && (__view) ? true : false
    return (
        <ApiContext.Provider value={apiValue}>
            <Navigation />
            {title && <TitleComponent {...{ title }} />}
            {showForm && <FormComponent ref={reactHookFormRef} {...{ formFields }} />}
            <hr />
            {showTable && <TableComponent {...{ tableFields, reactHookFormRef }} />}
        </ApiContext.Provider>
    )
}

