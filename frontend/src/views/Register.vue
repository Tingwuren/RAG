<template>
  <div class="register-page">
    <div class="register-container">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" id="username" v-model="username" required>
          <p class="error-message" v-if="errors.username">{{ errors.username }}</p>
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" v-model="password" required>
          <p class="error-message" v-if="errors.password">{{ errors.password }}</p>
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input type="password" id="confirmPassword" v-model="confirmPassword" required>
          <p class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</p>
        </div>
        <div class="form-group">
          <label for="role">角色</label>
          <select id="role" v-model="role">
            <option value="user">普通用户</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? '注册中...' : '注册' }}
        </button>
        <p class="login-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('user')
const isSubmitting = ref(false)
const errors = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateForm = () => {
  let isValid = true
  errors.username = ''
  errors.password = ''
  errors.confirmPassword = ''

  if (!username.value) {
    errors.username = '请输入用户名'
    isValid = false
  }

  if (!password.value) {
    errors.password = '请输入密码'
    isValid = false
  } else if (password.value.length < 6) {
    errors.password = '密码长度不能少于6位'
    isValid = false
  }

  if (password.value !== confirmPassword.value) {
    errors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    const response = await api.post('/api/register', {
      username: username.value,
      password: password.value,
      role: role.value
    })

    if (response.status === 201) {
      alert('注册成功！')
      router.push('/login')
    }
  } catch (error) {
    if (error.response) {
      const message = error.response.data.message
      if (message === 'Username already exists') {
        errors.username = '用户名已存在'
      } else {
        alert('注册失败：' + message)
      }
    } else {
      alert('注册失败，请稍后重试')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.register-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
}

.register-container {
  width: 400px;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

input, select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus, select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.error-message {
  color: #f44336;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

button {
  width: 100%;
  padding: 0.8rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.login-link {
  margin-top: 1.5rem;
  text-align: center;
  color: #666;
}

.login-link a {
  color: #4CAF50;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 