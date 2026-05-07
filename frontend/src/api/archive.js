import request from '@/utils/request'

export function searchArchives(data) {
  return request.post('/api/archive/search', data)
}

export function getArchiveDetail(id) {
  return request.get(`/api/archive/${id}/detail`)
}

export function batchExport(data) {
  return request.post('/api/archive/batch-export', data)
}

export function getExportStatus(taskId) {
  return request.get(`/api/archive/export-status/${taskId}`)
}
