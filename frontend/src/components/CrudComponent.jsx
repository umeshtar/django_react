import '../styles/crudTable.css'

const FormComponent = () => {
    return (
        <form style={{ marginBottom: 40 }}>
            <label>Name:</label>
            <input type="text" name="name" />
            <label>Designation:</label>
            <select name="designation">
                <option value="IT">IT</option>
                <option value="Sales">Sales</option>
                <option value="HR">HR</option>
            </select>
            <button style={{ marginTop: 20 }}>Submit</button>
        </form>
    )
}

const TableComponent = ({ rows, columns }) => {
    return (
        <table>
            <thead>
                <tr>
                    {Object.values(columns).map((label, headerIndex) => {
                        return (
                            <th key={headerIndex}>{label}</th>
                        )
                    })}
                    <th colSpan={2}>Actions</th>
                </tr>
            </thead>
            <tbody>
                {rows.map((obj, rowIndex) => {
                    return (
                        <tr key={rowIndex}>
                            {Object.keys(columns).map((key, dataIndex) => {
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

export function CrudComponent({ title, columns, rows }) {
    return (
        <>
            <h4>{title}</h4>
            <FormComponent />
            <TableComponent rows={rows} columns={columns} />
        </>
    )
}

