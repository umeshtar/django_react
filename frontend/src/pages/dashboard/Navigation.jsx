import { useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchSideBarData } from "../../slices/global/sidebarSlice";
import { useDispatch, useSelector } from "react-redux";

export function Navigation() {

    const data = useSelector((state) => state.sidebar.data)
    const all_modules = useSelector((state) => state.sidebar.all_modules)

    const dispatch = useDispatch()
    useEffect(() => {
        if (all_modules === null) {
            let api = fetchSideBarData()
            dispatch(api())
        }
    }, [])

    const NavigationElement = ({ label, link }) => {
        return (
            <li>
                <Link to={link}>{label}</Link>
            </li>
        )
    }

    const DropDownElement = ({ label, subItems }) => {
        return (
            <li>{label}
                <ul>
                    {subItems.map((subItem, index) => <NavigationElement key={index} {...subItem} />)}
                </ul>
            </li>
        )
    }

    return (
        <ul>
            {data.map((item, index) => {
                if (item.subItems) return <DropDownElement key={index} {...item} />
                else return <NavigationElement key={index} {...item} />
            })}
        </ul>
    )
}

