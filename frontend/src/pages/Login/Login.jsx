import Cookies from "js-cookie"
import { authFetch } from "../../helpers/fetch"
import { useNavigate } from "react-router-dom"

export const handleLogout = () => {
    Cookies.remove('authUser')
    window.location.href = ''
}

export function Login() {
    const navigate = useNavigate()

    const handleLogin = async (e) => {
        e.preventDefault()
        try {
            const response = await authFetch.post('/token/', {
                username: document.querySelector('input[name=username]').value,
                password: document.querySelector('input[name=password]').value,
            })
            Cookies.set('authUser', JSON.stringify({
                access: response.data.access,
                refresh: response.data.refresh
            }))
            window.location.href = '/dashboard'
        } catch (err) {
            alert('Login Failed')
        }
    }

    return (
        <form method="post" onSubmit={handleLogin}>
            <div>
                <label>User Name</label>
                <input type="text" name="username" />
            </div>
            <div>
                <label>Password</label>
                <input type="text" name="password" />
            </div>
            <button>Submit</button>
        </form>
    )
}
