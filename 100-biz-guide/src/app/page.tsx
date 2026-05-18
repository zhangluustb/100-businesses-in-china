"use client";

import { useState } from 'react';
import data from '@/data/businesses.json';

const CATEGORY_ICONS: Record<string, string> = {
  '街边小吃摆摊': '🍡',
  '饮品类': '🧋',
  '餐饮小店': '🍜',
  '生活服务': '🧹',
  '零售电商': '🛒',
  '美容健康': '💅',
  '线上自媒体': '📱',
  '教育培训': '📚',
  '汽车出行': '🚗',
  '手工创意': '🎨',
  '社区便民': '🏪',
};

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const categories = data.categories;
  const businesses = data.businesses;
  
  const filteredBusinesses = selectedCategory
    ? businesses.filter(b => b.category === selectedCategory)
    : businesses;
    
  const searchFiltered = searchQuery
    ? filteredBusinesses.filter(b => 
        b.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : filteredBusinesses;
    
  const totalFund = businesses.reduce((sum, b) => {
    const match = b.fund.match(/(\d+\.?\d*)/);
    return sum + (match ? parseFloat(match[1]) : 0);
  }, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-4xl">💼</span>
              <div>
                <h1 className="text-2xl font-bold text-white">100个低成本生意</h1>
                <p className="text-white/60 text-sm">小红书UGC真实数据 · 行业秘籍</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-emerald-400">{businesses.length}</div>
              <div className="text-white/60 text-sm">个行业</div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search */}
        <div className="mb-8">
          <input
            type="text"
            placeholder="搜索行业名称或类别..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-6 py-4 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-white/40 text-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2 mb-8">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              selectedCategory === null
                ? 'bg-purple-500 text-white'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            全部 ({businesses.length})
          </button>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1 ${
                selectedCategory === cat
                  ? 'bg-purple-500 text-white'
                  : 'bg-white/10 text-white/70 hover:bg-white/20'
              }`}
            >
              <span>{CATEGORY_ICONS[cat]}</span>
              <span>{cat}</span>
              <span className="text-xs opacity-60">
                ({businesses.filter(b => b.category === cat).length})
              </span>
            </button>
          ))}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="text-2xl font-bold text-emerald-400">
              {Math.round(totalFund)}万起
            </div>
            <div className="text-white/60 text-sm">最低启动资金</div>
          </div>
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="text-2xl font-bold text-blue-400">{categories.length}</div>
            <div className="text-white/60 text-sm">个行业类别</div>
          </div>
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="text-2xl font-bold text-purple-400">
              {businesses.filter(b => b.links?.length > 0).length}
            </div>
            <div className="text-white/60 text-sm">个有参考链接</div>
          </div>
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10">
            <div className="text-2xl font-bold text-orange-400">
              {searchFiltered.length}
            </div>
            <div className="text-white/60 text-sm">当前显示</div>
          </div>
        </div>

        {/* Business Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {searchFiltered.map(business => (
            <a
              key={business.id}
              href={`/business/${business.id}`}
              className="group bg-white/5 rounded-2xl p-5 border border-white/10 hover:border-purple-500/50 hover:bg-white/10 transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{CATEGORY_ICONS[business.category]}</span>
                  <span className="text-white/40 text-sm font-mono">{business.id}</span>
                </div>
                <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">
                  {business.fund}
                </span>
              </div>
              
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-purple-400 transition-colors">
                {business.name}
              </h3>
              
              <p className="text-white/60 text-sm line-clamp-2 mb-3">
                {business.truth || '点击查看完整行业分析...'}
              </p>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-white/40">{business.category}</span>
                {business.links?.length > 0 && (
                  <span className="text-xs text-purple-400">
                    🔗 {business.links.length} 个参考
                  </span>
                )}
              </div>
            </a>
          ))}
        </div>

        {searchFiltered.length === 0 && (
          <div className="text-center py-16">
            <div className="text-4xl mb-4">🔍</div>
            <p className="text-white/60">没有找到匹配的行业</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center text-white/40 text-sm">
          <p>数据来源：小红书UGC内容 · 仅供参考</p>
        </div>
      </footer>
    </div>
  );
}