import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">设置</h1>
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            个人设置
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            设置功能即将开放...
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
