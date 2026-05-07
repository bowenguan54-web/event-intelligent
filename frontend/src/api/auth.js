import request from '@/utils/request'

export function login(data) {
  return request.post('/api/auth/login', data)
}

export function register(data) {
  return request.post('/api/auth/register', data)
}

export function getUserInfo() {
  return request.get('/api/auth/me')
}

export function getUsers(params) {
  return request.get('/api/auth/users', { params })
}

export function createParticipant(data) {
  return request.post('/api/auth/participants', data)
}

export function deleteParticipant(userId) {
  return request.delete(`/api/auth/participants/${userId}`)
}
