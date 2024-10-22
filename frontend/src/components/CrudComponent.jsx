import React from 'react';
import '../styles/crudTable.css'
import { useForm } from 'react-hook-form';
import { useDispatch } from 'react-redux';
import { submitEmployeeForm } from '../features/Employee/employeeSlice';

const FormComponent = ({ formConfigs }) => {
    const { fields, defaultValues } = formConfigs
    const { register, handleSubmit, formState: { errors }, } = useForm({ mode: 'all', defaultValues })

    const dispatch = useDispatch()
    const handleFormSubmit = (data) => {
        dispatch(submitEmployeeForm({ ...data }))
    }

    return (
        <form onSubmit={handleSubmit(handleFormSubmit)} noValidate>
            {Object.entries(fields).map(([name, configs], index) => {
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
            <button>Submit</button>
        </form >
    )
}

const TableComponent = ({ data, fields }) => {
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
                            <td><button>edit</button></td>
                            <td><button>delete</button></td>
                        </tr>
                    )
                })}
            </tbody>
        </table>
    )
}

export function CrudComponent({ title, fields, data, formConfigs }) {
    return (
        <>
            <h4>{title}</h4>
            {formConfigs && <FormComponent formConfigs={formConfigs} />}
            <hr />
            {fields && <TableComponent data={data} fields={fields} />}
        </>
    )
}

