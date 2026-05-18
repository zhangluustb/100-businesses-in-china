import fs from 'fs';
import path from 'path';
import { notFound } from 'next/navigation';

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

const FUND_MAP: Record<string, string> = {
  '001': '0.3-1万', '002': '0.2-0.5万', '003': '0.5-2万', '004': '0.3-1万', '005': '0.3-0.8万',
  '006': '0.5-1.5万', '007': '0.5-2万', '008': '0.3-1万', '009': '0.2-0.5万', '010': '0.3-1万',
  '011': '1-3万', '012': '1-3万', '013': '0.5-2万', '014': '0.5-1.5万', '015': '0.3-1万',
  '016': '10-30万', '017': '2-8万', '018': '5-15万', '019': '3-20万', '020': '5-15万',
  '021': '0.3-2万', '022': '3-10万', '023': '3-8万', '024': '5-15万', '025': '5-15万',
  '026': '10-30万', '027': '5-15万', '028': '5-20万', '029': '5-15万', '030': '10-30万',
  '031': '10-50万', '032': '10-30万', '033': '5-20万', '034': '3-10万', '035': '5-15万',
  '036': '5-15万', '037': '5-20万', '038': '8-25万', '039': '5-20万', '040': '2-10万',
  '041': '1-5万', '042': '1-3万', '043': '0.5-3万', '044': '5-15万', '045': '3-10万',
  '046': '10-50万', '047': '5-20万', '048': '3-15万', '049': '1-10万', '050': '2-8万',
  '051': '3-10万', '052': '3-8万', '053': '5-20万', '054': '3-10万', '055': '5-30万',
  '056': '10-50万', '057': '5-20万', '058': '5-30万', '059': '5-20万', '060': '5-30万',
  '061': '5-20万', '062': '3-15万', '063': '5-15万', '064': '2-10万', '065': '0.5-3万',
  '066': '0-0.5万', '067': '2-10万', '068': '0.5-3万', '069': '10-30万', '070': '3-15万',
  '071': '0-2万', '072': '0.5-5万', '073': '0-0.5万', '074': '0-2万', '075': '0-0.5万',
  '076': '0-1万', '077': '0-2万', '078': '1-5万', '079': '5-20万', '080': '5-30万',
  '081': '3-15万', '082': '5-20万', '083': '5-30万', '084': '5-15万', '085': '2-10万',
  '086': '5-20万', '087': '5-30万', '088': '0-0.3万', '089': '10-50万', '090': '3-10万',
  '091': '2-10万', '092': '1-5万', '093': '0.5-3万', '094': '3-10万', '095': '10-30万',
  '096': '10-30万', '097': '5-20万', '098': '10-50万', '099': '10-50万', '100': '5-20万',
};

const CATEGORIES: Record<string, string> = {
  '001': '街边小吃摆摊', '002': '街边小吃摆摊', '003': '街边小吃摆摊', '004': '街边小吃摆摊',
  '005': '街边小吃摆摊', '006': '街边小吃摆摊', '007': '街边小吃摆摊', '008': '街边小吃摆摊',
  '009': '街边小吃摆摊', '010': '街边小吃摆摊', '011': '街边小吃摆摊', '012': '街边小吃摆摊',
  '013': '街边小吃摆摊', '014': '街边小吃摆摊', '015': '街边小吃摆摊',
  '016': '饮品类', '017': '饮品类', '018': '饮品类', '019': '饮品类', '020': '饮品类',
  '021': '饮品类', '022': '饮品类',
  '023': '餐饮小店', '024': '餐饮小店', '025': '餐饮小店', '026': '餐饮小店', '027': '餐饮小店',
  '028': '餐饮小店', '029': '餐饮小店', '030': '餐饮小店', '031': '餐饮小店', '032': '餐饮小店',
  '033': '餐饮小店', '034': '餐饮小店', '035': '餐饮小店', '036': '餐饮小店', '037': '餐饮小店',
  '038': '餐饮小店',
  '039': '生活服务', '040': '生活服务', '041': '生活服务', '042': '生活服务', '043': '生活服务',
  '044': '生活服务', '045': '生活服务',
  '046': '零售电商', '047': '生活服务', '048': '生活服务', '049': '生活服务', '050': '生活服务',
  '051': '美容健康', '052': '美容健康', '053': '美容健康', '054': '美容健康', '055': '美容健康',
  '056': '美容健康', '057': '美容健康', '058': '美容健康', '059': '美容健康', '060': '美容健康',
  '061': '零售电商', '062': '零售电商', '063': '零售电商', '064': '零售电商',
  '065': '线上自媒体', '066': '线上自媒体', '067': '线上自媒体',
  '068': '零售电商', '069': '零售电商', '070': '零售电商',
  '071': '线上自媒体', '072': '线上自媒体', '073': '线上自媒体', '074': '线上自媒体',
  '075': '线上自媒体', '076': '线上自媒体', '077': '线上自媒体', '078': '线上自媒体',
  '079': '教育培训', '080': '教育培训', '081': '教育培训', '082': '教育培训', '083': '教育培训',
  '084': '汽车出行', '085': '教育培训', '086': '汽车出行', '087': '汽车出行', '088': '汽车出行',
  '089': '汽车出行', '090': '汽车出行',
  '091': '手工创意', '092': '手工创意', '093': '手工创意', '094': '手工创意',
  '095': '社区便民', '096': '社区便民', '097': '社区便民', '098': '社区便民', '099': '社区便民',
  '100': '社区便民',
};

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function BusinessPage({ params }: PageProps) {
  const { id } = await params;
  
  // 找到目录
  const businessesDir = '/Users/zhanglu30/Desktop/0517_100_make_money/businesses';
  const entries = fs.readdirSync(businessesDir).filter(e => e.startsWith(id));
  
  if (entries.length === 0) {
    notFound();
  }
  
  const fullPath = path.join(businessesDir, entries[0]);
  const summaryPath = path.join(fullPath, 'summary.md');
  const researchPath = path.join(fullPath, 'research.md');
  
  if (!fs.existsSync(summaryPath)) {
    notFound();
  }
  
  const summary = fs.readFileSync(summaryPath, 'utf-8');
  const hasResearch = fs.existsSync(researchPath);
  const research = hasResearch ? fs.readFileSync(researchPath, 'utf-8') : '';
  
  const name = entries[0].replace(/^\d+_/, '').replace(/摊$/, '') + '摊';
  const category = CATEGORIES[id] || '其他';
  const fund = FUND_MAP[id] || '未知';
  
  // 提取链接
  const links: { title: string; url: string }[] = [];
  const linkMatches = summary.match(/🔗 \[([^\]]+)\]\(([^)]+)\)/g);
  if (linkMatches) {
    for (const m of linkMatches) {
      const titleMatch = m.match(/🔗 \[([^\]]+)\]/);
      const urlMatch = m.match(/\(([^)]+)\)/);
      if (titleMatch && urlMatch) {
        links.push({ title: titleMatch[1], url: urlMatch[1] });
      }
    }
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <a href="/" className="text-white/60 hover:text-white transition-colors">
              ← 返回
            </a>
            <div className="flex items-center gap-2">
              <span className="text-2xl">{CATEGORY_ICONS[category]}</span>
              <span className="text-white/40 font-mono">{id}</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">{name}</h1>
              <div className="flex items-center gap-2 text-sm text-white/60">
                <span>{category}</span>
                <span>·</span>
                <span className="text-emerald-400">{fund}启动</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Summary Content */}
        <article className="prose prose-invert prose-purple max-w-none">
          <div className="bg-white/5 rounded-2xl p-6 md:p-8 border border-white/10">
            <div className="text-white/90 leading-relaxed whitespace-pre-wrap">
              {summary.split('\n').map((line, i) => {
                // 渲染标题
                if (line.startsWith('## ')) {
                  return (
                    <h2 key={i} className="text-xl font-bold text-purple-400 mt-8 mb-4 first:mt-0">
                      {line.replace('## ', '')}
                    </h2>
                  );
                }
                // 渲染加粗
                if (line.includes('**')) {
                  return (
                    <p key={i} className="mb-3">
                      {line.split('**').map((part, j) => 
                        j % 2 === 1 ? (
                          <strong key={j} className="text-emerald-400 font-semibold">{part}</strong>
                        ) : (
                          part
                        )
                      )}
                    </p>
                  );
                }
                // 渲染引用
                if (line.startsWith('> ')) {
                  return (
                    <blockquote key={i} className="border-l-4 border-purple-500 pl-4 my-4 text-purple-300 italic">
                      {line.replace('> ', '')}
                    </blockquote>
                  );
                }
                // 渲染列表
                if (line.startsWith('- ')) {
                  return (
                    <li key={i} className="ml-4 text-white/80 mb-1">
                      {line.replace('- ', '')}
                    </li>
                  );
                }
                // 渲染普通段落
                if (line.trim()) {
                  return <p key={i} className="mb-3 text-white/80">{line}</p>;
                }
                return null;
              })}
            </div>
          </div>
        </article>

        {/* Reference Links */}
        {links.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-white mb-4">📚 参考来源</h3>
            <div className="space-y-2">
              {links.map((link, i) => (
                <a
                  key={i}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 p-3 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <span className="text-purple-400">🔗</span>
                  <span className="text-white/80 hover:text-purple-400">{link.title}</span>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Research Data */}
        {hasResearch && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-white mb-4">📋 调研数据</h3>
            <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
              <pre className="text-sm text-white/70 whitespace-pre-wrap overflow-x-auto">
                {research.substring(0, 2000)}...
              </pre>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 mt-16">
        <div className="max-w-4xl mx-auto px-4 text-center text-white/40 text-sm">
          <p>数据来源：小红书UGC内容 · 仅供参考</p>
        </div>
      </footer>
    </div>
  );
}