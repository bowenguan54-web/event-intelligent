import request from '@/utils/request'

export function getTodoList(params) {
  return request.get('/api/todo/list', { params })
}

export function createTodo(data) {
  return request.post('/api/todo/create', data)
}

export function updateTodo(id, data) {
  return request.put(`/api/todo/${id}`, data)
}

export function bindFlow(id, data) {
  return request.post(`/api/todo/${id}/bindflow`, data)
}

export function getFlowStatus(id) {
  return request.get(`/api/todo/${id}/flowstatus`)
}

export function getReminders() {
  return request.get('/api/todo/reminders/pending')
}
