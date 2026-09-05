import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: (import.meta.env.VITE_API_URL?.trim() || 'http://localhost:8000').replace(/\/+$/, ''),
})

export { axiosInstance }
