import { CrudComponent } from "../../../components/CrudComponent";
import { api } from "../../../slices/main/employee/employeeSlice";

export const Employee = () => {
    return <>
        <CrudComponent name='employee' api={api} />
    </>
}





