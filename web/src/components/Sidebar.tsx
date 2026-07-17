'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  BookOpen, 
  GraduationCap, 
  FileText, 
  HelpCircle, 
  XCircle, 
  StickyNote, 
  Settings,
  Home
} from 'lucide-react';

const navItems = [
  { href: '/', label: '首页', icon: Home },
  { href: '/learn', label: '开始学习', icon: BookOpen },
  { href: '/questions', label: '题库', icon: HelpCircle },
  { href: '/wrong-questions', label: '错题本', icon: XCircle },
  { href: '/materials', label: '资料库', icon: FileText },
  { href: '/notes', label: '笔记', icon: StickyNote },
  { href: '/settings', label: '设置', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  
  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-4">
      <div className="mb-8">
        <Link href="/" className="flex items-center gap-2">
          <GraduationCap className="h-8 w-8 text-blue-600" />
          <span className="text-xl font-bold text-gray-900">架构师学习</span>
        </Link>
      </div>
      
      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || 
            (item.href !== '/' && pathname.startsWith(item.href));
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
