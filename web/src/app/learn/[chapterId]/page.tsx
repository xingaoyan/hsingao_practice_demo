import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BookOpen, 
  Star, 
  Clock, 
  CheckCircle,
  ArrowLeft
} from 'lucide-react';
import Link from 'next/link';
import { 
  getKnowledgePointsByChapter, 
  getChapterStats,
  getLearningRecord 
} from '@/lib/db-queries';
import { getImportanceLabel, getDifficultyLabel, getStatusColor, getStatusLabel } from '@/lib/utils';

const USER_ID = 'local-user';

export default async function ChapterPage({
  params,
}: {
  params: { chapterId: string };
}) {
  const { chapterId } = params;
  
  const knowledgePoints = await getKnowledgePointsByChapter(chapterId);
  const stats = await getChapterStats(chapterId, USER_ID);
  
  // 获取每个知识点的学习状态
  const kpsWithStatus = await Promise.all(
    knowledgePoints.map(async (kp) => {
      const record = await getLearningRecord(USER_ID, kp.id);
      return { 
        ...kp, 
        status: record?.status || 'not_started',
        progress: record?.progressPercent || 0,
      };
    })
  );
  
  return (
    <div className="max-w-6xl mx-auto">
      {/* 返回按钮 */}
      <Link 
        href="/learn" 
        className="inline-flex items-center gap-2 text-muted-foreground hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        返回学习目录
      </Link>
      
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          {knowledgePoints[0]?.chapterId || chapterId}
        </h1>
        <div className="text-right">
          <p className="text-sm text-muted-foreground">章节进度</p>
          <p className="text-2xl font-bold">{stats.progress}%</p>
        </div>
      </div>
      
      {/* 进度条 */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">学习进度</span>
            <span className="text-sm text-muted-foreground">
              {stats.completed} / {stats.total} 个知识点
            </span>
          </div>
          <Progress value={stats.progress} />
        </CardContent>
      </Card>
      
      {/* 知识点列表 */}
      <h2 className="text-xl font-semibold text-gray-900 mb-4">知识点列表</h2>
      <div className="space-y-4">
        {kpsWithStatus.map((kp) => (
          <Link key={kp.id} href={`/learn/${chapterId}/${kp.id}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium text-gray-900">{kp.title}</h3>
                      <Badge className={getStatusColor(kp.status)}>
                        {getStatusLabel(kp.status)}
                      </Badge>
                    </div>
                    
                    {kp.summary && (
                      <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                        {kp.summary}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 text-sm">
                      <span className="flex items-center gap-1">
                        <Star className="h-4 w-4 text-yellow-500" />
                        {getImportanceLabel(kp.importance || 3)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4 text-blue-500" />
                        {getDifficultyLabel(kp.difficulty || 3)}
                      </span>
                      {kp.tags && (
                        <div className="flex gap-1">
                          {JSON.parse(kp.tags).slice(0, 3).map((tag: string) => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {kp.status === 'completed' && (
                    <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
                  )}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
      
      {knowledgePoints.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-muted-foreground">该章节暂无知识点</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
