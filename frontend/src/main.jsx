import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { router } from './routes/router.jsx'
import { Provider } from 'react-redux'
import store from './store/store.js'
import Loader from './components/Loader.jsx'

createRoot(document.getElementById('root')).render(
  <Provider store={store}>
    <RouterProvider router={router} />
    <Loader />
  </Provider>
)
