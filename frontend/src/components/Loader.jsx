import { useSelector } from 'react-redux'
import '../styles/style.css'

export default function Loader() {
    const activeRequests = useSelector((state) => state.loader.activeRequests)
    return <>
        {activeRequests.length > 0 && (
            <div className="loading-overlay">
                <div className="spinner"></div>
            </div>
        )}
    </>
}



