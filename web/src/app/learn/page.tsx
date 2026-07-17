import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { BookOpen, ChevronRight } from 'lucide-react';
import Link from 'next/link';
import { getSubjects, getChaptersBySubject, getChapterStats } from '@/lib/db-queries';

const USER_ID = 'local-user';

export default async function LearnPage({
  searchParams,
}: {
  searchParams: { subject?: string };
}) {
  const subjects = await getSubjects();
  const currentSubjectId = searchParams.subject || subjects[0]?.id;
  
  const chapters = currentSubjectId 
    ? await getChaptersBySubject(currentSubjectId) 
    : [];
  
  // 获取每个章节的进度
  const chaptersWithStats = await Promise.all(
    chapters.map(async (chapter) => {
      const stats = await getChapterStats(chapter.id, USER_ID);
      return { ...chapter, stats };
    })
  );
  
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">学习目录</h1>
      
      {/* 科目选择 */}
      <div className="flex gap-4 mb-8">
        {subjects.map((subject) => (
          <Link
            key={subject.id}
            href={`/learn?subject=${subject.id}`}
          >
            <Badge 
              variant={currentSubjectId === subject.id ? "default" : "outline"}
              className="cursor-pointer text-sm py-2 px-4"
            >
              {subject.title}
            </Badge>
          </Link>
        ))}
      </div>
      
      {/* 章节列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {chaptersWithStats.map((chapter) => (
          <Link key={chapter.id} href={`/learn/${chapter.id}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="text-lg">{chapter.title}</span>
                  <ChevronRight className="h-5 w-5 text-gray-400" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                {chapter.description && (
                  <p className="text-sm text-muted-foreground mb-4">
                    {chapter.description}
                  </p>
                )}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">学习进度</span>
                    <span className="font-medium">{chapter.stats.progress}%</span>
                  </div>
                  <Progress value={chapter.stats.progress} />
                  <p className="text-xs text-muted-foreground">
                    已完成 {chapter.stats.completed} / {chapter.stats.total} 个知识点
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
      
      {chapters.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <BookOpen className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-muted-foreground">暂无章节数据</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
