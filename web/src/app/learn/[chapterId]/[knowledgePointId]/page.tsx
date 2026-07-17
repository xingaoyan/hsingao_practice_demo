import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  ArrowLeft, 
  ArrowRight, 
  BookOpen, 
  CheckCircle, 
  Star,
  Clock,
  FileText,
  MessageSquare
} from 'lucide-react';
import Link from 'next/link';
import { 
  getKnowledgePoint, 
  getKnowledgePointsByChapter,
  getLearningRecord 
} from '@/lib/db-queries';
import { getImportanceLabel, getDifficultyLabel, getStatusColor, getStatusLabel } from '@/lib/utils';
import { KnowledgePointActions } from './KnowledgePointActions';
import ReactMarkdown from 'react-markdown';

const USER_ID = 'local-user';

export default async function KnowledgePointPage({
  params,
}: {
  params: { chapterId: string; knowledgePointId: string };
}) {
  const { chapterId, knowledgePointId } = params;
  
  const [kp, chapterKPs, record] = await Promise.all([
    getKnowledgePoint(knowledgePointId),
    getKnowledgePointsByChapter(chapterId),
    getLearningRecord(USER_ID, knowledgePointId),
  ]);
  
  if (!kp) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-muted-foreground">知识点不存在</p>
            <Link href={`/learn/${chapterId}`} className="mt-4">
              <Button variant="outline">返回章节</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  // 找到上一个和下一个知识点
  const currentIndex = chapterKPs.findIndex(k => k.id === knowledgePointId);
  const prevKP = currentIndex > 0 ? chapterKPs[currentIndex - 1] : null;
  const nextKP = currentIndex < chapterKPs.length - 1 ? chapterKPs[currentIndex + 1] : null;
  
  const status = record?.status || 'not_started';
  const tags = kp.tags ? JSON.parse(kp.tags) : [];
  const examPoints = kp.examPoints ? JSON.parse(kp.examPoints) : [];
  
  return (
    <div className="max-w-6xl mx-auto">
      {/* 返回按钮 */}
      <Link 
        href={`/learn/${chapterId}`} 
        className="inline-flex items-center gap-2 text-muted-foreground hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        返回章节
      </Link>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 主内容区 */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl mb-2">{kp.title}</CardTitle>
                  <div className="flex items-center gap-3">
                    <Badge className={getStatusColor(status)}>
                      {getStatusLabel(status)}
                    </Badge>
                    <span className="flex items-center gap-1 text-sm">
                      <Star className="h-4 w-4 text-yellow-500" />
                      {getImportanceLabel(kp.importance || 3)}
                    </span>
                    <span className="flex items-center gap-1 text-sm">
                      <Clock className="h-4 w-4 text-blue-500" />
                      {getDifficultyLabel(kp.difficulty || 3)}
                    </span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* 标签 */}
              {tags.length > 0 && (
                <div className="flex gap-2 mb-6">
                  {tags.map((tag: string) => (
                    <Badge key={tag} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
              
              {/* 内容 */}
              <div className="prose prose-blue max-w-none">
                <ReactMarkdown>{kp.contentMarkdown || ''}</ReactMarkdown>
              </div>
              
              {/* 考点 */}
              {examPoints.length > 0 && (
                <div className="mt-8 p-4 bg-yellow-50 rounded-lg">
                  <h3 className="font-semibold text-yellow-800 mb-2 flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    考试关注点
                  </h3>
                  <ul className="list-disc list-inside space-y-1">
                    {examPoints.map((point: string, index: number) => (
                      <li key={index} className="text-sm text-yellow-700">
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* 导航按钮 */}
          <div className="flex justify-between mt-6">
            {prevKP ? (
              <Link href={`/learn/${chapterId}/${prevKP.id}`}>
                <Button variant="outline" className="flex items-center gap-2">
                  <ArrowLeft className="h-4 w-4" />
                  {prevKP.title}
                </Button>
              </Link>
            ) : (
              <div />
            )}
            {nextKP ? (
              <Link href={`/learn/${chapterId}/${nextKP.id}`}>
                <Button className="flex items-center gap-2">
                  {nextKP.title}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            ) : (
              <div />
            )}
          </div>
        </div>
        
        {/* 侧边栏 */}
        <div className="space-y-6">
          {/* 学习操作 */}
          <KnowledgePointActions 
            userId={USER_ID}
            knowledgePointId={knowledgePointId}
            currentStatus={status}
          />
          
          {/* 来源信息 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">来源信息</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p className="text-muted-foreground">
                  文档: {kp.sectionId || '未知'}
                </p>
                <p className="text-muted-foreground">
                  章节: {chapterId}
                </p>
              </div>
            </CardContent>
          </Card>
          
          {/* 笔记 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                学习笔记
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                笔记功能即将开放...
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
