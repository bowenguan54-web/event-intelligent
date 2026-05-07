import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/meeting/list',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'meeting/list',
        name: 'MeetingList',
        component: () => import('@/views/meeting/MeetingList.vue'),
        meta: { title: '会议管理', icon: 'Calendar' },
      },
      {
        path: 'meeting/create',
        name: 'MeetingCreate',
        component: () => import('@/views/meeting/MeetingCreate.vue'),
        meta: { title: '新建会议', icon: 'Plus', parent: { title: '会议管理', path: '/meeting/list' } },
      },
      {
        path: 'meeting/:id/edit',
        name: 'MeetingEdit',
        component: () => import('@/views/meeting/MeetingCreate.vue'),
        meta: { title: '编辑会议', hidden: true, parent: { title: '会议管理', path: '/meeting/list' } },
      },
      {
        path: 'meeting/:id/live',
        name: 'MeetingLive',
        component: () => import('@/views/meeting/MeetingLive.vue'),
        meta: {
          title: '会议进行中',
          hidden: true,
          parents: [
            { title: '会议管理', path: '/meeting/list' },
            { title: '会议详情', paramPath: '/meeting/:id/detail' },
          ],
        },
      },
      {
        path: 'meeting/:id/minutes',
        name: 'MeetingMinutes',
        component: () => import('@/views/meeting/MeetingMinutes.vue'),
        meta: { title: '会议纪要', hidden: true, parent: { title: '会议管理', path: '/meeting/list' } },
      },
      {
        path: 'meeting/:id/issue-review',
        name: 'MeetingIssueReview',
        component: () => import('@/views/meeting/MeetingIssueReview.vue'),
        meta: { title: '问题记录审查', hidden: true, parent: { title: '会议管理', path: '/meeting/list' } },
      },
      {
        path: 'meeting/:id/track',
        name: 'MeetingTrack',
        component: () => import('@/views/meeting/MeetingTrack.vue'),
        meta: { title: '进度跟踪', hidden: true, parent: { title: '会议管理', path: '/meeting/list' } },
      },
      {
        path: 'meeting/:id/detail',
        name: 'MeetingDetail',
        component: () => import('@/views/meeting/MeetingDetail.vue'),
        meta: { title: '会议详情', hidden: true, parent: { title: '会议管理', path: '/meeting/list' } },
      },

      {
        path: 'todo/list',
        name: 'TodoList',
        component: () => import('@/views/todo/TodoList.vue'),
        meta: { title: '待办事项', icon: 'List' },
      },
      {
        path: 'archive',
        name: 'Archive',
        component: () => import('@/views/archive/ArchiveSearch.vue'),
        meta: { title: '归档查询', icon: 'FolderOpened' },
      },
      {
        path: 'meeting/archive',
        name: 'MeetingArchive',
        component: () => import('@/views/meeting/MeetingArchiveTab.vue'),
        meta: { title: '会后事项管理', icon: 'Finished' },
      },
      {
        path: 'room/management',
        name: 'RoomManagement',
        component: () => import('@/views/room/RoomManagement.vue'),
        meta: { title: '会议室管理', icon: 'OfficeBuilding' },
      },
    ],
  },
  {
    path: '/terminal/:id',
    name: 'MeetingTerminal',
    component: () => import('@/views/meeting/MeetingTerminal.vue'),
    meta: { requiresAuth: false, title: '会议终端' },
  },
  {
    path: '/meeting/:id/prepare-screen',
    name: 'MeetingPrepareScreen',
    component: () => import('@/views/meeting/MeetingPrepareWelcome.vue'),
    meta: { requiresAuth: true, title: '会议准备屏' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth !== false && !userStore.token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
