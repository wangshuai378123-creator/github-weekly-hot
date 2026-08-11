# -*- coding: utf-8 -*-
"""
GitHub 每周热点 · 更新脚本
用法: python update_weekly.py <YYYYMMDD> [--label W33] [--range "08.11 — 08.16"]
      (可选 --highlights "A|B|C" --trends "T1|T2")

流程:
  1. 从 OpenGithubs/github-weekly-rank 下载当周榜单 md
  2. 解析 Top12 仓库 (总 Star 与周增长)
  3. 为新增仓库拉取 GitHub API 元数据与中文说明
  4. 追加到 github-trending-data.js (保留历史周)

认证: 优先使用环境变量 GH_TOKEN, 否则读取本机 gh 配置。
"""
import json, os, re, sys, urllib.request, urllib.parse, datetime, time
from concurrent.futures import ThreadPoolExecutor

VIZ = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(VIZ, 'github-trending-data.js')
TOKEN_FILE = os.path.expandvars(r'%APPDATA%\GitHub CLI\hosts.yml')
REPO_RE = r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'

# 中文说明库: repo -> (作用, 意义)
NOTES = {
 'diegosouzapw/OmniRoute': ('免费 AI 网关，一个端点接入 231+ 模型服务商，自动路由与压缩。', '开发者无需逐个对接各家 API 即可切换 Claude/GPT/Gemini，显著降低调用与迁移成本。'),
 'stablyai/orca': ('Stability AI 开源的图像生成模型。', '提供可自托管的高质量文生图能力，推动开源 AIGC 与闭源产品竞争。'),
 'tirth8205/code-review-graph': ('把代码审查记录与关系构建成知识图谱。', '让评审意见、文件依赖、提交历史形成可查询的结构化数据，帮助沉淀评审经验。'),
 'bojieli/ai-agent-book': ('系统讲解 AI Agent 原理与实战的开源书籍。', '从零到一教读者构建智能体，是 Agent 工程化学习地图。'),
 'ruvnet/RuView': ('AI 驱动的视频与内容理解工具。', '自动提取视频要点与摘要，把被动看视频变成主动获取信息。'),
 'block/buzz': ('基于 Nostr 的自托管协作工作区，人类与 AI 智能体共享房间。', '每条消息与操作都是可审计的签名事件，开创去中心化 Agent 协作范式。'),
 'safishamsi/graphify': ('把数据、文档与代码一键转成可视化图谱。', '让复杂关系一目了然，辅助理解与决策。'),
 'Nutlope/hallmark': ('AI 生成营销文案、品牌标语与素材。', '把内容创作门槛降到最低，适合独立开发者与小微企业。'),
 'earendil-works/pi': ('面向 AI 智能体的工具与运行时项目。', '提供可复用的 Agent 组件，帮助开发者更快构建智能体应用。'),
 'baidu/Unlimited-OCR': ('百度开源的高精度 OCR 引擎。', '免费开源、中文效果出色，可自部署替代收费 OCR 服务。'),
 'xai-org/grok-build': ('xAI 推出的 Grok 构建与接入工具链。', '让开发者更便捷地调用 Grok 能力，扩展 xAI 开发者生态。'),
 'oblien/openship': ('开源电商与订单履约全流程工具。', '独立开发者可搭建商品、支付到发货的电商闭环，摆脱平台依赖。'),
 'andrewyng/openworker': ('Andrew Ng 团队开源的多 Agent 协作框架。', '把业界领先的 Agent 编排实践开源，适合学习与二次开发。'),
 'ayghri/i-have-adhd': ('让 AI 输出更高效的技能：行动优先、直接给答案。', '减少冗长铺垫，让回答更快被看懂，提升日常效率。'),
 'permissionlesstech/bitchat': ('去中心化、端到端加密的聊天与通信工具。', '把通信数据主权还给用户，是隐私优先场景的选择。'),
 'alibaba/open-code-review': ('阿里巴巴开源的 AI 代码审查工具。', '把大厂工程级评审经验开放出来，自动发现缺陷与规范问题。'),
 'citrolabs/ego-lite': ('轻量级 AI 智能体与记忆框架。', '以更低资源成本实现 Agent 记忆与自主能力。'),
 'DietrichGebert/ponytail': ('提升日常编码效率的 AI 辅助工具。', '聚焦高频补全与重构，让 AI 融入已有工作流。'),
 'MoonshotAI/Kimi-K3': ('月之暗面开源的大模型 Kimi K3。', '国产开源大模型代表，配合 AirLLM 可在消费级显卡本地运行。'),
 'zhaoxuya520/reverse-skill': ('逆向/渗透/安全研究的 AI 技能路由包。', '把安全研究经验打包成 AI 可调用技能，大幅降低安全测试门槛。'),
 'TencentCloud/TencentDB-Agent-Memory': ('腾讯云 Agent 团队级记忆中枢，沉淀对话、文档与代码。', '解决多 Agent 会话失忆问题，让智能体跨会话共享经验。'),
 'yc-software/qm': ('多人 Agent 协作框架，支持多智能体分工。', '示范如何让 Agent 像团队一样管理任务与结果。'),
 'firecrawl/anydoc': ('把任意文档（PDF/网页/Office）转成干净的 Markdown。', '为 RAG 与大模型预处理提供统一入口，解决文档格式混乱痛点。'),
 'firecrawl/pdf-inspector': ('快速 PDF 检查、分类与文本提取的 Rust 库。', '自动识别扫描件与文本 PDF 并分流处理，是文档智能处理前置利器。'),
 'trycompai/crm': ('Agent 原生的客户关系管理系统。', '用 AI 重构销售与客户跟进流程，让 CRM 从记录工具变成自动执行者。'),
 'virgiliojr94/book-to-skill': ('把技术书籍 PDF 一键转成 Claude Code 可用技能。', '让知识库随取随用，是书到技能到生产力的转化捷径。'),
 'cloudflare/computer': ('Cloudflare 的浏览器与计算基础设施。', '把无头浏览器托管到边缘，与 AI 结合做网页自动化。'),
 'emilkowalski/skills': ('实用 Agent Skills 精选集合。', '提供高质量技能示例与最佳实践，是 Skill 生态样板库。'),
 'lyogavin/airllm': ('低显存大模型推理：4GB 显卡跑 70B 甚至 2.8T 模型。', '让本地推理平民化，无需昂贵硬件即可私有化运行大模型。'),
}

def to_num(s):
    s = s.replace(',', '').strip()
    m = re.search(r'([0-9.]+)\s*([kKwW万]?)', s)
    if not m: return 0
    v = float(m.group(1)); u = m.group(2).lower()
    if u == 'k': v *= 1000
    elif u in ('w', '万'): v *= 10000
    return int(v)

def fetch(url, timeout=40, retries=5):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Codex'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e; time.sleep(2)
    raise last

def parse_table(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('|'): continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 4: continue
        if '项目' in cells[1] or '排名' in cells[0] or 'Star' in cells[2]: continue
        m = re.search(r'\[([^\]]+)\]\(([^)]+)\)', cells[1])
        if not m: continue
        rows.append({'repo': m.group(1), 'url': m.group(2),
                     'stars': to_num(cells[2]), 'week': to_num(cells[3])})
    return rows

def api_get(path, token):
    url = 'https://api.github.com/' + path
    req = urllib.request.Request(url, headers={'User-Agent': 'Codex', 'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read())

def get_token():
    tok = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if tok: return tok
    try:
        txt = open(TOKEN_FILE, encoding='utf-8').read()
        m = re.search(r'oauth_token:\s*"?([A-Za-z0-9_]+)"?', txt)
        if m: return m.group(1)
    except Exception:
        pass
    return None

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    date_str = sys.argv[1]
    label = None; rng = None; highlights = []; trends = []
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--label': label = sys.argv[i+1]; i += 2
        elif sys.argv[i] == '--range': rng = sys.argv[i+1]; i += 2
        elif sys.argv[i] == '--highlights': highlights = sys.argv[i+1].split('|'); i += 2
        elif sys.argv[i] == '--trends': trends = sys.argv[i+1].split('|'); i += 2
        else: i += 1

    y, m, d = date_str[:4], date_str[4:6], date_str[6:8]
    url = f'https://raw.githubusercontent.com/OpenGithubs/github-weekly-rank/main/{y}/{m}/{date_str}.md'
    print('下载:', url)
    try:
        raw = fetch(url).decode('utf-8', 'ignore')
    except Exception as e:
        print('本周数据尚未发布, 跳过 (', e, ')')
        return
    rows = parse_table(raw)[:12]
    if not rows:
        print('未解析到榜单行, 跳过'); return
    end = datetime.date(int(y), int(m), int(d))
    start = end - datetime.timedelta(days=6)
    if not label:
        label = 'W' + str(end.isocalendar()[1])
    if not rng:
        rng = f'{start.month:02d}.{start.day:02d} — {end.month:02d}.{end.day:02d}'

    data = json.loads(re.sub(r'^window\.GH_DATA\s*=\s*', '', open(DATA_FILE, encoding='utf-8').read().rstrip().rstrip(';')))
    token = get_token()

    existing = set(data['repos'].keys())
    new_repos = [r['repo'] for r in rows if r['repo'] not in existing]
    def meta(repo):
        try:
            d = api_get('repos/' + urllib.parse.quote(repo), token)
            note = NOTES.get(repo, ('', ''))
            return repo, {'url': d.get('html_url'), 'lang': d.get('language') or 'N/A',
                          'desc': (d.get('description') or '')[:160],
                          'created': (d.get('created_at') or '')[:10],
                          'stars': d.get('stargazers_count', 0), 'forks': d.get('forks_count', 0),
                          'purpose': note[0], 'significance': note[1], 'history': {}}
        except Exception as e:
            return repo, None
    with ThreadPoolExecutor(max_workers=8) as ex:
        metas = dict(ex.map(meta, new_repos))
    for r in rows:
        repo = r['repo']
        if repo in data['repos']:
            data['repos'][repo]['history'][label] = r['stars']
        elif repo in metas and metas[repo]:
            mm = dict(metas[repo]); mm['history'] = {label: r['stars']}
            data['repos'][repo] = mm
    if not highlights:
        for r in rows[:3]:
            dd = data['repos'].get(r['repo'], {})
            highlights.append(f"{r['repo']} 周增 {r['week']:,}★ — {(dd.get('significance') or dd.get('desc') or '')[:40]}")
    if not trends:
        trends = ['AI Agent 生态持续升温', '本地推理平民化', '大厂加速开源', '开发工具链 AI 化']
    data['weeks'].append({'id': label, 'range': rng, 'end': f'{y}-{m}-{d}',
                          'repos': rows, 'highlights': highlights, 'trends': trends})
    data['generated'] = datetime.date.today().isoformat()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write('window.GH_DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n')
    print(f'完成: 追加 {label} ({rng}), 共 {len(data["weeks"])} 周, 仓库 {len(data["repos"])} 个')

if __name__ == '__main__':
    main()
