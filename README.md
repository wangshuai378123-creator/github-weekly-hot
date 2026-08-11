# GitHub 每周热点速览

逐周归档 GitHub Trending 热榜，用真实 Star 数据绘制增长曲线，可切换历史周查看。

## 在线地址
- 主站: https://wangshuai378123-creator.github.io/github-weekly-hot/
- 风格备选: `style-dark.html` / `style-paper.html` / `style-glass.html`

## 每周自动更新
GitHub Actions 每周二 09:25（北京时间）自动运行 `每周自动更新` 工作流（`.github/workflows/update-weekly.yml`）:
1. 从 [OpenGithubs/github-weekly-rank](https://github.com/OpenGithubs/github-weekly-rank) 抓取当周榜单（自动解析周次，重复运行幂等跳过）
2. 为新增仓库自动补充中文说明（作用/意义）
3. 更新 `github-trending-data.js`（保留全部历史周与 Star 增长曲线）
4. 提交推送，GitHub Pages 自动重新发布

也可手动触发: 仓库 Actions 页 → `每周自动更新` → Run workflow；
或本地运行 `python update_weekly.py 20260817`（日期传周一发布日即可，脚本自动算周次）。

## 本地预览
```bash
python serve.py 8766
# 打开 http://localhost:8766/
```