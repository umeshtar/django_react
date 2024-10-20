import { useDispatch, useSelector } from "react-redux";
import { CrudComponent } from "../../components/CrudComponent";
import { useEffect } from "react";
import { fetchEmployees } from "../../features/Employee/employeeSlice";

export function Employee() {
    const empData = useSelector((state) => state.employee.data)
    const empFields = useSelector((state) => state.employee.fields)

    const dispatch = useDispatch()
    useEffect(() => {
        dispatch(fetchEmployees())
    }, [dispatch])

    return (
        <>
            <CrudComponent title='Employee' columns={empFields} rows={empData}></CrudComponent>
        </>
    )
}

