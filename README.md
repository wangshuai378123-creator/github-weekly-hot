# GitHub 每周热点速览

逐周归档 GitHub Trending 热榜，用真实 Star 数据绘制增长曲线，可切换历史周查看。

## 在线地址
- 主站: https://wangshuai378123-creator.github.io/github-weekly-hot/
- 风格备选: `style-dark.html` / `style-paper.html` / `style-glass.html`

## 每周自动更新
GitHub Actions 每周二自动运行 `.github/workflows/update-weekly.yml`:
1. 从 [OpenGithubs/github-weekly-rank](https://github.com/OpenGithubs/github-weekly-rank) 抓取当周榜单
2. 更新 `github-trending-data.js`(保留全部历史周)
3. 提交推送, GitHub Pages 自动重新发布

也可手动触发: Actions 页 → Weekly Update → Run workflow;
或本地运行 `python update_weekly.py 20260817 --label W33`。

## 本地预览
```bash
python serve.py 8766
# 打开 http://localhost:8766/
```
