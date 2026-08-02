# CYD Games 门户（gh-pages 部署分支）

多款自研小游戏的汇总门户：`index.html` / `express.html`（大厅）、`gallery.html`（陈列馆）、`atrium.html`（中庭）。

## Spellforge 引用规范（2026-08-02 起生效，长期有效）

- 本门户对《法术工坊 Spellforge》一律**直链引用正版地址**：<https://handkerhandker.github.io/spellforge/>。
- **禁止在本仓库放置该游戏的任何文件副本**（含 `index.html` 原样或改名副本）。`games/spellforge/` 目录已于 2026-08-02 移除，不得回流。
- 原因：副本会造成版本分裂与存档分裂，且旧版副本仍持有排行榜写入配置，会把旧版成绩污染到线上排行榜。
- ⚠️ **给部署/同步脚本维护者**：门户构建源（本地项目的 `src/games.json`、`tools/sync-games.mjs` 等）必须同步应用本规范——将 spellforge 的 `entry` 改为上述正版地址、并从同步名单中移除其文件拷贝，否则下一次整站部署会把副本与旧入口原样带回本仓库。
