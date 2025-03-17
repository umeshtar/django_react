import React, { useEffect, useState } from 'react';
import '../styles/style.css'
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { handleLogout } from '../pages/login/Login';
import { ErrorMessage } from '@hookform/error-message';
import { deleteRecordThunk, fetchDataThunk } from '../slices/crud/crudSlice';
import { fetchSideBarData } from '../slices/global/sidebarSlice';


export function FormField({ name, register, configs = {}, errors = {} }) {
    console.log('Render - FormField')

    let formField;
    if (configs.type === 'select') {
        formField = (
            <div>
                <label>{configs.name}</label>
                <select {...register(name)} multiple={configs.multiple || false}>
                    <option value="" disabled>{`Select ${configs.name}`}</option>
                    {configs.options.map((opt, i) => <option key={i} value={opt.value}>{opt.label}</option>)}
                </select>
            </div>
        )

    } else if (configs.type === 'checkbox') {
        formField = (
            <div>
                <label>{configs.name}</label>
                <input type='checkbox' {...register(name)} />
            </div>
        )

    } else if (configs.type === 'textarea') {
        formField = (
            <div>
                <label>{configs.name}</label>
                <textarea {...register(name)} />
            </div>
        )

    } else {
        formField = (
            <div>
                <label>{configs.name}</label>
                <input type={configs.type} {...register(name)} placeholder={`Enter ${configs.name}`} />
            </div>
        )
    }
    return (
        <React.Fragment>
            {formField}
            <ErrorMessage errors={errors} name={name} render={({ message }) => <span style={{ color: 'red' }}>{message}</span>} />
        </ React.Fragment>
    )
}

export function TableComponent({ name, url, tableFields, permissions, handleEdit, dynamic = false }) {
    console.log('Render - TableComponent');

    const dispatch = useDispatch()
    const data = useSelector((state) => state[name].data)

    const { __change, __delete } = permissions
    const showActions = __change || __delete

    function handleDelete(rec_id) {
        let api = deleteRecordThunk({ name, url })
        if (dynamic === true) {
            if (confirm('Are you sure?')) {
                dispatch(api({
                    ids: [rec_id],
                    delete_confirmation: true,
                }))
            }
        } else {
            dispatch(api({
                ids: [rec_id],
                delete_confirmation: false,
                successCallBack: (data) => {
                    const msg_type = data?.data?.delete_context?.msg_type
                    if (msg_type === 'protect') {
                        alert(data.data.delete_context.protect_msg)
                    } else if (msg_type === 'cascade') {
                        if (confirm('Are you sure?')) {
                            dispatch(api({
                                ids: [rec_id],
                                delete_confirmation: true,
                            }))
                        }
                    }
                }
            }))
        }

    }

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
                            {Object.keys(tableFields).map((key, dataIndex) => <td key={dataIndex}>{obj[key]?.toString()}</td>)}
                            {showActions && (
                                <>
                                    {__change && <td><button onClick={() => handleEdit(obj.rec_id)}>edit</button></td>}
                                    {__delete && <td><button onClick={() => handleDelete(obj.rec_id)}>delete</button></td>}
                                </>
                            )}
                        </tr>
                    )
                })}
            </tbody>
        </table>
    )
}

export function TitleComponent() {
    console.log('Render - TitleComponent');
    const all_modules = useSelector((state) => state.sidebar.all_modules) || []
    const link = window.location.origin + window.location.pathname
    const matches = all_modules.filter(obj => obj.link === link)
    let result = []
    if (matches.length > 0) {
        matches[0]?.path?.forEach((codename) => {
            let module = all_modules.find(obj => obj.codename === codename)
            if (module && module.name) {
                result.push(module.name)
            }
        })
    }
    const title = result.join(' -- ')

    return (
        <header className="header">
            <h1>{title || 'No Title Found'}</h1>
            <button className="logout-button" onClick={handleLogout}>Logout</button>
        </header>
    )
}

export function BaseComponent({ name, url, children }) {
    console.log("Render - BaseComponent");

    const [init, setInit] = useState(false)
    const all_modules = useSelector((state) => state.sidebar.all_modules)

    const dispatch = useDispatch()
    useEffect(() => {
        if (all_modules === null) {
            let api = fetchSideBarData()
            dispatch(api())
        } else {
            let fetchApi = fetchDataThunk({ name, url })
            dispatch(fetchApi({
                successCallBack: () => {
                    setInit(true)
                }
            }))
        }

    }, [all_modules, name, url])

    return (
        init === true ? children : "Loading..."
    )
}



