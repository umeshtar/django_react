import Cookies from "js-cookie"
import { authFetch } from "../api_helper"

const handleSubmit = async (e) => {
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
        window.location.href = '/'
    } catch (err) {
        alert('Login Failed')
    }
}

export function Login() {
    return (
        <form method="post" onSubmit={handleSubmit}>
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


