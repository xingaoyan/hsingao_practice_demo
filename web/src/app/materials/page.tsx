import { Card, CardContent } from '@/components/ui/card';
import { FileText } from 'lucide-react';

export default function MaterialsPage() {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">资料库</h1>
      
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mb-4" />
          <p className="text-muted-foreground">资料库功能即将开放...</p>
        </CardContent>
      </Card>
    </div>
  );
}
