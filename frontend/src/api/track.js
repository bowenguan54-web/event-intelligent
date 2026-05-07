import request from '@/utils/request'

export function getTrackStats(meetingId) {
  return request.get(`/api/meeting/${meetingId}/track/stats`)
}

export function getGanttData(meetingId) {
  return request.get(`/api/meeting/${meetingId}/track/gantt`)
}

export function generateReport(meetingId) {
  return request.post(`/api/meeting/${meetingId}/track/report`)
}

export function exportReport(meetingId) {
  return request.get(`/api/meeting/${meetingId}/track/report/export`)
}
