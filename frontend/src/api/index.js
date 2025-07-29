import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    console.log('Request:', config)
    return config
  },
  error => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('Response:', response)
    return response
  },
  error => {
    console.error('Response Error:', error)
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('Error Status:', error.response.status)
      console.error('Error Data:', error.response.data)
      
      // 如果是401错误，说明token过期或无效，需要重新登录
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('isLoggedIn')
        localStorage.removeItem('username')
        window.location.href = '/login'
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('No Response:', error.request)
    } else {
      // 请求配置出错
      console.error('Error Config:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api 