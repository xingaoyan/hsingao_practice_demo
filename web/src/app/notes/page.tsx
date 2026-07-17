import { Card, CardContent } from '@/components/ui/card';
import { StickyNote } from 'lucide-react';

export default function NotesPage() {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">我的笔记</h1>
      
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <StickyNote className="h-12 w-12 text-gray-400 mb-4" />
          <p className="text-muted-foreground">笔记功能即将开放...</p>
        </CardContent>
      </Card>
    </div>
  );
}
