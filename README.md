# Survivalcraft (SC) 完全学习笔记

> 🌐 **在线阅读（GitHub Pages）**：https://3366434156.github.io/survivalcraft-notes/  
> 更新流程：改 md → `python wiki/build_wiki.py` 重生成 docs/ → git push 即自动上线。

> 独立知识库：只含 Survivalcraft 引擎/游戏层（源码 E:\SurvivalcraftAPIProject）的学习笔记，**不含任何 mod 项目内容**。
> 页面行号为 2026-10-31 实读所得；行号跳转依赖本机存在 E:\SurvivalcraftAPIProject 源码树。

## 快速开始（三跳查找协议）

1. 先看下方"页面地图"选页 → 页内"快查路由"→"目录地图"拿绝对路径 → 直接跳源码 `file:line`。
2. 页面没覆盖 → Grep `E:\SurvivalcraftAPIProject` → **把发现回写进对应页面**（库越用越准）。
3. 抄范例先看 [45-SC原版范例菜谱](45-SC原版范例菜谱.md)；坑在各页"坑与对策"节。

## 页面地图（10-SC引擎\）

| 页 | 覆盖 | 状态 |
|---|---|---|
| [01-程序入口与主循环](10-SC引擎/01-程序入口与主循环.md) | Program/Window/ScreensManager/GameScreen 一帧全序 | 全读 |
| [02-Subsystem体系](10-SC引擎/02-Subsystem体系.md) | Subsystem/Project/加载保存/更新驱动 + 40 业务子系统 | 全读111/111 · [02a 逐文件明细](10-SC引擎/02a-子系统明细.md) |
| [03-实体与组件体系](10-SC引擎/03-实体与组件体系.md) | Entity/Component 契约 + 91 组件族 | 全读91/91 · [03a 逐文件明细](10-SC引擎/03a-组件明细.md) |
| [04-方块系统](10-SC引擎/04-方块系统.md) | Block 116 虚方法/BlocksManager/304 方块 | 见页首状态 · [04a 逐文件明细](10-SC引擎/04a-方块明细.md) |
| [05-世界与地形生成](10-SC引擎/05-世界与地形生成.md) | 区块十态/TCG 生成器族 | 见页首状态 · [05a 明细](10-SC引擎/05a-地形生成明细.md) |
| [06-渲染管线与着色器](10-SC引擎/06-渲染管线与着色器.md) | Graphics/语义头/预乘alpha/批次 | 抽样→待波次 |
| [07-粒子系统](10-SC引擎/07-粒子系统.md) | ParticleSystem 基类与新增 5 步 | 抽样→待波次 |
| [08-音频系统](10-SC引擎/08-音频系统.md) | OpenAL/播放链/格式嗅探 | Engine.Audio 全读 |
| [09-UI与Widget体系](10-SC引擎/09-UI与Widget体系.md) | 布局/命中/Update必调base/XML解析 | 抽样→待波次 |
| [10-输入与相机](10-SC引擎/10-输入与相机.md) | 输入分发/键位/相机类族 | 抽样→待波次 |
| [11-存档持久化](10-SC引擎/11-存档持久化.md) | 存档 6+9 步/ValuesDictionary 硬拆箱 | 核心全读 |
| [12-ModAPI与加载链](10-SC引擎/12-ModAPI与加载链.md) | modinfo 13键/加载 20 步/HarmonyX | 关键段全读 |
| [13-物理与碰撞](10-SC引擎/13-物理与碰撞.md) | ComponentBody 全链/碰撞对O(n²)/弹道/爆炸 | 全读 |
| [14-光照天空与天气](10-SC引擎/14-光照天空与天气.md) | 光照0-15/昼夜曲线/天气状态机 | 全读 |
| [15-电学与机构](10-SC引擎/15-电学与机构.md) | 电路 tick 链/自定义元件 4 步 | 主链全读 |

（"抽样→待波次"= 该页仍在按深学计划逐批推进到全读，见库外私有笔记 `50-深学台账.md` A 区进度。）

## 原版范例（最快照抄入口）

[45-SC原版范例菜谱.md](45-SC原版范例菜谱.md) —— 任务 → 最快照抄的原版实现（AI行为/方块/子系统/存档/粒子/弹道/电力…）。

## 写作规则

见 [00-页面模板与规则.md](00-页面模板与规则.md)。核心铁律：绝对路径+实读行号、零空话、单页≤350行、每页必有"原版范例"表、**本库零 mod 内容（域隔离）**。

## 对 mod 开发者的提示

- 本库页首状态行的"全读(N/M)"= 该目录源码文件实读覆盖数。
- mod 挂点（UpdateComponentBody、OnLightningStrike、GenerateChunkLightSources 等）在各页"原版范例/快查路由"中有引擎侧位置；实际用法案例不在本库收录范围。
