import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { XCircle, BookOpen } from 'lucide-react';
import { getWrongQuestions } from '@/lib/db-queries';
import { formatDate, getStatusColor, getStatusLabel } from '@/lib/utils';

const USER_ID = 'local-user';

export default async function WrongQuestionsPage() {
  const wrongQuestions = await getWrongQuestions(USER_ID);
  
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">错题本</h1>
      
      <div className="space-y-4">
        {wrongQuestions.map((item) => (
          <Card key={item.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Badge variant="destructive">错题</Badge>
                  <Badge className={getStatusColor(item.reviewStatus || 'pending')}>
                    {getStatusLabel(item.reviewStatus || 'pending')}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    错误次数: {item.wrongCount}
                  </span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {item.lastWrongAt ? formatDate(item.lastWrongAt) : ''}
                </span>
              </div>
              
              <p className="text-gray-900 mb-4 line-clamp-3">
                {item.questionText}
              </p>
              
              {item.wrongReason && (
                <p className="text-sm text-muted-foreground mb-4">
                  错误原因: {item.wrongReason}
                </p>
              )}
              
              <div className="flex items-center gap-3">
                <Button size="sm">再做一次</Button>
                <Button size="sm" variant="outline">标记已掌握</Button>
                <Button size="sm" variant="ghost">
                  <BookOpen className="h-4 w-4 mr-2" />
                  返回知识点
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {wrongQuestions.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <XCircle className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-muted-foreground">暂无错题记录</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
