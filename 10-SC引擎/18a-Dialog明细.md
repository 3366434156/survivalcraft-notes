# Dialog 明细（57 文件全量一行表）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全读(57/57 全文深读)
>
> 父页: 18-Dialog对话框族.md。每行 = 一个 .cs 文件。格式：文件 | 继承 | 职责/关键成员+行号 | 坑/备注。
> 路径前缀统一为 `E:\SurvivalcraftAPIProject\Survivalcraft\Dialog\`（Community/ 子目录单独标注）；行号以 2026-10-31 源码为准。

## 一、根目录 · 基元与通用框（26）

| 文件 | 继承 | 职责/关键成员 | 坑/备注 |
|---|---|---|---|
| Dialog.cs | CanvasWidget | 全族基类：ctor `IsHitTestVisible=true`+`Size=∞`(`:4-9`) | 实际尺寸在 XML 根 |
| SureDialog.cs | Dialog | 4 行空壳，XML 占位用 | — |
| MessageDialogButton.cs | enum | Button1=0 / Button2=1 | — |
| MessageDialog.cs | Dialog | 两按钮消息框：ctor(`:18-47`) 4 文本+size 参数(≥0 才覆盖)；Update 查 Ok/Cancel/IsClicked(`:52-68`)；Dismiss 三件套(`:70-75`)；至少一按钮否则抛(`:42-45`) | AutoHide 默认 true |
| ListSelectionDialog.cs | Dialog | 通用列表框：ctor 填 ListPanel(`:23-57`，条目多时收缩 Content 高度)；选中后延迟 50ms 关(`:82-88`)；`m_isDismissed` 防重复(`:92-101`) | result==null 不回调 |
| TextBoxDialog.cs | Dialog | 文本输入框：`HasFocus=true`+Enter 提交(`:31-32`)；第二 ctor 带 TextChanged handler2(`:36-55`) | 取消也回调 null |
| BusyDialog.cs | Dialog | 忙碌框：Large/SmallMessage 属性；Update `Input.Clear()` 吞 Back(`:34-38`) | 强制等待，Back 无效 |
| CancellableBusyDialog.cs | Dialog | 可取消进度：自建 `CancellableProgress`(`:46`)；百分比刷 SmallMessage(`:70-72`)；可选"隐藏"按钮 ctor2(`:52-67`) | autoHideOnCancel 参数 |
| SpawnDialog.cs | Dialog | 出生/季节进度：ValueBar + 季节名上色(`:13-19`) | 只读展示，无输入 |
| GameMenuDialog.cs | Dialog | 暂停菜单+全量统计(542 行)：ctor 动态 AddStat(`:516-541`)；性能建议弹窗(`:26-45`)；More 菜单 Tuple 列表(`:379-483`)；Quit 存档退主菜单(`:489-494`) | 静态弹窗标志只弹一次 |
| BuildFurnitureDialog.cs | Dialog | 家具编辑(352 行)：三角形计数与 MaxTriangles 校验(`:75-92`)；2D/3D 双预览(FurnitureDesignWidget)；Shift/Mirror/Rotate/分辨率增减(`:225-314`)；命名走 TextBoxDialog+ListSelectionDialog(`:118-224`)；DirectionAxisToDelta 轴映射(`:316-346`) | 构建结果经 handler(bool) 回调 |
| BulletinDialog.cs | Dialog | 公告框：滚动 ≥80% 才显示 OK(`:58-63`)；m_scrollPanel.m_scrollAreaLength 直访私有字段 | Edit/Update 按钮已注释死码 |
| LevelFactorDialog.cs | Dialog | 等级系数展示：±/× 前缀+∞ 特判(`:29-44`) | 只读 |
| KeyboardHelpDialog.cs | Dialog | 键盘帮助：H 键关(`:21`)；Help 按钮不在 HelpScreen 时才显示(`:18`) | — |
| GamepadHelpDialog.cs | Dialog | 手柄帮助：Start 键关(`:21`) | 同上 |
| SelectGameModeDialog.cs | ListSelectionDialog | 游戏模式选择：条目 XML 工厂(`:10-17`)；ContentSize 750×420(`:20`)；GetAllowedGameModes 按参数裁 Adventure/Cruel(`:22-33`) | — |
| SelectExternalContentProviderDialog.cs | ListSelectionDialog | 外部内容提供者选择：条目 XML 工厂(`:11-18`)；ContentSize 宽 700(`:20`) | — |
| SelectExternalContentTypeDialog.cs | ListSelectionDialog | 内容类型选择：枚举过滤可下载项(`:7-9`)；图标+文本条目(`:14-16`) | — |
| SelectClassSubstituteDialog.cs | Dialog | 类替换选择(模组冲突)：ItemWidgetFactory/ItemClicked 就地赋值(`:19-48`)；描述支持 [库:键] 本地化(`:51-58`) | survivalcraft 包名显示"原版" |
| SelectCommunityServerDialog.cs | Dialog | 社区服务器列表：`m_selectOnly` 双模式(仅选 vs 导航，`:13-18`)；仅选模式只列中文栈(`:70-81`)；Add/Remove/Edit 供编辑框回调(`:83-123`) | 模式混用会造不可见条目 |
| RunJsDialog.cs | Dialog | JS 控制台：`JsInterface.Evaluate`(`:59`)；Enter 运行/Esc 关(`:27-28`)；耗时显示(`:62-63`) | Dismiss(true) 不关框只执行 |
| RemoteControlDialog.cs | Dialog | 远程控制(HTTP 监听开关/端口/密码，`:30-78`)；IOS/BROWSER 编译为空壳(`:85-91`) | — |
| ViewGameLogDialog.cs | Dialog | 日志查看：GameLogSink.GetRecentLogLines 上限 1000 行(`:165-169`)；三级过滤循环(`:63-67`)；行颜色按 ERROR/WARNING/INFO(`:138-148`) + ModifyLogColor 钩子(`:149-155`) | 上传按钮整段注释死码(`:87-133`) |
| DownloadContentFromLinkDialog.cs | Dialog | 链接下载输入：sealed；点外关+确认回调 URL(`:26-43`) | — |
| ExternalContentLinkDialog.cs | Dialog | 链接展示：ctor 直接写剪贴板(`:10`) | — |
| EditWorldSeedDialog.cs | Dialog | 世界种子编辑：字符串种子↔真种子双框联动(`:41-58`)；`SeedToTrueSeed` Σ(c×(1+29n))(`:94-102`) | 直接改真种子后字符串框清空 |

## 二、根目录 · 电元件与调色编辑器（9）

| 文件 | 继承 | 职责/关键成员 | 坑/备注 |
|---|---|---|---|
| EditSignDialog.cs | Dialog | 告示牌：4 行文本+8 色循环(`:44-53,125-136`)+URL 页切换(`:114-121`)；URL 非空时禁用颜色(`:146-155`)；告示牌被移动即自动关(`:141-143`) | — |
| EditMemoryBankDialog.cs | Dialog | 存储器：线性/Grid 双视图(`:81-94`)；`m_ignoreTextChanges` 防回写循环(`:49-80`)；临时副本 OK 才提交(`:95-97`) | — |
| EditMemoryBankDialogAPI.cs | Dialog | 存储器 API 版(392 行，全代码构建)：17×17 ClickTextWidget 网格(`:107-155`)；hex 字符串 Load/Save(`:67-105`)；脏标记 isclick 重绘(`:369-391`)；转置+清零+设定位置模式 | 供模组 API 弹出，不依赖 XML |
| EditTruthTableDialog.cs | Dialog | 真值表：16 Checkbox↔byte 0/15(`:59-64`)；线性字符串同步带 Data 快照比较防抖(`:48-58`) | — |
| EditVoltageLevelDialog.cs | Dialog | 电压选择：Slider 0-15，显示 V 数与充/放电标签(`:40-44`) | — |
| EditPistonDialog.cs | Dialog | 活塞：3 Slider(伸长/拉回/速度)↔data 位域(`:33-62`，PistonBlock.Get/Set)；Pushing 模式藏第二组(`:47`) | 方块 id 237 硬编码(`:37`) |
| EditAdjustableDelayGateDialog.cs | Dialog | 可调延迟门：Slider+±1 按钮(`:30-48`)；延迟→秒换算 0.01×(n+1)(`:54`) | — |
| EditColorDialog.cs | Dialog | RGB 调色(全代码构建，201 行)：3 Slider+色块按钮；点色块弹 TextBoxDialog 输入 #RRGGBB(`:139-166`)；HumanReadableConverter 解析(`:149`) | 嵌套框 parent=this 先例 |
| EditPaletteDialog.cs | Dialog | 世界调色板 16 色：行代码构建(`:23-61`)；名字校验 VerifyColorName；重置到默认(`:112-115`) | — |

## 三、根目录 · 模组/社区管理（8）

| 文件 | 继承 | 职责/关键成员 | 坑/备注 |
|---|---|---|---|
| LoginDialog.cs | Dialog | 旧登录框(尸体类，仅 SchubExternalContentProvider 用，`:4`)；全代码构建账号/密码框 | 新登录走 CommunityLoginDialog |
| MoreCommunityLinkDialog.cs | Dialog | 社区入口：用户/UniqueId 展示+复制；切换用户(ListSelectionDialog)、发布链接(`:30-66`) | 文本超 15 字省略 |
| PublishCommunityLinkDialog.cs | Dialog | 发布链接：链接→自动填名(GetFilenameFromLink `:92-109`)；类型选择；发布配 CancellableBusyDialog(`:62-88`) | — |
| RateCommunityContentDialog.cs | Dialog | 评分：StarRating>0 才可提交(`:37`)；跳转举报框(`:51-55`) | — |
| ReportCommunityContentDialog.cs | Dialog | 举报：8 原因 Checkbox 随机洗牌+Other 恒底(`:36-41`)；恰好勾 1 项才可提交(`:47`) | — |
| ModDetailsDialog.cs | Dialog | 模组详情(335 行)：动态字段行(`:66-144`)；依赖逐条标注+查找/查看下钻(`:133-144,290-305`)；删除按引用移除(`:237-259,328-334`)；社区按钮按黑名单/待重启禁用(`:207-217`) | ModEntity Equals 按值，必须 ReferenceEquals 移除 |
| ModpackDetailsDialog.cs | Dialog | 整合包详情(205 行，internal ctor)：字段行+子项清单文本(`:180-199`)；下载状态行三色分级(`:167-177`)；busy/loading 边沿轮询恢复按钮(`:118-127`) | 宿主屏 internal，构造器收窄 |
| EditCommunityServerInfoDialog.cs | Dialog | 服务器编辑：内置条目只读可克隆(`:29-38`)；仅选择模式锁中文类型(`:66-69`)；有改动禁删除(`:97`) | 新增/编辑统一回写字段(`:100-105`) |

## 四、Community 子目录（14）

| 文件 | 继承 | 职责/关键成员 | 坑/备注 |
|---|---|---|---|
| Community/CommunityDownloadDialog.cs | Dialog | 下载进度(ValueBar)：SetProgress/SetCompleted/SetFailed/SetStopped(`:37-63`)；终态 m_closable 才可关(`:74-77`)；取消/后台按钮按回调有无显隐(`:80-87`) | 终态后忽略迟到进度(`:39`) |
| Community/CommunityDownloadFailureDialog.cs | Dialog | 下载失败：错误文本+复制链接+换源(`:40-61`)；换源复用 DFM 的源选择框 | 换源时本框保持打开 |
| Community/CommunityDownloadQueueDialog.cs | Dialog | 下载队列(269 行)：`IDownloadQueueDialogHost` 宿主抽象(`:9-19`)；条目能力位 CanXxx 决定按钮(`:43-49,207-235`)；每帧 Refresh 轮询(`:72-89`)；SelectedIndex 每帧 Sync 对抗强制重选(`:91-96`)；缓存稳定行 ReferenceEquals 快跳(`:178-193`) | 条目实例每帧新建，按 Id 对齐 |
| Community/CommunityFiltersDialog.cs | Dialog | 社区筛选(212 行)：struct State 8 字段(`:5-14`)；4 下拉全走 ListSelectionDialog；`HasLiveListSelectionDialog` 防同帧连关(`:64-72,156-185`)；保存默认按钮 | 存活判据须父链可达 Root |
| Community/CommunityImportOverwriteDialog.cs | Dialog | 导入重名三选：Overwrite/Rename/Cancel(`:4-50`)；canRename=false 时模组只留覆盖/取消(`:12-28`) | MessageDialog 两按钮不够用时的自建样板 |
| Community/CommunityLoginDialog.cs | Dialog | 社区登录(新版)：账号/密码+错误行；SetBusy 锁按钮(`:30-35`)；busy 期间全局输入全忽略(`:41-56`) | — |
| Community/CommunityMissingDependenciesDialog.cs | Dialog | 缺失依赖下载(360 行)：文件分组 BuildFileGroups(`:158-180`)；组内按首选版本匹配度排序(`:218-237`)；精确范围加权(`:300-323`)；全部下载=每组首选文件(`:289-298`) | 无下载行的包名段落后置显示(`:102-116`) |
| Community/CommunityModReviewDialog.cs | Dialog | 模组评分+评语：0 星禁提交(含 Input.Ok，`:66-70`)；恢复上次内容 Link(`:46-56`) | — |
| Community/CommunityModVersionsDialog.cs | Dialog | 版本列表(177 行)：版本行+文件展开集合 m_expandedVersionKeys(`:86-95`)；当前版本高亮金色(`:148-149`)；兼容性文案由 CommunityVersionCompatibilityFormatter 算(`:111-117`) | 展开状态重建整表 |
| Community/CommunityModpackFileConflictDialog.cs | Dialog | 整合包文件冲突五选：Overwrite/Skip/SkipAll/OverwriteAll/Close(`:5-62`) | — |
| Community/CommunityPostDetailsDialog.cs | Dialog | 帖子详情(316 行)：HtmlWidget 正文+链接分流(#锚点滚转，外链浏览器，`:61-67`)；纯文本降级(`:239-266`)；自动翻译 Task+RequestId 防串(`:140-226`)；UpdateCeases 取消在途翻译(`:105-110`) | 重建只截 Html 后子件，不摘部件防纹理早释放(`:112-119`) |
| Community/EditDownloadSourceInfoDialog.cs | Dialog | 下载源编辑：空名/重名拒绝(`:63-78`)；主机留空=默认线路(`:6`) | 名称是身份键 |
| Community/RestartConfirmDialog.cs | Dialog | 重启确认：回调返回 true 才 `Window.Restart()`/软重启(`:61-74`)；静态便捷法 ShowModImportRestartConfirm(`:35-51`) | 回调先兑现挂起动作再重启 |
| Community/SelectDownloadSourceDialog.cs | Dialog | 下载源列表：● 标默认(`:23-28`)；点已选中项即设默认(`:30-35`) | 镜像 SelectCommunityServerDialog |

## 五、XML 模板（Content\Assets\Dialogs\，48 个）

与 .cs 一一对应（SureDialog/MessageDialogButton/LoginDialog/ModpackDetailsDialog 除外或新增）；根节点一律 `CanvasWidget` 定 `Size` + `ClampToBounds="true"`，底板 `<BevelledRectangleWidget Style="{Styles/DialogArea}" />`（MessageDialog.xml:1-3 为样板）。个别对话框无 XML（EditColorDialog、EditMemoryBankDialogAPI、LoginDialog 全代码）。
