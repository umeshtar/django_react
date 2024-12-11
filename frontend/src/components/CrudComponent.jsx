import React from 'react';
import '../styles/style.css'
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { handleLogout } from '../pages/login/Login';
import { ErrorMessage } from '@hookform/error-message';
import { deleteRecordThunk, fetchSingleRecordThunk } from '../slices/crud/crudSlice';


export function FormField({ name, register, configs = {}, errors = {} }) {
    console.log('Render - FormField')
    const required = configs.rules.required ? true : false

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
            <ErrorMessage errors={errors} name={name} />
        </ React.Fragment>
    )
}

export function TableActions({ name, url, rec_id }) {
    console.log('Render - TableActions')

    const { __change, __delete } = useSelector((state) => state[name].permissions)
    const dispatch = useDispatch()

    function handleEdit(rec_id) {
        let api = fetchSingleRecordThunk({ name, url })
        dispatch(api({
            rec_id
        }))
    }

    function handleDelete(rec_id) {
        const isDelete = confirm('Are you Sure?')
        if (isDelete) {
            let api = deleteRecordThunk({ name, url })
            dispatch(api({ rec_id }))
        }
    }

    return <>
        {__change && <td><button onClick={() => handleEdit(rec_id)}>edit</button></td>}
        {__delete && <td><button onClick={() => handleDelete(rec_id)}>delete</button></td>}
    </>
}

export function TableComponent({ name, url, tableFields, permissions }) {
    console.log('Render - TableComponent');
    const data = useSelector((state) => state[name].data)
    const { __change, __delete } = permissions

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
                            {showActions && <TableActions {...{ name, url, rec_id: obj.rec_id }} />}
                        </tr>
                    )
                })}
            </tbody>
        </table>
    )
}

export function TitleComponent({ title }) {
    console.log('Render - TitleComponent');
    return (
        <h4>{title}</h4>
    )
}

export function Navigation() {
    return <>
        <div>
            <Link to="/dashboard">Dashboard</Link>
        </div>
        <div>
            <button onClick={handleLogout}>Log out</button>
        </div>
    </>
}


