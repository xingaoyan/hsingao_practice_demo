import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { HelpCircle, Filter } from 'lucide-react';
import { getQuestions } from '@/lib/db-queries';

export default async function QuestionsPage() {
  const questions = await getQuestions({ limit: 20 });
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">题库</h1>
        <Button variant="outline" className="flex items-center gap-2">
          <Filter className="h-4 w-4" />
          筛选
        </Button>
      </div>
      
      <div className="space-y-4">
        {questions.map((question) => (
          <Card key={question.id}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Badge variant="outline">{question.questionType}</Badge>
                  <Badge variant="secondary">{question.sourceType}</Badge>
                  {question.year && (
                    <Badge>{question.year}年</Badge>
                  )}
                </div>
                <span className="text-sm text-muted-foreground">
                  ID: {question.id}
                </span>
              </div>
              
              <p className="text-gray-900 mb-4 line-clamp-3">
                {question.questionText}
              </p>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    难度: {question.difficulty}/5
                  </span>
                </div>
                <Button size="sm">开始答题</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {questions.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <HelpCircle className="h-12 w-12 text-gray-400 mb-4" />
            <p className="text-muted-foreground">暂无题目数据</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
