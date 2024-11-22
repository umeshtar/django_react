import { CrudComponent } from "../../../components/CrudComponent";
import { api } from "../../../slices/main/employee/departmentSlice";

export const Department = () => {
    return (
        <CrudComponent name='department' api={api} />
    )
}





