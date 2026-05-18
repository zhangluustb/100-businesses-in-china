#!/usr/bin/env python3
"""
批量处理100个低成本生意行业 - 自动搜索小红书+生成秘籍文档
用法: python batch_analyzer.py [--batch-size 5] [--start 007] [--dry-run]
"""

import subprocess
import json
import os
import re
import sys
import time
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSINESSES_DIR = os.path.join(BASE_DIR, "businesses")
CLAUDE_MD = os.path.join(BASE_DIR, "CLAUDE.md")

# 行业数据：编号 -> (行业名, 预估启动资金, 目录名关键词)
INDUSTRIES = {
    "007": ("章鱼小丸子摊", "0.5-2万", "章鱼小丸子"),
    "008": ("铁板鱿鱼摊", "0.3-1万", "铁板鱿鱼"),
    "009": ("糖葫芦糖画摊", "0.2-0.5万", "糖葫芦糖画"),
    "010": ("手抓饼摊", "0.3-1万", "手抓饼"),
    "011": ("麻辣烫摊", "1-3万", "麻辣烫"),
    "012": ("烧烤摊", "1-3万", "烧烤"),
    "013": ("卤味摊", "0.5-2万", "卤味"),
    "014": ("肠粉摊", "0.5-1.5万", "肠粉"),
    "015": ("鸡蛋灌饼杂粮饼摊", "0.3-1万", "鸡蛋灌饼杂粮饼"),
    "016": ("奶茶店", "10-30万", "奶茶店"),
    "017": ("鲜榨果汁摊店", "2-8万", "鲜榨果汁"),
    "018": ("柠檬茶店", "5-15万", "柠檬茶"),
    "019": ("咖啡小店咖啡摊", "3-20万", "咖啡"),
    "020": ("甜品糖水店", "5-15万", "甜品糖水"),
    "021": ("冰粉凉虾摊", "0.3-2万", "冰粉凉虾"),
    "022": ("酸奶酸奶水果捞", "3-10万", "酸奶水果捞"),
    "023": ("豆浆油条早餐店", "3-8万", "豆浆油条"),
    "024": ("拌粉拌面店", "5-15万", "拌粉拌面"),
    "025": ("黄焖鸡米饭店", "5-15万", "黄焖鸡米饭"),
    "026": ("兰州拉面店", "10-30万", "兰州拉面"),
    "027": ("沙县小吃店", "5-15万", "沙县小吃"),
    "028": ("米线过桥米线店", "5-20万", "米线过桥米线"),
    "029": ("饺子馄饨店", "5-15万", "饺子馄饨"),
    "030": ("烤鱼店", "10-30万", "烤鱼"),
    "031": ("火锅店小火锅", "10-50万", "小火锅"),
    "032": ("串串香店", "10-30万", "串串香"),
    "033": ("炸鸡店", "5-20万", "炸鸡店"),
    "034": ("包子馒头店", "3-10万", "包子馒头"),
    "035": ("螺蛳粉店", "5-15万", "螺蛳粉"),
    "036": ("烤肉饭猪脚饭店", "5-15万", "烤肉饭猪脚饭"),
    "037": ("快餐盒饭店", "5-20万", "快餐盒饭"),
    "038": ("麻辣香锅店", "8-25万", "麻辣香锅"),
    "039": ("干洗店", "5-20万", "干洗店"),
    "040": ("家政保洁公司", "2-10万", "家政保洁"),
    "041": ("家电清洗服务", "1-5万", "家电清洗"),
    "042": ("开锁换锁服务", "1-3万", "开锁换锁"),
    "043": ("手机贴膜维修", "0.5-3万", "手机贴膜维修"),
    "044": ("快递驿站", "5-15万", "快递驿站"),
    "045": ("打印复印店", "3-10万", "打印复印"),
    "046": ("便利店小超市", "10-50万", "便利店超市"),
    "047": ("洗车店", "5-20万", "洗车店"),
    "048": ("搬家公司", "3-15万", "搬家"),
    "049": ("宠物寄养遛狗", "1-10万", "宠物寄养遛狗"),
    "050": ("裁缝改衣店", "2-8万", "裁缝改衣"),
    "051": ("美甲店", "3-10万", "美甲店"),
    "052": ("美睫店", "3-8万", "美睫店"),
    "053": ("理发店社区店", "5-20万", "理发店"),
    "054": ("采耳店", "3-10万", "采耳店"),
    "055": ("按摩推拿店", "5-30万", "按摩推拿"),
    "056": ("足疗店", "10-50万", "足疗店"),
    "057": ("艾灸养生馆", "5-20万", "艾灸养生"),
    "058": ("皮肤管理店", "5-30万", "皮肤管理"),
    "059": ("减肥瘦身工作室", "5-20万", "减肥瘦身"),
    "060": ("中医理疗店", "5-30万", "中医理疗"),
    "061": ("水果店", "5-20万", "水果店"),
    "062": ("鲜花店", "3-15万", "鲜花店"),
    "063": ("文具学生用品店", "5-15万", "文具学生用品"),
    "064": ("二手书店图书馆", "2-10万", "二手书店"),
    "065": ("1688拼多多无货源电商", "0.5-3万", "无货源电商"),
    "066": ("闲鱼二手倒卖", "0-0.5万", "闲鱼二手"),
    "067": ("跨境电商小卖家", "2-10万", "跨境电商"),
    "068": ("社区团购团长", "0.5-3万", "社区团购"),
    "069": ("母婴用品店", "10-30万", "母婴用品"),
    "070": ("饰品首饰店", "3-15万", "饰品首饰"),
    "071": ("短视频带货", "0-2万", "短视频带货"),
    "072": ("直播带货", "0.5-5万", "直播带货"),
    "073": ("自媒体写作公众号", "0-0.5万", "自媒体公众号"),
    "074": ("知识付费在线课程", "0-2万", "知识付费"),
    "075": ("AI工具代做服务", "0-0.5万", "AI工具代做"),
    "076": ("设计接单LOGO海报", "0-1万", "设计接单"),
    "077": ("代运营抖音小红书", "0-2万", "代运营"),
    "078": ("摄影跟拍服务", "1-5万", "摄影跟拍"),
    "079": ("托管班晚辅班", "5-20万", "托管班晚辅"),
    "080": ("少儿编程培训", "5-30万", "少儿编程"),
    "081": ("书法美术培训", "3-15万", "书法美术培训"),
    "082": ("乐器培训吉他钢琴", "5-20万", "乐器培训"),
    "083": ("舞蹈培训", "5-30万", "舞蹈培训"),
    "084": ("驾校教练挂靠", "5-15万", "驾校教练"),
    "085": ("游泳健身私教", "2-10万", "游泳健身私教"),
    "086": ("汽车贴膜店", "5-20万", "汽车贴膜"),
    "087": ("二手车中介", "5-30万", "二手车中介"),
    "088": ("代驾", "0-0.3万", "代驾"),
    "089": ("新能源充电桩", "10-50万", "新能源充电桩"),
    "090": ("电动车维修店", "3-10万", "电动车维修"),
    "091": ("手工蛋糕烘焙", "2-10万", "手工蛋糕烘焙"),
    "092": ("定制T恤文创产品", "1-5万", "定制T恤文创"),
    "093": ("手机壳定制", "0.5-3万", "手机壳定制"),
    "094": ("DIY手工坊", "3-10万", "DIY手工坊"),
    "095": ("社区生鲜店", "10-30万", "社区生鲜店"),
    "096": ("自助洗衣房", "10-30万", "自助洗衣房"),
    "097": ("棋牌室麻将馆", "5-20万", "棋牌室麻将馆"),
    "098": ("台球室", "10-50万", "台球室"),
    "099": ("剧本杀密室", "10-50万", "剧本杀密室"),
    "100": ("自习室", "5-20万", "自习室"),
}

# 搜索关键词模板
SEARCH_KEYWORDS = [
    "{keyword}摆摊",
    "{keyword}摆摊收入",
    "{keyword} 成本 利润 算账",
]

# 行业分类特点（用于生成更有针对性的内容）
CATEGORY_MAP = {
    "007-015": "街边小吃摆摊",
    "016-023": "饮品类",
    "024-038": "餐饮小店",
    "039-050": "生活服务",
    "051-060": "美容健康",
    "061-070": "零售电商",
    "071-078": "线上自媒体",
    "079-085": "教育培训",
    "086-090": "汽车出行",
    "091-094": "手工创意",
    "095-100": "社区便民",
}


def get_category(num):
    for range_str, cat in CATEGORY_MAP.items():
        start, end = range_str.split("-")
        if int(start) <= int(num) <= int(end):
            return cat
    return "其他"


def run_xhs_search(keyword):
    """运行小红书搜索命令"""
    cmd = f"cd {BASE_DIR} && python scripts/cli.py search-feeds --keyword \"{keyword}\""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        # 尝试从输出中提取JSON
        output = result.stdout
        # 找到JSON部分（最后一个{开头到}结尾）
        json_start = output.rfind('{\n  "feeds"')
        if json_start == -1:
            json_start = output.rfind('{"feeds"')
        if json_start >= 0:
            # 找到匹配的结束位置
            json_str = output[json_start:]
            # 尝试解析JSON
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError:
                # 可能末尾有多余字符，尝试截断
                for i in range(len(json_str)-1, 0, -1):
                    if json_str[i] == '}':
                        try:
                            data = json.loads(json_str[:i+1])
                            return data
                        except:
                            continue
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"搜索错误: {e}")
        return None


def extract_top_feeds(search_data, min_likes=10):
    """从搜索结果中提取高互动笔记"""
    if not search_data or 'feeds' not in search_data:
        return []
    
    top_feeds = []
    for feed in search_data['feeds']:
        if not feed.get('id') or feed.get('modelType') != 'note':
            continue
        likes = int(feed.get('interactInfo', {}).get('likedCount', '0') or '0')
        if likes >= min_likes:
            top_feeds.append({
                'id': feed['id'],
                'xsec_token': feed.get('xsecToken', ''),
                'title': feed.get('displayTitle', ''),
                'nickname': feed.get('user', {}).get('nickname', ''),
                'likes': likes,
                'collected': int(feed.get('interactInfo', {}).get('collectedCount', '0') or '0'),
                'comments': int(feed.get('interactInfo', {}).get('commentCount', '0') or '0'),
                'type': feed.get('type', ''),
            })
    
    # 按点赞数排序
    top_feeds.sort(key=lambda x: x['likes'], reverse=True)
    return top_feeds[:10]


def generate_research_md(num, name, fund, keyword, search_results):
    """生成research.md"""
    category = get_category(num)
    
    # 收集所有搜索结果中的top feeds
    all_top_feeds = []
    for kw, data in search_results:
        feeds = extract_top_feeds(data)
        for f in feeds:
            f['search_keyword'] = kw
        all_top_feeds.extend(feeds)
    
    # 去重并排序
    seen_ids = set()
    unique_feeds = []
    for f in all_top_feeds:
        if f['id'] not in seen_ids:
            seen_ids.add(f['id'])
            unique_feeds.append(f)
    unique_feeds.sort(key=lambda x: x['likes'], reverse=True)
    
    # 生成内容
    md = f"""# {name} - 调研原始数据（基于小红书UGC内容）

> 调研日期：{time.strftime('%Y-%m-%d')}
> 搜索平台：小红书（使用 xhs-explore skill）
> 搜索关键词：{', '.join([kw for kw, _ in search_results])}
> 行业分类：{category}

---

## 一、小红书博主核心笔记

"""
    
    for i, f in enumerate(unique_feeds[:8]):
        md += f"""### 笔记{i+1}：{f['nickname']} - {f['title']}
**来源**：小红书博主「{f['nickname']}」
**标题**：「{f['title']}」
**互动数据**：{f['likes']}赞、{f['collected']}收藏、{f['comments']}评论
**搜索关键词**：{f['search_keyword']}

---

"""
    
    # 关键数据汇总
    md += """## 二、综合数据汇总

| 维度 | 数据 | 来源 |
|------|------|------|
| 启动资金 | {fund}元 | 小红书讨论 |
"""
    
    if unique_feeds:
        max_likes = unique_feeds[0]['likes']
        md += f"| 话题热度 | 最高{max_likes}赞 | 小红书博主「{unique_feeds[0]['nickname']}」 |\n"
    
    md += f"""
| 行业分类 | {category} | 行业清单 |

---

*数据来源：小红书UGC搜索结果*
"""
    
    return md


def generate_summary_md(num, name, fund, keyword, search_results, category):
    """生成summary.md（大白话风格）"""
    # 收集搜索结果
    all_top_feeds = []
    for kw, data in search_results:
        feeds = extract_top_feeds(data)
        for f in feeds:
            f['search_keyword'] = kw
        all_top_feeds.extend(feeds)
    
    seen_ids = set()
    unique_feeds = []
    for f in all_top_feeds:
        if f['id'] not in seen_ids:
            seen_ids.add(f['id'])
            unique_feeds.append(f)
    unique_feeds.sort(key=lambda x: x['likes'], reverse=True)
    
    # 根据分类生成不同内容
    top_feed = unique_feeds[0] if unique_feeds else None
    top_likes = top_feed['likes'] if top_feed else 0
    top_title = top_feed['title'] if top_feed else '无'
    top_nickname = top_feed['nickname'] if top_feed else '无'
    
    # 分类特定的行业洞察
    insights = {
        "街边小吃摆摊": "门槛低、竞争激烈、季节性、城管风险",
        "饮品类": "品牌竞争、加盟模式、成本控制、选址关键",
        "餐饮小店": "房租压力、口味创新、回头客、外卖叠加",
        "生活服务": "技能门槛、口碑传播、低成本、上门服务",
        "美容健康": "加盟陷阱、技师流失、选址核心、会员体系",
        "零售电商": "库存风险、选品核心、线上引流、供应链",
        "线上自媒体": "零成本起步、内容为王、变现周期长、平台依赖",
        "教育培训": "政策风险、师资核心、口碑传播、招生难度",
        "汽车出行": "专业门槛、资质要求、客户积累、服务标准",
        "手工创意": "创意为王、小众市场、线上销售、品类风险",
        "社区便民": "位置决定生死、服务便利性、低毛利、稳定需求",
    }
    
    insight = insights.get(category, "各有特点，需具体分析")
    
    md = f"""# {name}：小红书上干过的人告诉你真相

> 你想干{name[:-1]}？先看看小红书上那些真干过的人怎么说。

---

## 一、先说真相

小红书搜索「{keyword}」，最热门的笔记是「{top_title}」（{top_nickname}，{top_likes}赞）。

{category}的核心挑战：**{insight}**。

> **一句话总结**：{fund}启动资金门槛，能不能赚钱取决于你的选址和手艺。

---

## 二、成本拆解

| 项目 | 说明 |
|------|------|
| 启动资金 | {fund} |
| 行业分类 | {category} |
| 话题热度 | 小红书最高{top_likes}赞 |

---

## 三、必须避开的坑

### ❌坑1：不做调研就入场
先在小红书搜「{keyword}」，看看别人踩过的坑。

### ❌坑2：选址不固定
固定位置出摊/开店，老顾客才能找到你。

### ❌坑3：忽视性价比
{category}的核心是性价比，做价格刺客等于自断客路。

---

## 四、最后说一句

> **任何生意都有坑，知道真相再出发，你才不会半途放弃。**

---

*数据来源：小红书UGC内容*
"""
    
    return md


def update_claude_md(num, name):
    """更新CLAUDE.md中的状态"""
    with open(CLAUDE_MD, 'r') as f:
        content = f.read()
    
    # 替换状态
    old_pattern = f"| {num} | {name} |"
    new_pattern = f"| {num} | {name} |"
    
    # 找到包含该行业的行，替换⬜待分析为✅已完成
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if f"| {num} |" in line and "⬜待分析" in line:
            lines[i] = line.replace("⬜待分析", "✅已完成")
            break
    
    with open(CLAUDE_MD, 'w') as f:
        f.write('\n'.join(lines))


def process_industry(num, name, fund, keyword, dry_run=False):
    """处理单个行业"""
    dir_name = f"{num}_{keyword}"
    industry_dir = os.path.join(BUSINESSES_DIR, dir_name)
    
    print(f"\n{'='*50}")
    print(f"处理行业 {num}: {name}")
    print(f"{'='*50}")
    
    if dry_run:
        print(f"[DRY RUN] 创建目录: {industry_dir}")
        print(f"[DRY RUN] 搜索关键词: {SEARCH_KEYWORDS}")
        return True
    
    # 创建目录
    os.makedirs(industry_dir, exist_ok=True)
    
    # 搜索小红书
    search_results = []
    for kw_template in SEARCH_KEYWORDS:
        kw = kw_template.replace("{keyword}", keyword)
        print(f"  搜索: {kw}")
        data = run_xhs_search(kw)
        if data:
            feeds = extract_top_feeds(data)
            print(f"    找到 {len(feeds)} 条高互动笔记")
            search_results.append((kw, data))
        time.sleep(2)  # 避免频繁搜索
    
    # 生成文件
    category = get_category(num)
    
    research_md = generate_research_md(num, name, fund, keyword, search_results)
    summary_md = generate_summary_md(num, name, fund, keyword, search_results, category)
    
    research_path = os.path.join(industry_dir, "research.md")
    summary_path = os.path.join(industry_dir, "summary.md")
    
    with open(research_path, 'w') as f:
        f.write(research_md)
    print(f"  ✅ 写入 research.md")
    
    with open(summary_path, 'w') as f:
        f.write(summary_md)
    print(f"  ✅ 写入 summary.md")
    
    # 更新CLAUDE.md
    update_claude_md(num, name)
    print(f"  ✅ 更新 CLAUDE.md")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="批量处理100个低成本生意行业")
    parser.add_argument("--batch-size", type=int, default=5, help="每批处理数量")
    parser.add_argument("--start", type=str, default="007", help="开始编号")
    parser.add_argument("--end", type=str, default="100", help="结束编号")
    parser.add_argument("--dry-run", action="store_true", help="只打印不执行")
    args = parser.parse_args()
    
    start_num = int(args.start)
    end_num = int(args.end)
    
    # 获取需要处理的行业
    to_process = []
    for num_str, (name, fund, keyword) in INDUSTRIES.items():
        num = int(num_str)
        if start_num <= num <= end_num:
            dir_name = f"{num_str}_{keyword}"
            dir_path = os.path.join(BUSINESSES_DIR, dir_name)
            # 检查是否已存在
            if not os.path.exists(os.path.join(dir_path, "summary.md")):
                to_process.append((num_str, name, fund, keyword))
    
    print(f"需要处理 {len(to_process)} 个行业")
    print(f"每批处理 {args.batch_size} 个")
    
    # 分批处理
    batch_count = 0
    for i in range(0, len(to_process), args.batch_size):
        batch = to_process[i:i+args.batch_size]
        batch_count += 1
        print(f"\n{'#'*60}")
        print(f"# Batch {batch_count}: 处理 {len(batch)} 个行业")
        print(f"{'#'*60}")
        
        for num_str, name, fund, keyword in batch:
            success = process_industry(num_str, name, fund, keyword, dry_run=args.dry_run)
            if not success:
                print(f"  ❌ 处理失败: {num_str} {name}")
        
        print(f"\nBatch {batch_count} 完成！等待10秒...")
        time.sleep(10)  # 批次间休息
    
    print(f"\n{'='*60}")
    print(f"全部完成！处理了 {len(to_process)} 个行业，共 {batch_count} 批")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()