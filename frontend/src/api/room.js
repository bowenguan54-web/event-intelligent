import request from '@/utils/request'

export function getRoomList() {
  return request.get('/api/room/list')
}

export function createRoom(data) {
  return request.post('/api/room/create', data)
}

export function getRoom(id) {
  return request.get(`/api/room/${id}`)
}

export function updateRoom(id, data) {
  return request.put(`/api/room/${id}`, data)
}

export function deleteRoom(id) {
  return request.delete(`/api/room/${id}`)
}

export function getRoomByName(name) {
  return request.get(`/api/room/by-name/${encodeURIComponent(name)}`)
}

export function getRoomListPublic() {
  return request.get('/api/room/public/all')
}
