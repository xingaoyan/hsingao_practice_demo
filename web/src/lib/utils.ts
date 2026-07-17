import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date) {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`;
  }
  return `${minutes}分钟`;
}

export function getImportanceLabel(importance: number) {
  const labels: Record<number, string> = {
    1: '了解',
    2: '熟悉',
    3: '掌握',
    4: '重要',
    5: '核心',
  };
  return labels[importance] || '未知';
}

export function getDifficultyLabel(difficulty: number) {
  const labels: Record<number, string> = {
    1: '入门',
    2: '基础',
    3: '中级',
    4: '进阶',
    5: '高级',
  };
  return labels[difficulty] || '未知';
}

export function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    not_started: 'bg-gray-100 text-gray-800',
    learning: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    reviewing: 'bg-yellow-100 text-yellow-800',
    pending: 'bg-gray-100 text-gray-800',
    verified: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    mastered: 'bg-green-100 text-green-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}

export function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    not_started: '未开始',
    learning: '学习中',
    completed: '已完成',
    reviewing: '复习中',
    pending: '待审核',
    verified: '已验证',
    rejected: '已拒绝',
    mastered: '已掌握',
  };
  return labels[status] || status;
}
