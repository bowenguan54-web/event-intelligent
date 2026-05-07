import request from '@/utils/request'

export function getMeetingList(params) {
  return request.get('/api/meeting/list', { params })
}

export function getMeetingById(id) {
  return request.get(`/api/meeting/${id}`)
}

export function createMeeting(data) {
  return request.post('/api/meeting/create', data)
}

export function updateMeeting(id, data) {
  return request.put(`/api/meeting/${id}`, data)
}

export function deleteMeeting(id) {
  return request.delete(`/api/meeting/${id}`)
}

export function startMeeting(id) {
  return request.post(`/api/meeting/${id}/start`)
}

export function prepareMeeting(id) {
  return request.post(`/api/meeting/${id}/prepare`)
}

export function getCurrentMeeting() {
  return request.get('/api/meeting/current')
}

export function endMeeting(id) {
  return request.post(`/api/meeting/${id}/end`)
}

export function getMeetingPublic(id) {
  return request.get(`/api/meeting/${id}/public`)
}

export function getMeetingByCode(code) {
  return request.get(`/api/meeting/by-code/${code}`)
}

export function getSeatPerson(meetingId, seatId) {
  return request.get(`/api/meeting/${meetingId}/seat/${seatId}`)
}

export function updateSeatLayout(meetingId, seatLayout) {
  return request.put(`/api/meeting/${meetingId}/seat-layout`, { seat_layout: seatLayout })
}

export function getPublicParticipants(meetingId) {
  return request.get(`/api/meeting/${meetingId}/public-participants`)
}

export function terminalCheckin(meetingId, userId) {
  return request.post(`/api/meeting/${meetingId}/terminal-checkin`, null, { params: { user_id: userId } })
}

export function getPublicAttachments(meetingId, userId) {
  return request.get(`/api/meeting/${meetingId}/public-attachments`, {
    params: userId ? { user_id: userId } : {},
  })
}

export function getParticipantsStatus(meetingId) {
  return request.get(`/api/meeting/${meetingId}/participants-status`)
}

export function updateParticipantsOrder(meetingId, userIds) {
  return request.put(`/api/meeting/${meetingId}/participants-order`, userIds)
}

export function getAttachments(meetingId) {
  return request.get(`/api/meeting/${meetingId}/attachments`)
}

export function uploadAttachment(meetingId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/api/meeting/${meetingId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function updateAttachmentPermissions(meetingId, attachmentId, userIds) {
  return request.put(`/api/meeting/${meetingId}/attachments/${attachmentId}/permissions`, { user_ids: userIds || [] })
}

export function updateAttachmentArchiveSelection(meetingId, attachmentIds) {
  return request.put(`/api/meeting/${meetingId}/attachments/archive`, { attachment_ids: attachmentIds || [] })
}

export function batchDeleteTranscripts(meetingId, segmentIds) {
  return request.delete(`/api/meeting/${meetingId}/transcripts/batch`, { data: { segment_ids: segmentIds || [] } })
}

export function checkConflicts(data) {
  return request.post('/api/meeting/conflict-check', data)
}

export function checkRoomConflict(params) {
  return request.get('/api/meeting/room-conflict-check', { params })
}

export function generateAgenda(meetingId) {
  return request.post(`/api/meeting/${meetingId}/agenda/generate`)
}

export function generateCheckinSheet(meetingId) {
  return request.post(`/api/meeting/${meetingId}/checkin-sheet/generate`)
}

export function getTranscripts(meetingId) {
  return request.get(`/api/meeting/${meetingId}/transcripts`)
}

export function createTranscript(meetingId, data) {
  return request.post(`/api/meeting/${meetingId}/transcript`, data)
}

export function updateTranscript(meetingId, segId, data) {
  return request.put(`/api/meeting/${meetingId}/transcript/${segId}`, data)
}

export function getAudioSegment(meetingId, segId) {
  return `/api/meeting/${meetingId}/audio/${segId}`
}

export function generateKeypoints(meetingId, data) {
  return request.post(`/api/meeting/${meetingId}/keypoints`, data)
}

export function validateTranscripts(meetingId) {
  return request.post(`/api/meeting/${meetingId}/validate`)
}

export function createMinutesRecord(meetingId, data = {}) {
  return request.post(`/api/meeting/${meetingId}/minutes`, data)
}

export function listMinutesRecords(meetingId) {
  return request.get(`/api/meeting/${meetingId}/minutes/list`)
}

export function setPrimaryMinutes(meetingId, minutesId) {
  return request.post(`/api/meeting/${meetingId}/minutes/${minutesId}/set-primary`)
}

export function deleteMinutesRecord(meetingId, minutesId) {
  return request.delete(`/api/meeting/${meetingId}/minutes/${minutesId}`)
}

export function generateMinutes(meetingId, minutesId) {
  return request.post(`/api/meeting/${meetingId}/minutes/generate`, null, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function updateMinutes(meetingId, data, minutesId) {
  return request.put(`/api/meeting/${meetingId}/minutes`, data, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function signMinutes(meetingId, data, minutesId) {
  return request.post(`/api/meeting/${meetingId}/minutes/sign`, data, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function publicSignMinutes(meetingId, data, minutesId) {
  return request.post(`/api/meeting/${meetingId}/minutes/public-sign`, data, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function getMinutesInfo(meetingId, minutesId) {
  return request.get(`/api/meeting/${meetingId}/minutes/info`, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function publishMinutes(meetingId, data = {}) {
  return request.post(`/api/meeting/${meetingId}/minutes/publish`, data)
}

export function rejectMinutes(meetingId, data, minutesId) {
  return request.post(`/api/meeting/${meetingId}/minutes/reject`, data, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function forceCompleteSign(meetingId, minutesId) {
  return request.post(`/api/meeting/${meetingId}/minutes/force-complete`, null, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function getMinutesVersions(meetingId, minutesId) {
  return request.get(`/api/meeting/${meetingId}/minutes/versions`, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function exportMinutes(meetingId, minutesId) {
  return request.get(`/api/meeting/${meetingId}/minutes/export`, {
    params: minutesId ? { minutes_id: minutesId } : {},
  })
}

export function polishText(data) {
  return request.post('/api/ai/polish', data)
}

export function synthesizeSpeech(data) {
  return request.post('/api/tts/synthesize', data)
}

export function aiQA(data) {
  return request.post('/api/ai/qa', data)
}

export function publicMeetingQA(meetingId, question) {
  return request.post(`/api/meeting/${meetingId}/public-ai-qa`, { question })
}

export function getArchivedMeetings(params) {
  return request.get('/api/archive/list', { params })
}

export function getArchivedFull(meetingId) {
  return request.get(`/api/archive/${meetingId}/full-detail`)
}

export function generateMeetingSummary(meetingId) {
  return request.post(`/api/archive/${meetingId}/generate-summary`)
}

export function getMeetingKeypoints(meetingId) {
  return request.get(`/api/archive/${meetingId}/keypoints`)
}

export function getMeetingAllTodos(meetingId) {
  return request.get(`/api/archive/${meetingId}/all-todos`)
}

export function aiExtractTodos(meetingId) {
  return request.post(`/api/archive/${meetingId}/ai-extract-todos`)
}

export function generateClosureReport(meetingId) {
  return request.post(`/api/archive/${meetingId}/generate-report`)
}

export function getMeetingRecordText() {
  return request.get('/api/ai/meeting-record-text')
}

export function getMeetingIssues(meetingId) {
  return request.get(`/api/meeting/${meetingId}/issues`)
}

export function createMeetingIssue(meetingId, data) {
  return request.post(`/api/meeting/${meetingId}/issues`, data)
}

export function updateMeetingIssue(meetingId, issueId, data) {
  return request.put(`/api/meeting/${meetingId}/issues/${issueId}`, data)
}

export function updateIssueReviewStatus(meetingId, data) {
  return request.post(`/api/meeting/${meetingId}/issue-review/status`, data)
}

export function deleteMeetingIssue(meetingId, issueId) {
  return request.delete(`/api/meeting/${meetingId}/issues/${issueId}`)
}

export function submitMeetingIssue(meetingId, issueId) {
  return request.post(`/api/meeting/${meetingId}/issues/${issueId}/submit`)
}

export function getTerminalIssues(meetingId, reporterName) {
  return request.get(`/api/meeting/${meetingId}/terminal-issues`, { params: reporterName ? { reporter_name: reporterName } : {} })
}

export function listPostOpinions(meetingId) {
  return request.get(`/api/meeting/${meetingId}/post-opinions`)
}

export function createPostOpinion(meetingId, data) {
  return request.post(`/api/meeting/${meetingId}/post-opinions`, data)
}

export function createPublicPostOpinion(meetingId, data) {
  return request.post(`/api/meeting/${meetingId}/public-post-opinions`, data)
}

export function terminalSign(meetingId, userId, signatureImage) {
  return request.post(`/api/meeting/${meetingId}/terminal-sign`, { signature_image: signatureImage }, {
    params: { user_id: userId },
  })
}

export function signatureRollback(meetingId, userId) {
  return request.post(`/api/meeting/${meetingId}/signature-rollback`, null, {
    params: { user_id: userId },
  })
}

export function feeSign(meetingId, userId, feeSignatureImage, idCard, bankCard) {
  return request.post(`/api/meeting/${meetingId}/fee-sign`, {
    user_id: userId,
    fee_signature_image: feeSignatureImage,
    fee_id_card: idCard || '',
    fee_bank_card: bankCard || '',
  })
}

export function updateParticipantsRoles(meetingId, expertIds, leaderId) {
  return request.put(`/api/meeting/${meetingId}/participants-roles`, expertIds, {
    params: { leader_id: leaderId || undefined },
  })
}

export function getUserList(params) {
  return request.get('/api/auth/users', { params })
}

export function registerUser(data) {
  return request.post('/api/auth/register', data)
}
