'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  CheckCircle, 
  RotateCcw, 
  Bookmark,
  Loader2
} from 'lucide-react';
import { useState } from 'react';
import { updateStatus } from './actions';

interface KnowledgePointActionsProps {
  userId: string;
  knowledgePointId: string;
  currentStatus: string;
}

export function KnowledgePointActions({ 
  userId, 
  knowledgePointId, 
  currentStatus 
}: KnowledgePointActionsProps) {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleStatusChange = async (newStatus: string) => {
    setIsLoading(true);
    try {
      const result = await updateStatus(userId, knowledgePointId, newStatus);
      if (!result.success) {
        console.error('Failed to update status');
      }
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">学习操作</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {currentStatus === 'not_started' && (
          <Button 
            className="w-full" 
            onClick={() => handleStatusChange('learning')}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            开始学习
          </Button>
        )}
        
        {currentStatus === 'learning' && (
          <Button 
            className="w-full"
            onClick={() => handleStatusChange('completed')}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <CheckCircle className="h-4 w-4 mr-2" />
            )}
            标记完成
          </Button>
        )}
        
        {currentStatus === 'completed' && (
          <Button 
            variant="outline"
            className="w-full"
            onClick={() => handleStatusChange('reviewing')}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RotateCcw className="h-4 w-4 mr-2" />
            )}
            标记复习
          </Button>
        )}
        
        {currentStatus === 'reviewing' && (
          <Button 
            className="w-full"
            onClick={() => handleStatusChange('completed')}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <CheckCircle className="h-4 w-4 mr-2" />
            )}
            完成复习
          </Button>
        )}
        
        <Button 
          variant="ghost" 
          className="w-full"
          disabled={isLoading}
        >
          <Bookmark className="h-4 w-4 mr-2" />
          收藏
        </Button>
      </CardContent>
    </Card>
  );
}
