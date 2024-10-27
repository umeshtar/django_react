import { CrudComponent } from "../../../components/CrudComponent";
import {
    createEmployee,
    deleteEmployee,
    fetchEmployees,
    fetchSingleEmployee,
    updateEmployee
} from "../../../slices/main/employee/employeeSlice";

export const Employee = () => {
    return (
        <CrudComponent
            name='employee'
            fetchData={fetchEmployees}
            fetchSingleRecord={fetchSingleEmployee}
            createRecord={createEmployee}
            updateRecord={updateEmployee}
            deleteRecord={deleteEmployee}

        />
    )
}





