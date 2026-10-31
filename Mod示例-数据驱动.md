# Mod 示例 · 数据驱动（零代码）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 端到端示例；全部引擎事实有源码行号背书（行号 2026-11-01 实读复核）

## 目标

不写一行 C#：泥土挖掘掉落 1→3、挖冰改为掉冰本体、新增"2 泥土竖排→4 木棍"配方。zip 包丢进 `Mods/` 即可跑。

## 前置知识

- [12-ModAPI与加载链](01-引擎/12-ModAPI与加载链.md)：装载 20 步、modinfo 13 键陷阱、包结构红线
- [04-方块系统](01-引擎/04-方块系统.md)"csv 数据覆盖"节：解析规则逐条（本文不重复）
- [Mod开发配方](Mod开发配方.md)"数据资产"节：原版数据文件底本位置

## 原理 30 秒

- 模组 `.csv` 与原版 `BlocksData.txt` 共用同一解析器 `BlocksManager.LoadBlocksData`（E:\SurvivalcraftAPIProject\Survivalcraft\Managers\BlocksManager.cs:1037-1094）：**第 1 行是本文件自己的表头**；逐行按"第 1 列类名"找到已注册的 Block 实例，回写 public 非静态实例字段；空单元格=不改该字段（:1073）。
- 模组 `.cr` 经 `ModsManager.CombineCrLogic`（E:\SurvivalcraftAPIProject\Survivalcraft\ModsManager\ModsManager.cs:974-996）：`<Recipe>` 无指令前缀属性 = **追加新配方**（:988-990）；`new-Xxx`/`r-Xxx` 前缀才改/删同款（:977-987）。
- 时序：csv 在全部方块注册后的 `PostProcessBlocksLoad` 逐模组加载（BlocksManager.cs:407-411），`.cr` 在 `CombineDataBase` 阶段合并（ModEntity.cs:365-378）——所以 csv 能改原版方块、也能改自己 mod 的方块。

## 制品

### 目录树（.scmod = zip 容器，条目名一律 UTF-8）

```
example-databasics.scmod
├── modinfo.json          ← 必需，zip 根
├── basics.csv            ← csv/cr 放包内任意路径（ModEntity.GetFiles 按扩展名全包收集 :98-121）
└── basics.cr
```

### modinfo.json（完整）

```json
{
    "Name": "数据示例：泥土改产量",
    "Version": "1.0.0",
    "ApiVersion": "1.8",
    "Author": "SC笔记示例",
    "Description": "覆盖泥土掉落数量与冰掉落物，新增一条合成配方。零代码。",
    "PackageName": "example-databasics",
    "LoadOrder": 10000,
    "GameplayImpactLevel": "Break"
}
```

- `LoadOrder` 必须是 JSON 数字（写成 `"10000"` 静默退 0）；`GameplayImpactLevel` 大小写敏感、取"产量倍增"含义故填 Break（枚举注释 E:\SurvivalcraftAPIProject\Survivalcraft\Game\GameplayImpactLevel.cs:29-32）。解析逐键规则见 12 页 modinfo 表（`ModsManager.DeserializeJson` ModsManager.cs:219-354）。
- 故意省略 `NonPersistentMod`：默认 false = 常规模组（会记入存档 UsedMods）；要临时试效果才写**字面量** `true`。

### basics.csv（完整，2 行改动 + 1 行可选演示）

底本：原版 `E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\BlocksData.txt` 第 1 行表头 + 第 6 行 DirtBlock（DefaultDropCount=1，DefaultDropContent=`#`=自引用掉落）。模组 csv 不必抄全 79 列——只写要改的列即可（解析器读本文件自己的表头，:1040/:1073）：

```
Class Name;DefaultDropCount;DefaultDropContent
DirtBlock;3;
IceBlock;;#
```

- 第 2 行：泥土掉落 1→3（留空 DefaultDropContent=沿用原版 `#`）。
- 第 3 行：冰掉落改为掉自己（`#`=本方块 BlockIndex，语法 :1078-1085；`#WaterBlock` 形式可引用别的方块）。
- csv 唯一能表达的"换装"是改显示名等字段值：把上表表头第三列换成 `DefaultDisplayName`，行写 `DirtBlock;3;沃土`。**csv 无法新增方块、无法做染色变体**：第 1 列只按类名匹配已注册实例（:1056），染色在 data 位不是 csv 字段——换色变体请走 [04-方块系统](01-引擎/04-方块系统.md) 的 PaintedCubeBlock/data 编码，此处按"宁缺毋错"放弃。

### basics.cr（完整）

底本：原版 `E:\SurvivalcraftAPIProject\Survivalcraft\Content\Assets\CraftingRecipes.xml:69-73` 的木棍配方（`"a"`×2 竖排，a=planks），仅把配料换成泥土的 CraftingId（DirtBlock 行 CraftingId=`dirt`）：

```xml
<Recipes>
    <Recipe Result="StickBlock" ResultCount="4" RequiredHeatLevel="0" a="dirt" Description="[0]">
      "a"
      "a"
    </Recipe>
</Recipes>
```

- 根元素 `<Recipes>`（无前缀 `<Recipe>`=追加，:988-990）；属性形态与原版条目一字不差。Remains 返桶写法见原版 :48（`Remains="EmptyBucketBlock" RemainsCount="1"`）。
- 只要求 XML 良构，不做 XSD 校验（`XmlUtils.LoadXmlFromStream(stream, UTF8, throwOnError)` 的第三参只管良构，EntitySystem\XmlUtilities\XmlUtils.cs:72-76）。

## 打包清单（每条都有出处）

1. zip 根必须有 `modinfo.json`；`Assets/**` 前缀拼写一字不差（本示例没有内容资源，不需要 Assets/）。
2. 扩展名**全小写**：`.csv`/`.cr`/`.scmod`——扩展名比较大小写敏感，`.CSV` 静默跳过（12 页包结构节）。
3. 不留 0 字节条目（当不存在）；条目不重名（重名整包失败）；压缩只认 Deflate/Store（任意 zip 工具默认即可）。
4. 所有文本文件 UTF-8。发布包用 `-c Release` 之类仅是习惯；本包无代码。
5. 双击导入若同名文件已存在会抛 `FileAlreadyExistsException` 不覆盖（ModsManager.cs:446-466）——换名或先删旧包。

## 验证（日志锚点 + 游戏内）

日志依次应出现（搜 `数据示例`）：

| 锚点 | 出处 |
|---|---|
| `[数据示例：泥土改产量](Version: 1.0.0) Loaded 3 resource files.` | ModEntity.cs:275（N=条目数：modinfo+csv+cr） |
| `[数据示例：泥土改产量] Loading .csv blocksdata files.`（中文客户端："加载 .csv 方块数据文件"） | ModEntity.cs:309 + Lang en-US/zh-CN `ModEntity:1` |
| `[数据示例：泥土改产量] Loading .cr crafting recipaedia files.`（zh："加载 .cr 合成配方文件"） | ModEntity.cs + Lang `ModEntity:4` |

失败锚点：`Get file [basics.csv] failed:`（ModEntity.cs:114）=列数不齐/陌生列名抛异常；只一条 `Log.Warning`（BlocksManager.cs:1058）=类名拼错、整行跳过。游戏内：挖泥土出 3 个；冰掉冰本体；2×1 竖排泥土合成 4 木棍（RequiredHeatLevel=0 无需加热）。

## 该示例踩的坑

- **csv 里写 `New-`/`Remove` 列**：被当陌生字段抛异常，整份 csv 失效——csv 没有指令层（:1074-1075，另见 04 页坑表）。
- **某行字段数 ≠ 表头列数**：抛异常，该行之后全丢、之前已应用的行保留（:1047-1050）。
- **想"新增方块/换色变体"**：csv 做不到（见上），别往 csv 里塞类名不存在的行。
- **布尔列大小写**：`true/false` 大小写不敏感（BooleanHumanReadableConverter.cs:6-7），原版表的 `TRUE/FALSE` 也能吃；枚举列大小写敏感（04 页）。
- **改了不生效**：先看三个锚点缺哪个；`Loaded 0/1 resource files` 基本都是 0 字节条目或后缀大写。
- **同包名互相禁用**：复制本包改名试验时，`PackageName` 也要改，否则互标 Duplicated（ModEntity.cs:257-268）。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查 csv 某列能不能写 | 该列名=Block 子类 public 非静态实例字段（BlocksManager.cs:1063-1067）；全集见 Block.cs:8-181 |
| 改原版配方/删配方 | `.cr` 的 `new-`/`r-` 前缀 DSL（ModsManager.cs:977-987；12 页数据合并协议） |
| 改生物数值/加变体 | `.xdb`（ModsManager.cs:1083-1152）+ 配方页"数据资产"节 |
| 模组设置页面 | 12 页"数据驱动设置层"；代码示例见本库《Mod示例-电力元件》 |
| 验证包结构对不对 | 12 页".scmod 包结构"要点清单 |
