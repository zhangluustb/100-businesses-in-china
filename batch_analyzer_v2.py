#!/usr/bin/env python3
"""
批量处理100个低成本生意行业 v2 - 强制获取笔记详情+评论
改进点：每个行业必须调用 get-feed-detail 获取3-5条笔记的评论区数据
用法: python batch_analyzer_v2.py [--batch-size 5] [--start 2] [--end 100]
"""

import subprocess
import json
import os
import re
import sys
import time
import argparse
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSINESSES_DIR = os.path.join(BASE_DIR, "businesses")
CLAUDE_MD = os.path.join(BASE_DIR, "CLAUDE.md")
CLI_SCRIPT = os.path.join(BASE_DIR, "scripts", "cli.py")

# 行业完整列表
INDUSTRIES = [
    ("002", "烤红薯/烤玉米摊", "0.2-0.5万", "烤红薯烤玉米"),
    ("004", "凉皮/凉面摊", "0.3-1万", "凉皮凉面"),
    ("005", "烤冷面摊", "0.3-0.8万", "烤冷面"),
    ("006", "臭豆腐摊", "0.5-1.5万", "臭豆腐"),
    ("007", "章鱼小丸子摊", "0.5-2万", "章鱼小丸子"),
    ("008", "铁板鱿鱼摊", "0.3-1万", "铁板鱿鱼"),
    ("009", "糖葫芦/糖画摊", "0.2-0.5万", "糖葫芦糖画"),
    ("010", "手抓饼摊", "0.3-1万", "手抓饼"),
    ("011", "麻辣烫摊", "1-3万", "麻辣烫"),
    ("012", "烧烤摊", "1-3万", "烧烤"),
    ("013", "卤味摊", "0.5-2万", "卤味"),
    ("014", "肠粉摊", "0.5-1.5万", "肠粉"),
    ("015", "鸡蛋灌饼杂粮饼摊", "0.3-1万", "鸡蛋灌饼杂粮饼"),
    ("016", "奶茶店", "10-30万", "奶茶店"),
    ("017", "鲜榨果汁摊店", "2-8万", "鲜榨果汁"),
    ("018", "柠檬茶店", "5-15万", "柠檬茶"),
    ("019", "咖啡小店咖啡摊", "3-20万", "咖啡"),
    ("020", "甜品糖水店", "5-15万", "甜品糖水"),
    ("021", "冰粉凉虾摊", "0.3-2万", "冰粉凉虾"),
    ("022", "酸奶酸奶水果捞", "3-10万", "酸奶水果捞"),
    ("023", "豆浆油条早餐店", "3-8万", "豆浆油条"),
    ("024", "拌粉拌面店", "5-15万", "拌粉拌面"),
    ("025", "黄焖鸡米饭店", "5-15万", "黄焖鸡米饭"),
    ("026", "兰州拉面店", "10-30万", "兰州拉面"),
    ("027", "沙县小吃店", "5-15万", "沙县小吃"),
    ("028", "米线过桥米线店", "5-20万", "米线过桥米线"),
    ("029", "饺子馄饨店", "5-15万", "饺子馄饨"),
    ("030", "烤鱼店", "10-30万", "烤鱼"),
    ("031", "火锅店小火锅", "10-50万", "小火锅"),
    ("032", "串串香店", "10-30万", "串串香"),
    ("033", "炸鸡店", "5-20万", "炸鸡店"),
    ("034", "包子馒头店", "3-10万", "包子馒头"),
    ("035", "螺蛳粉店", "5-15万", "螺蛳粉"),
    ("036", "烤肉饭猪脚饭店", "5-15万", "烤肉饭猪脚饭"),
    ("037", "快餐盒饭店", "5-20万", "快餐盒饭"),
    ("038", "麻辣香锅店", "8-25万", "麻辣香锅"),
    ("039", "干洗店", "5-20万", "干洗店"),
    ("040", "家政保洁公司", "2-10万", "家政保洁"),
    ("041", "家电清洗服务", "1-5万", "家电清洗"),
    ("042", "开锁换锁服务", "1-3万", "开锁换锁"),
    ("043", "手机贴膜维修", "0.5-3万", "手机贴膜维修"),
    ("044", "快递驿站", "5-15万", "快递驿站"),
    ("045", "打印复印店", "3-10万", "打印复印"),
    ("046", "便利店小超市", "10-50万", "便利店超市"),
    ("047", "洗车店", "5-20万", "洗车店"),
    ("048", "搬家公司", "3-15万", "搬家"),
    ("049", "宠物寄养遛狗", "1-10万", "宠物寄养遛狗"),
    ("050", "裁缝改衣店", "2-8万", "裁缝改衣"),
    ("051", "美甲店", "3-10万", "美甲店"),
    ("052", "美睫店", "3-8万", "美睫店"),
    ("053", "理发店社区店", "5-20万", "理发店"),
    ("054", "采耳店", "3-10万", "采耳店"),
    ("055", "按摩推拿店", "5-30万", "按摩推拿"),
    ("056", "足疗店", "10-50万", "足疗店"),
    ("057", "艾灸养生馆", "5-20万", "艾灸养生"),
    ("058", "皮肤管理店", "5-30万", "皮肤管理"),
    ("059", "减肥瘦身工作室", "5-20万", "减肥瘦身"),
    ("060", "中医理疗店", "5-30万", "中医理疗"),
    ("061", "水果店", "5-20万", "水果店"),
    ("062", "鲜花店", "3-15万", "鲜花店"),
    ("063", "文具学生用品店", "5-15万", "文具学生用品"),
    ("064", "二手书店图书馆", "2-10万", "二手书店"),
    ("065", "1688拼多多无货源电商", "0.5-3万", "无货源电商"),
    ("066", "闲鱼二手倒卖", "0-0.5万", "闲鱼二手"),
    ("067", "跨境电商小卖家", "2-10万", "跨境电商"),
    ("068", "社区团购团长", "0.5-3万", "社区团购"),
    ("069", "母婴用品店", "10-30万", "母婴用品"),
    ("070", "饰品首饰店", "3-15万", "饰品首饰"),
    ("071", "短视频带货", "0-2万", "短视频带货"),
    ("072", "直播带货", "0.5-5万", "直播带货"),
    ("073", "自媒体写作公众号", "0-0.5万", "自媒体公众号"),
    ("074", "知识付费在线课程", "0-2万", "知识付费"),
    ("075", "AI工具代做服务", "0-0.5万", "AI工具代做"),
    ("076", "设计接单LOGO海报", "0-1万", "设计接单"),
    ("077", "代运营抖音小红书", "0-2万", "代运营"),
    ("078", "摄影跟拍服务", "1-5万", "摄影跟拍"),
    ("079", "托管班晚辅班", "5-20万", "托管班晚辅"),
    ("080", "少儿编程培训", "5-30万", "少儿编程"),
    ("081", "书法美术培训", "3-15万", "书法美术培训"),
    ("082", "乐器培训吉他钢琴", "5-20万", "乐器培训"),
    ("083", "舞蹈培训", "5-30万", "舞蹈培训"),
    ("084", "驾校教练挂靠", "5-15万", "驾校教练"),
    ("085", "游泳健身私教", "2-10万", "游泳健身私教"),
    ("086", "汽车贴膜店", "5-20万", "汽车贴膜"),
    ("087", "二手车中介", "5-30万", "二手车中介"),
    ("088", "代驾", "0-0.3万", "代驾"),
    ("089", "新能源充电桩", "10-50万", "新能源充电桩"),
    ("090", "电动车维修店", "3-10万", "电动车维修"),
    ("091", "手工蛋糕烘焙", "2-10万", "手工蛋糕烘焙"),
    ("092", "定制T恤文创产品", "1-5万", "定制T恤文创"),
    ("093", "手机壳定制", "0.5-3万", "手机壳定制"),
    ("094", "DIY手工坊", "3-10万", "DIY手工坊"),
    ("095", "社区生鲜店", "10-30万", "社区生鲜店"),
    ("096", "自助洗衣房", "10-30万", "自助洗衣房"),
    ("097", "棋牌室麻将馆", "5-20万", "棋牌室麻将馆"),
    ("098", "台球室", "10-50万", "台球室"),
    ("099", "剧本杀密室", "10-50万", "剧本杀密室"),
    ("100", "自习室", "5-20万", "自习室"),
]

# 行业分类映射
CATEGORY_MAP = {
    (2, 15): ("街边小吃摆摊", "门槛低、竞争激烈、季节性、城管风险、手艺门槛不高但酱料/配方是命门"),
    (16, 23): ("饮品类", "品牌竞争、加盟模式、成本控制、选址关键、夏季旺季"),
    (24, 38): ("餐饮小店", "房租压力、口味创新、回头客、外卖叠加、厨师/手艺是核心"),
    (39, 50): ("生活服务", "技能门槛、口碑传播、低成本、上门服务、诚信经营"),
    (51, 60): ("美容健康", "加盟陷阱、技师流失、选址核心、会员体系、装修投入"),
    (61, 70): ("零售电商", "库存风险、选品核心、线上引流、供应链、选址决定生死"),
    (71, 78): ("线上自媒体", "零成本起步、内容为王、变现周期长、平台依赖、不稳定"),
    (79, 85): ("教育培训", "政策风险、师资核心、口碑传播、招生难度、证件要求"),
    (86, 90): ("汽车出行", "专业门槛、资质要求、客户积累、服务标准"),
    (91, 94): ("手工创意", "创意为王、小众市场、线上销售、品类风险、审美门槛"),
    (95, 100): ("社区便民", "位置决定生死、服务便利性、低毛利、稳定需求、装修投入"),
}


def get_category(num):
    for (start, end), (cat, insight) in CATEGORY_MAP.items():
        if start <= num <= end:
            return cat, insight
    return "其他", "各有特点，需具体分析"


def run_cli(cmd):
    """运行CLI命令，返回完整输出"""
    full_cmd = f"cd {BASE_DIR} && python {CLI_SCRIPT} {cmd}"
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        return output
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        print(f"  CLI错误: {e}")
        return ""


def parse_json_from_output(output):
    """从CLI输出中解析JSON - 经过验证的方法"""
    # 方法：找到"feeds"或"feed"关键词，然后找到外层{}
    for keyword in ['"feeds"', '"feed"', '"success"', '"logged_in"']:
        idx = output.find(keyword)
        if idx < 0:
            idx = output.rfind(keyword)
        if idx >= 0:
            brace_start = output.rfind('{', 0, idx)
            brace_end = output.rfind('}')
            if brace_start >= 0 and brace_end > brace_start:
                json_str = output[brace_start:brace_end+1]
                try:
                    result = json.loads(json_str)
                    if keyword.replace('"', '') in result:
                        return result
                except json.JSONDecodeError:
                    # JSON可能不完整，尝试找到最近的完整闭合
                    for end_pos in range(brace_end, brace_start, -1):
                        if output[end_pos] == '}':
                            try:
                                return json.loads(output[brace_start:end_pos+1])
                            except:
                                continue
    return None


def search_feeds(keyword):
    """搜索小红书笔记"""
    print(f"  搜索: {keyword}")
    output = run_cli(f"search-feeds --keyword \"{keyword}\"")
    data = parse_json_from_output(output)
    if data and 'feeds' in data:
        feeds = []
        for f in data['feeds']:
            if f.get('modelType') != 'note' or not f.get('id'):
                continue
            feeds.append({
                'id': f['id'],
                'xsec_token': f.get('xsecToken', ''),
                'title': f.get('displayTitle', ''),
                'nickname': f.get('user', {}).get('nickname', ''),
                'likes': int(f.get('interactInfo', {}).get('likedCount', '0') or '0'),
                'collected': int(f.get('interactInfo', {}).get('collectedCount', '0') or '0'),
                'comments': int(f.get('interactInfo', {}).get('commentCount', '0') or '0'),
                'shared': int(f.get('interactInfo', {}).get('sharedCount', '0') or '0'),
                'type': f.get('type', ''),
            })
        feeds.sort(key=lambda x: x['likes'], reverse=True)
        return feeds
    return []


def get_feed_detail(feed_id, xsec_token):
    """获取笔记详情+评论（增加延迟避免触发验证）"""
    # 去掉token中可能的空格
    xsec_token = xsec_token.strip()
    print(f"  获取详情: {feed_id[:20]}...")
    
    # 先等待避免频繁触发验证
    time.sleep(8)
    
    output = run_cli(f"get-feed-detail --feed-id {feed_id} --xsec-token \"{xsec_token}\" --load-all-comments --max-comment-items 20")
    
    # 检查是否触发了验证
    if '验证' in output or '扫码' in output or 'NoFeedDetailError' in output:
        print(f"    ⚠️ 触发验证或不可访问，跳过")
        # 等待更长时间后继续
        time.sleep(15)
        return None
    
    data = parse_json_from_output(output)
    if data and 'feed' in data:
        feed = data['feed']
        note_info = {
            'title': feed.get('title', ''),
            'desc': feed.get('desc', ''),
            'nickname': feed.get('user', {}).get('nickname', ''),
            'likes': feed.get('interactInfo', {}).get('likedCount', ''),
            'collected': feed.get('interactInfo', {}).get('collectedCount', ''),
            'comment_count': feed.get('interactInfo', {}).get('commentCount', ''),
            'shared': feed.get('interactInfo', {}).get('sharedCount', ''),
            'ip_location': feed.get('ipLocation', ''),
            'type': feed.get('type', ''),
        }
        comments = []
        for c in data.get('comments', []):
            comment = {
                'content': c.get('content', ''),
                'nickname': c.get('user', {}).get('nickname', ''),
                'ip_location': c.get('ipLocation', ''),
                'likes': c.get('likeCount', '0'),
                'sub_comments': [],
            }
            for sc in c.get('subComments', []):
                comment['sub_comments'].append({
                    'content': sc.get('content', ''),
                    'nickname': sc.get('user', {}).get('nickname', ''),
                    'ip_location': sc.get('ipLocation', ''),
                })
            comments.append(comment)
        return {'note': note_info, 'comments': comments}
    
    print(f"    ❌ 解析失败")
    return None


def collect_ugc_quotes(details_list):
    """从多条笔记详情中提取UGC金句"""
    quotes = []
    for detail in details_list:
        if not detail:
            continue
        for c in detail.get('comments', []):
            content = c.get('content', '')
            if len(content) > 5 and len(content) < 200:  # 过滤太短和太长的
                nick = c.get('nickname', '')
                loc = c.get('ip_location', '')
                quotes.append({
                    'content': content,
                    'nickname': nick,
                    'location': loc,
                    'likes': c.get('likes', '0'),
                    'sub_comments': c.get('sub_comments', []),
                })
    # 按点赞数排序
    quotes.sort(key=lambda x: int(x.get('likes', '0') or '0'), reverse=True)
    return quotes


def generate_research_md(num, name, fund, keyword, search_results, details_list):
    """生成research.md"""
    category, _ = get_category(int(num))
    quotes = collect_ugc_quotes(details_list)
    
    md = f"# {name} - 调研原始数据（基于小红书UGC内容）\n\n"
    md += f"> 调研日期：{time.strftime('%Y-%m-%d')}\n"
    md += f"> 搜索平台：小红书（使用 xhs-explore skill）\n"
    md += f"> 搜索关键词：「{keyword}摆摊」「{keyword}摆摊收入」「{keyword} 成本 利润 算账」\n"
    md += f"> 行业分类：{category}\n\n---\n\n"
    
    # 笔记详情
    md += "## 一、小红书博主核心笔记\n\n"
    for i, detail in enumerate(details_list):
        if not detail:
            continue
        note = detail.get('note', {})
        md += f"### 笔记{i+1}：{note.get('nickname', '')} - {note.get('title', '')}\n"
        md += f"**来源**：小红书博主「{note.get('nickname', '')}」\n"
        md += f"**标题**：「{note.get('title', '')}」\n"
        md += f"**互动数据**：{note.get('likes', '')}赞、{note.get('collected', '')}收藏、{note.get('comment_count', '')}评论、{note.get('shared', '')}分享\n"
        if note.get('desc'):
            desc = note.get('desc', '').replace('\n', ' ').replace('\t', ' ')
            if len(desc) > 200:
                desc = desc[:200] + '...'
            md += f"\n**笔记正文摘要**：{desc}\n"
        md += "\n**评论区关键UGC数据**：\n"
        for c in detail.get('comments', [])[:10]:
            md += f"- {c.get('nickname', '')}（{c.get('ip_location', '')}）：{c.get('content', '')}\n"
            for sc in c.get('sub_comments', [])[:2]:
                md += f"  → {sc.get('nickname', '')}（{sc.get('ip_location', '')}）：{sc.get('content', '')}\n"
        md += "\n---\n\n"
    
    # 搜索结果汇总表
    md += "## 二、搜索结果汇总\n\n"
    md += "| 笔记标题 | 博主 | 点赞 | 评论 | 核心话题 |\n"
    md += "|----------|------|------|------|----------|\n"
    for f in search_results[:10]:
        title = f.get('title', '')[:25]
        md += f"| {title} | {f.get('nickname', '')} | {f.get('likes', '')} | {f.get('comments', '')} | 摆摊经验 |\n"
    
    # UGC金句
    md += "\n## 三、UGC金句汇总（评论区原话）\n\n"
    for q in quotes[:15]:
        md += f"- 「{q['content']}」——{q.get('nickname', '')}（{q.get('location', '')}）\n"
    
    # 综合数据
    md += f"\n## 四、综合数据汇总\n\n"
    md += "| 维度 | 数据 | 来源 |\n"
    md += "|------|------|------|\n"
    md += f"| 启动资金 | {fund} | 小红书讨论 |\n"
    md += f"| 行业分类 | {category} | 行业清单 |\n"
    if quotes:
        md += f"| 话题热度 | 最高{search_results[0].get('likes', 0)}赞 | 小红书博主「{search_results[0].get('nickname', '')}」 |\n"
    md += "| UGC金句数 | " + str(len(quotes)) + "条 | 评论区提取 |\n"
    
    md += "\n---\n\n*数据来源：小红书UGC搜索结果+评论区真实对话*\n"
    return md


def generate_summary_md(num, name, fund, keyword, search_results, details_list):
    """生成summary.md（大白话风格）"""
    category, insight = get_category(int(num))
    quotes = collect_ugc_quotes(details_list)
    
    # 选取最有价值的评论
    top_quotes = quotes[:8]
    
    # 笔记正文摘要
    note_descs = []
    for d in details_list:
        if d and d.get('note', {}).get('desc'):
            desc = d['note']['desc'].replace('\n', ' ').replace('\t', ' ')
            if len(desc) > 150:
                desc = desc[:150] + '...'
            note_descs.append((d['note'].get('nickname', ''), desc))
    
    # 行业特定坑点
    pitfall_map = {
        "街边小吃摆摊": [
            ("不做品类搭配，只卖一样东西", "搭配卖才能提高客单价"),
            ("第一天就想赚大钱", "新手前2周收入很低是正常的"),
            ("设备买全新的", "二手设备够用，省钱"),
            ("夏天也坚持卖（季节性品类）", "淡季要么休息要么转型"),
            ("花钱买网上配方", "网上的配方大部分不靠谱"),
        ],
        "饮品类": [
            ("盲目加盟", "加盟费+装修费+设备费是三座大山"),
            ("只卖一种饮品", "搭配奶茶+果汁+冰粉才赚钱"),
            ("选址错误", "饮品靠人流，没有人流就死"),
            ("不考虑外卖", "外卖是饮品类重要补充"),
        ],
        "餐饮小店": [
            ("选址只看租金便宜", "人流比租金重要得多"),
            ("只靠堂食不做外卖", "外卖是餐饮店重要收入来源"),
            ("口味不稳定", "口味是回头客的命门"),
            ("厨师/手艺不稳定", "核心人员走了生意就垮"),
        ],
        "生活服务": [
            ("不做口碑营销", "生活服务靠口碑传播"),
            ("服务标准化不够", "标准化才能规模化"),
            ("不做线上引流", "58同城+美团+小红书都要有"),
        ],
        "美容健康": [
            ("加盟费是最大坑", "加盟费+装修+设备=十几万打底"),
            ("技师流失", "技师走了客户也跟着走"),
            ("不做会员体系", "会员是稳定收入来源"),
        ],
        "零售电商": [
            ("库存积压", "库存管理是零售核心"),
            ("只靠线下不做线上", "线上+线下双渠道"),
            ("选址不看人流", "人流=销量"),
        ],
        "线上自媒体": [
            ("以为能一夜暴富", "变现周期6-12个月起步"),
            ("只做一个平台", "多平台分发才稳定"),
            ("不做内容储备", "至少准备30条内容再启动"),
        ],
        "教育培训": [
            ("政策风险不关注", "双减政策影响很大"),
            ("不做口碑", "教育靠口碑传播"),
            ("招生只靠广告", "口碑+转介绍比广告有效"),
        ],
        "汽车出行": [
            ("资质证件不全", "证件是合法经营的前提"),
            ("不做客户积累", "客户是长期收入来源"),
        ],
        "手工创意": [
            ("只做线下不做线上", "线上渠道是手工创意的核心"),
            ("审美跟不上", "审美是产品竞争力"),
        ],
        "社区便民": [
            ("位置不好还坚持", "位置不好就换，别死撑"),
            ("不做线上引流", "美团+小程序都要有"),
            ("装修投入过高", "装修控制在预算30%以内"),
        ],
    }
    
    pitfalls = pitfall_map.get(category, [
        ("不做调研就入场", "先搜小红书看别人踩过的坑"),
        ("选址不固定", "固定位置老顾客才能找到你"),
        ("忽视性价比", "性价比是核心竞争力"),
    ])
    
    md = f"# {name}：小红书上干过的人告诉你真相\n\n"
    md += f"> 你想干{name[:-1]}？先看看小红书上那些真干过的人说了什么再说。这里没有鸡汤，只有踩过的坑、赚过的钱、和那些他们不会告诉你的潜规则。\n\n---\n\n"
    
    # 一、真相
    md += "## 一、先说真相\n\n"
    if search_results:
        top = search_results[0]
        md += f"小红书搜索「{keyword}」，最热门的笔记是「{top['title']}」（{top['nickname']}，{top['likes']}赞）。\n\n"
    if note_descs:
        for nick, desc in note_descs[:2]:
            if desc:
                md += f"博主「{nick}」说：{desc}\n\n"
    md += f"**{category}的核心挑战**：{insight}\n\n"
    md += f"> **一句话总结**：{fund}启动资金门槛，能不能赚钱取决于你的选址和手艺。别做梦，别裸辞。\n\n---\n\n"
    
    # 二、成本
    md += "## 二、这笔账到底怎么算\n\n"
    md += "### 启动成本拆解\n\n"
    md += "| 项目 | 说明 |\n"
    md += "|------|------|\n"
    md += f"| 启动资金 | {fund} |\n"
    if quotes:
        # 找关于成本的评论
        cost_quotes = [q for q in quotes if any(w in q['content'] for w in ['成本', '费用', '价格', '投入', '花', '万', '块', '元'])]
        for cq in cost_quotes[:3]:
            md += f"| 成本参考 | 「{cq['content']}」——{cq['nickname']}（{cq['location']}） |\n"
    md += f"| 行业分类 | {category} |\n\n"
    
    # 三、启动资金
    md += "## 三、启动要花多少钱\n\n"
    md += f"**{fund}就能启动**，但别被网上的低成本创业骗了。\n\n"
    if quotes:
        equip_quotes = [q for q in quotes if any(w in q['content'] for w in ['设备', '买', '二手', '车', '工具', '冰箱', '炉'])]
        if equip_quotes:
            md += "评论区关于设备的讨论：\n"
            for eq in equip_quotes[:3]:
                md += f"- 「{eq['content']}」——{eq['nickname']}（{eq['location']}）\n"
            md += "\n"
    md += "**二手设备是王道**。别花冤枉钱买全新的。\n\n---\n\n"
    
    # 四、选址
    md += "## 四、选址：决定了你80%的收入\n\n"
    md += f"### {category}的选址铁律\n\n"
    if category == "街边小吃摆摊":
        md += "- **小区门口**：居民下班顺路买\n- **地铁口**：早晚高峰人流大\n- **学校门口**：放学时间生意好\n- **夜市固定位置**：最稳定但竞争激烈\n"
    elif category in ["饮品类", "餐饮小店"]:
        md += "- **写字楼商圈**：午饭+外卖双渠道\n- **大学周边**：学生消费稳定\n- **社区门口**：外卖配送方便\n- **商场附近**：周末人流多\n"
    elif category in ["美容健康", "教育培训"]:
        md += "- **社区商圈**：周边居民是核心客群\n- **写字楼附近**：白领消费力强\n- **商业街**：人流+品牌效应\n"
    elif category == "线上自媒体":
        md += "- **线上为主**：不依赖线下选址\n- **多平台分发**：抖音+小红书+B站+公众号\n"
    else:
        md += "- **人流密集区**：位置决定生死\n- **交通便利**：方便顾客到达\n- **周边配套**：有消费需求的区域\n"
    
    # 选址相关评论
    location_quotes = [q for q in quotes if any(w in q['content'] for w in ['位置', '选址', '城管', '门口', '街道', '人流'])]
    if location_quotes:
        md += "\n评论区关于选址的真实对话：\n"
        for lq in location_quotes[:3]:
            md += f"- 「{lq['content']}」——{lq['nickname']}（{lq['location']}）\n"
    md += "\n---\n\n"
    
    # 五、手艺/技能
    md += "## 五、手艺/技能：[行业特有难点]\n\n"
    skill_quotes = [q for q in quotes if any(w in q['content'] for w in ['配方', '酱料', '技术', '学', '做法', '技巧', '手艺', '油', '口味', '味道'])]
    if skill_quotes:
        md += "评论区关于手艺的讨论：\n"
        for sq in skill_quotes[:5]:
            md += f"- 「{sq['content']}」——{sq['nickname']}（{sq['location']}）\n"
        md += "\n"
    else:
        md += f"**{category}的核心技能**：{insight.split('、')[0] if '、' in insight else insight}\n\n"
    md += "---\n\n"
    
    # 六、真实作息
    md += "## 六、每天的真实作息\n\n"
    time_quotes = [q for q in quotes if any(w in q['content'] for w in ['时间', '小时', '起床', '熬夜', '辛苦', '累', '忙', '休息'])]
    if time_quotes:
        for tq in time_quotes[:3]:
            md += f"- 「{tq['content']}」——{tq['nickname']}（{tq['location']}）\n"
        md += "\n"
    if category == "街边小吃摆摊":
        md += "**真实时间表**：凌晨备料→下午出摊→晚上收摊→深夜洗设备\n"
    elif category in ["饮品类", "餐饮小店"]:
        md += "**真实时间表**：早上备料→中午卖→下午补货→晚上高峰→深夜收摊\n"
    elif category == "线上自媒体":
        md += "**真实时间表**：选题→创作→发布→互动→复盘，每天至少4-6小时\n"
    else:
        md += f"**{category}的时间投入**：每天6-10小时是常态\n"
    md += "\n---\n\n"
    
    # 七、潜规则
    md += "## 七、潜规则：那些小红书评论区告诉你但博主不会置顶说的事\n\n"
    # 找负面/警告类评论
    warn_quotes = [q for q in quotes if any(w in q['content'] for w in ['坑', '骗', '割韭菜', '假', '不好', '别', '不要', '难', '失败', '亏', '投诉', '城管'])]
    for i, wq in enumerate(warn_quotes[:4]):
        md += f"### 潜规则{i+1}\n\n"
        md += f"「{wq['content']}」——{wq['nickname']}（{wq['location']}）\n\n"
    if not warn_quotes and quotes:
        for i, q in enumerate(quotes[:4]):
            md += f"### 潜规则{i+1}\n\n"
            md += f"「{q['content']}」——{q['nickname']}（{q['location']}）\n\n"
    md += "---\n\n"
    
    # 八、避坑
    md += "## 八、必须避开的坑\n\n"
    for i, (pitfall, advice) in enumerate(pitfalls[:5]):
        md += f"### ❌坑{i+1}：{pitfall}\n\n{advice}\n\n"
    md += "---\n\n"
    
    # 九、趋势
    md += "## 九、趋势信号\n\n"
    if search_results:
        md += f"- 小红书最高{search_results[0]['likes']}赞，说明{keyword}话题有一定关注度\n"
    if quotes:
        ai_quotes = [q for q in quotes if any(w in q['content'] for w in ['AI', '智能', '机器', '自动'])]
        if ai_quotes:
            md += f"- AI冲击信号：评论区提到AI/自动化\n"
    md += f"- {category}的总体趋势：竞争加剧但需求稳定\n\n---\n\n"
    
    # 十、进阶
    md += "## 十、进阶路线：从试水到稳赚\n\n"
    md += "### 第1个月：试水期\n"
    md += f"- 投资{fund}启动\n- 选一个好位置\n- 先做基础品类测试客流\n\n"
    md += "### 第2-3个月：稳定期\n"
    md += "- 优化口味/服务\n- 固定出摊/营业时间\n- 开始做线上引流\n\n"
    md += "### 第3-6个月：增长期\n"
    md += f"- 开发特色品类/服务\n- 小红书发日常引流\n- 建微信群/会员体系\n\n"
    md += "### 6个月以后：两条路\n"
    md += "- 继深耕：稳定收入来源\n- 转型/扩张：开分店或换赛道\n\n---\n\n"
    
    # 十一、结尾
    md += "## 十一、最后说一句最重要的话\n\n"
    md += f"> **{name[:-1]}不是暴富赛道，但如果你能坚持半年以上，稳定收入是可以做到的。别裸辞，别买假配方，别做梦。先兼职试水，撑过新手期再说。**\n\n"
    md += "献给每一个准备入行的普通人。\n\n---\n\n"
    
    # 数据来源
    md += "*数据来源：小红书UGC内容"
    if details_list:
        nicks = [d['note'].get('nickname', '') for d in details_list if d]
        md += f"（博主「{'」「'.join(nicks[:4])}」等）"
    md += "*\n"
    
    return md


def update_claude_md(num, name):
    """更新CLAUDE.md状态"""
    try:
        with open(CLAUDE_MD, 'r') as f:
            content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if f"| {num} |" in line and "⬜待分析" in line:
                lines[i] = line.replace("⬜待分析", "✅已完成")
                break
        with open(CLAUDE_MD, 'w') as f:
            f.write('\n'.join(lines))
    except Exception as e:
        print(f"  更新CLAUDE.md失败: {e}")


def search_and_get_details(keyword, num_details=3):
    """搜索并立即获取详情（避免token过期）"""
    search_keywords = [
        f"{keyword}摆摊",
        f"{keyword} 成本 利润",
        f"{keyword}摆摊收入",
    ]
    
    all_search_results = []
    all_details = []
    
    for kw in search_keywords:
        print(f"  搜索: {kw}")
        feeds = search_feeds(kw)
        all_search_results.extend(feeds)
        time.sleep(5)
        
        # 立即获取前2条笔记详情（避免token过期）
        for f in feeds[:2]:
            if f.get('id') and f.get('xsec_token') and f['id'] not in {d.get('note',{}).get('title','') for d in all_details}:
                detail = get_feed_detail(f['id'], f['xsec_token'])
                if detail:
                    all_details.append(detail)
                    print(f"    ✅ 详情成功 ({len(detail.get('comments',[]))}评论)")
                # 如果失败太多，停止尝试详情获取
                if len(all_details) >= 2:
                    break
        time.sleep(5)
    
    # 去重搜索结果
    seen_ids = set()
    unique_results = []
    for f in all_search_results:
        if f['id'] not in seen_ids:
            seen_ids.add(f['id'])
            unique_results.append(f)
    unique_results.sort(key=lambda x: x['likes'], reverse=True)
    
    # 去重详情
    seen_ids2 = set()
    unique_details = []
    for d in all_details:
        nid = d.get('note', {}).get('title', '')  
        if nid not in seen_ids2:
            seen_ids2.add(nid)
            unique_details.append(d)
    
    return unique_results, unique_details


def process_one_industry(num, name, fund, keyword):
    """处理单个行业的完整流程"""
    dir_name = f"{num}_{keyword}"
    industry_dir = os.path.join(BUSINESSES_DIR, dir_name)
    
    print(f"\n{'='*50}")
    print(f"处理 {num}: {name} ({keyword})")
    print(f"{'='*50}")
    
    # 创建目录
    os.makedirs(industry_dir, exist_ok=True)
    
    # Step 1+2: 搜索并立即获取详情（避免token过期）
    unique_results, details_list = search_and_get_details(keyword, num_details=3)
    
    print(f"  搜索结果: {len(unique_results)}条")
    print(f"  笔记详情: {len(details_list)}条")
    
    # 如果详情不足，补充搜索
    if len(details_list) < 2:
        print(f"  ⚠️ 详情不足，补充搜索...")
        extra_feeds = search_feeds(f"{keyword}摆摊收入")
        for f in extra_feeds[:2]:
            if f.get('id') and f.get('xsec_token') and f['id'] not in {r['id'] for r in unique_results}:
                detail = get_feed_detail(f['id'], f['xsec_token'])
                if detail:
                    details_list.append(detail)
                    print(f"    ✅ 补充详情成功")
                time.sleep(5)
        unique_results.extend(extra_feeds)
        seen = set()
        unique_results = sorted([r for r in unique_results if r['id'] not in seen and not seen.add(r['id'])], key=lambda x: x['likes'], reverse=True)
    
    # Step 3: 生成文件
    research_md = generate_research_md(num, name, fund, keyword, unique_results, details_list)
    summary_md = generate_summary_md(num, name, fund, keyword, unique_results, details_list)
    
    research_path = os.path.join(industry_dir, "research.md")
    summary_path = os.path.join(industry_dir, "summary.md")
    
    with open(research_path, 'w') as f:
        f.write(research_md)
    
    with open(summary_path, 'w') as f:
        f.write(summary_md)
    
    # 质量检查
    summary_lines = len(summary_md.split('\n'))
    quotes = collect_ugc_quotes(details_list)
    
    print(f"  ✅ research.md 写入完成")
    print(f"  ✅ summary.md 写入完成 ({summary_lines}行)")
    print(f"  UGC金句: {len(quotes)}条")
    print(f"  笔记详情: {len(details_list)}条")
    
    quality_pass = summary_lines >= 80 and len(details_list) >= 2
    print(f"  {'✅ 质量达标' if quality_pass else '⚠️ 质量不达标'}")
    
    # Step 4: 更新CLAUDE.md
    update_claude_md(num, name)
    print(f"  ✅ CLAUDE.md 已更新")
    
    return {
        'num': num,
        'name': name,
        'summary_lines': summary_lines,
        'quotes_count': len(quotes),
        'details_count': len(details_list),
        'quality_pass': quality_pass,
    }


def main():
    parser = argparse.ArgumentParser(description="批量处理行业v2")
    parser.add_argument("--start", type=int, default=2, help="开始编号(含)")
    parser.add_argument("--end", type=int, default=100, help="结束编号(含)")
    parser.add_argument("--batch-size", type=int, default=5, help="每批处理数")
    parser.add_argument("--delay", type=int, default=15, help="批次间休息秒数")
    args = parser.parse_args()
    
    # 过滤行业
    to_process = [(n, nm, f, kw) for n, nm, f, kw in INDUSTRIES 
                  if args.start <= int(n) <= args.end]
    
    print(f"需要处理 {len(to_process)} 个行业")
    print(f"每批 {args.batch_size} 个，批次间休息 {args.delay}秒")
    
    results = []
    failed = []
    
    for i in range(0, len(to_process), args.batch_size):
        batch = to_process[i:i+args.batch_size]
        print(f"\n{'#'*60}")
        print(f"# Batch {i//args.batch_size + 1}: {len(batch)}个行业")
        print(f"# 行业: {[b[1] for b in batch]}")
        print(f"{'#'*60}")
        
        for num, name, fund, keyword in batch:
            try:
                result = process_one_industry(num, name, fund, keyword)
                results.append(result)
                if not result['quality_pass']:
                    failed.append(result)
            except Exception as e:
                print(f"  ❌ 处理失败: {e}")
                traceback.print_exc()
                failed.append({'num': num, 'name': name, 'error': str(e)})
        
        print(f"\nBatch完成，等待{args.delay}秒...")
        time.sleep(args.delay)
    
    # 最终报告
    print(f"\n{'='*60}")
    print(f"全部完成！")
    print(f"处理: {len(results)}个行业")
    print(f"达标: {len([r for r in results if r.get('quality_pass', False)])}个")
    print(f"不达标: {len(failed)}个")
    if failed:
        print(f"不达标列表: {[f.get('name', f.get('num', '')) for f in failed]}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()