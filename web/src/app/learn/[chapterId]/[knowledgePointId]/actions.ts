'use server';

import { updateLearningStatus } from '@/lib/db-queries';
import { revalidatePath } from 'next/cache';

export async function updateStatus(userId: string, knowledgePointId: string, status: string) {
  try {
    await updateLearningStatus(userId, knowledgePointId, status);
    revalidatePath(`/learn`);
    return { success: true };
  } catch (error) {
    console.error('Failed to update status:', error);
    return { success: false, error: 'Failed to update status' };
  }
}
