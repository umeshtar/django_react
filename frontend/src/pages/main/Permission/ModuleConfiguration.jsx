import { useDispatch, useSelector } from "react-redux"
import { fetchSingleRecordThunk, handleFormSubmit } from "../../../slices/crud/crudSlice"
import { BaseComponent, FormField, TableComponent, TitleComponent } from "../../../components/CrudComponent"
import { useForm } from "react-hook-form"
import { Navigation } from "../../dashboard/Navigation"
import { ModuleConfigurationResetForm } from "../../../slices/main/permission/moduleConfigurationSlice"

export function ModuleConfiguration() {
    const name = 'module_configuration'
    const url = 'permission/module_configuration/'
    return (
        <BaseComponent {...{ name, url }}>
            <ModuleConfigurationHelper {...{ name, url }} />
        </BaseComponent>
    )
}

function ModuleConfigurationHelper({ name, url }) {
    const tableFields = {
        name: 'Name',
        codename: 'Codename',
        codename: 'Codename',
        menu_type: 'Menu Type',
        is_root_menu: 'Root Menu',
        is_global_menu: 'Global Menu',
        page_url: 'Link',
        sequence: 'Sequence',
        react_box_icon: 'Icon',
        permissions: 'Permissions',
        children: 'Children',
    }

    const dispatch = useDispatch()

    const title = useSelector((state) => state[name].title)
    const formFields = useSelector((state) => state[name].formFields)
    const permissions = useSelector((state) => state[name].permissions)
    const mode = useSelector((state) => state[name].mode)

    const { register, handleSubmit, reset, setValue, setError, formState: { errors } } = useForm({
        defaultValues: formFields.defaultValues
    })

    const { __view = false, __add = false, __change = false } = permissions || {}
    const showForm = formFields && (__add || __change) ? true : false
    const showTable = tableFields && (__view) ? true : false

    function onSubmit(data) {
        if ((mode === 'Update' && data.rec_id && __change) || (mode === 'Create' && __add)) {
            handleFormSubmit({ name, url, data, reset, setError, dispatch })
        }
    }
    function handleEdit(rec_id) {
        let api = fetchSingleRecordThunk({ name, url })
        dispatch(api({
            rec_id,
            successCallBack: (response) => {
                reset()
                Object.entries(response.data.data).forEach(([k, v]) => setValue(k, v))
            },
        }))
    }
    function handleReset() {
        reset()
        dispatch(ModuleConfigurationResetForm())
    }
    return (
        <>
            {title && <TitleComponent {...{ title }} />}
            <div className="container">
                <div className="sidebar">
                    <Navigation />
                </div>
                <div className="main-content">
                    {showForm && (
                        <form style={{ gap: 3 }} onSubmit={handleSubmit(onSubmit)} noValidate>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'name', configs: formFields.fields.name, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codename', configs: formFields.fields.codename, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codenamemenu_type', configs: formFields.fields.menu_type, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codenameis_root_menu', configs: formFields.fields.is_root_menu, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codenameis_global_menu', configs: formFields.fields.is_global_menu, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codenamepage_url', configs: formFields.fields.page_url, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codenamesequence', configs: formFields.fields.sequence, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codenamereact_box_icon', configs: formFields.fields.react_box_icon, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'codenamepermissions', configs: formFields.fields.permissions, errors }} />
                            </div>
                            <div style={{ marginBottom: '20px' }}>
                                <FormField {...{ register, name: 'children', configs: formFields.fields.children, errors }} />
                            </div>
                            <button>{mode === 'Create' ? 'Submit' : 'Update'}</button>
                            <button type='button' onClick={handleReset} style={{ marginLeft: 10 }}>Cancel</button>
                        </form >
                    )}
                    <hr />
                    {showTable && <TableComponent {...{ name, url, tableFields, permissions, handleEdit }} />}
                </div>
            </div>
        </>
    )
}





