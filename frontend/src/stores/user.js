import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => userInfo.value?.real_name || '')

  async function doLogin(credentials) {
    const res = await login(credentials)
    token.value = res.access_token
    userInfo.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('userInfo', JSON.stringify(res.user))
    return res
  }

  async function doRegister(data) {
    const res = await register(data)
    token.value = res.access_token
    userInfo.value = res.user
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('userInfo', JSON.stringify(res.user))
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    userName,
    doLogin,
    doRegister,
    logout,
  }
})
