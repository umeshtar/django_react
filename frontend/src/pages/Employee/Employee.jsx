import { useDispatch, useSelector } from "react-redux";
import { CrudComponent } from "../../components/CrudComponent";
import { useEffect } from "react";
import { fetchEmployees } from "../../features/Employee/employeeSlice";

export function Employee() {
    const title = useSelector((state) => state.employee.title)
    const data = useSelector((state) => state.employee.data)
    const fields = useSelector((state) => state.employee.fields)
    const formConfigs = useSelector((state) => state.employee.formConfigs)
    const crudConfigs = { title, data, fields, formConfigs }

    const dispatch = useDispatch()
    useEffect(() => {
        dispatch(fetchEmployees())
    }, [dispatch])

    return (
        <CrudComponent {...crudConfigs} />
    )
}




