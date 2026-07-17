import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  CheckCircle, 
  Clock, 
  Target, 
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import Link from 'next/link';
import { getLearningStats, getSubjects } from '@/lib/db-queries';

const USER_ID = 'local-user';

export default async function HomePage() {
  const [stats, subjects] = await Promise.all([
    getLearningStats(USER_ID),
    getSubjects(),
  ]);
  
  const completionRate = stats.totalKnowledgePoints > 0 
    ? Math.round((stats.completedKnowledgePoints / stats.totalKnowledgePoints) * 100) 
    : 0;
  
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">学习首页</h1>
      
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">已完成知识点</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completedKnowledgePoints}</div>
            <p className="text-xs text-muted-foreground">
              共 {stats.totalKnowledgePoints} 个知识点
            </p>
            <Progress value={completionRate} className="mt-2" />
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">学习中</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.learningKnowledgePoints}</div>
            <p className="text-xs text-muted-foreground">个知识点正在学习</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">答题正确率</CardTitle>
            <Target className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.accuracy}%</div>
            <p className="text-xs text-muted-foreground">
              共 {stats.totalAttempts} 道题
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">待复习错题</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.wrongQuestionCount}</div>
            <p className="text-xs text-muted-foreground">道错题需要复习</p>
          </CardContent>
        </Card>
      </div>
      
      {/* 科目进度 */}
      <h2 className="text-xl font-semibold text-gray-900 mb-4">学习进度</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {subjects.map((subject) => (
          <Card key={subject.id}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{subject.title}</span>
                <Badge variant="outline">{subject.id}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                {subject.description}
              </p>
              <Link 
                href={`/learn?subject=${subject.id}`}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                开始学习 →
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* 快速入口 */}
      <h2 className="text-xl font-semibold text-gray-900 mb-4">快速入口</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link href="/learn">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="flex items-center gap-4 p-4">
              <BookOpen className="h-8 w-8 text-blue-600" />
              <div>
                <p className="font-medium">开始学习</p>
                <p className="text-sm text-muted-foreground">浏览课程目录</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        
        <Link href="/questions">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="flex items-center gap-4 p-4">
              <Target className="h-8 w-8 text-green-600" />
              <div>
                <p className="font-medium">题库练习</p>
                <p className="text-sm text-muted-foreground">巩固知识点</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        
        <Link href="/wrong-questions">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="flex items-center gap-4 p-4">
              <AlertCircle className="h-8 w-8 text-red-600" />
              <div>
                <p className="font-medium">错题本</p>
                <p className="text-sm text-muted-foreground">复习错题</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        
        <Link href="/notes">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardContent className="flex items-center gap-4 p-4">
              <TrendingUp className="h-8 w-8 text-purple-600" />
              <div>
                <p className="font-medium">我的笔记</p>
                <p className="text-sm text-muted-foreground">查看学习笔记</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
