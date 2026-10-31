# Game/Community 明细（72 文件）

> 域: SC引擎 · 更新: 2026-10-31 · 状态: 全列(72/72，头部注释级)；主页面另见 16-玩法物品与背包.md，根目录 226 文件另见 16a-Game明细.md。
>
> 前缀：`E:\SurvivalcraftAPIProject\Survivalcraft\Game\Community\`（下表省略）。分层：Domain(纯规则/状态机，26) → Infrastructure(Http/持久化/导入，35) → Models(协议与落盘模型，11)。职责多取自源文件头注释原文压缩。

## Domain\Common（2）

| 文件 | 行 | 职责 |
|---|---|---|
| `ExternalVersionParser.cs` | 29 | 外部版本文本规范化并解析为 NuGetVersion |
| `WeakEventSource.cs` | 95 | 弱引用事件源：防静态单例事件把换语言重建前的旧屏幕实例钉死不释放 |

## Domain\Community（7，社区帖子/文件规则）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityDownloadFeedbackInfo.cs` | 9 | 下载反馈信息 |
| `CommunityFileRules.cs` | 33 | 服务端 filename 落盘前解码+净化；非法转义回退 id 命名 |
| `CommunityFilters.cs` | 121 | 服务器文件类型协议枚举 CommunityFileType（值=API 协议）+ 过滤器 |
| `CommunityLocalModMatchingRules.cs` | 57 | 社区可控文件名匹配前归一化（去转义/统一分隔符/取末段），存在性短路判定 |
| `CommunityModVersionSelector.cs` | 70 | 社区 mod 多版本时选版规则 |
| `ModpackManifestParser.cs` | 376 | 解析整合包清单：ZIP 内嵌条目大小上限、累计解压内存预算、嵌入图标探测序 |
| `PostIconRules.cs` | 45 | 帖子图标规则 |

## Domain\LocalResources（10，本地已装 mod 规则）

| 文件 | 行 | 职责 |
|---|---|---|
| `LocalModCollectionRules.cs` | 20 | 本地 mod 集合规则 |
| `ModCompatibility.cs` | 316 | mod 兼容判定：归一化文本复用 + pattern 编译正则缓存（上限 15） |
| `ModDependencyAvailabilityRules.cs` | 69 | 依赖满足判定：已装但禁用≠缺失（引导启用）；无解析产物判不满足 |
| `ModDependencyInfo.cs` | 25 | 依赖声明：规范化文本/引擎解析产物/下载页链接三要素 |
| `ModUpdateSelector.cs` | 120 | mod 更新选择：InvariantCulture+UTC 统一比较时间戳 |
| `ModpackActivationRules.cs` | 47 | 整合包启用规则 |
| `ModpackModMatcher.cs` | 92 | 整合包条目↔本地 mod 匹配（BCL 去扩展名语义；非法名回退空键） |
| `ModpackPresenceRules.cs` | 127 | 整合包子项"已装"判定规则（输入清单+记录+快照，输出判定不产 UI 文案） |
| `ModpackPresenceSnapshot.cs` | 15 | 在场判定用的本机资源快照（纯数据） |
| `ModpackRules.cs` | 227 | 整合包总规则：URL 取 AbsolutePath 后统一解码一次（防 %2520 二次解码） |

## Domain\Transfers（7，下载/上传传输域）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityDownloadQueueItem.cs` | 30 | 下载队列项；Imported 标志：进程死前已导入的项恢复时改判 Completed |
| `CommunityDownloadQueueStateMachine.cs` | 85 | 下载队列纯状态转换规则（UI/网络/文件操作禁入） |
| `CommunityDownloadSourceModels.cs` | 23 | 下载源模型；三值源选择枚举收编为布尔设置 |
| `CommunityDownloadSourceResolver.cs` | 41 | 下载源解析：Host 空=默认线路；用户输入畸形时按 null 不裸抛 |
| `CommunityTransferProgress.cs` | 21 | 传输进度 |
| `CommunityUploadFileNaming.cs` | 27 | 上传文件命名（空输入历史默认值带扩展名兼容） |
| `CommunityUploadModels.cs` | 31 | 上传模型 + CommunityWorldUploadResult |

## Infrastructure 根（2）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityDownloadCacheFile.cs` | 60 | 下载缓存文件 |
| `TaskSlot.cs` | 122 | 单槽后台任务生命周期：requestId 防陈旧+失察任务观察，须 UI 线程调用 |

## Infrastructure\Http（14，网络客户端）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityApiClient.cs` | 111 | 社区 API 总客户端：空/非 JSON body 归一化 InvalidOperationException |
| `CommunityAuthClient.cs` | 84 | 登录：区分网络故障与响应码异常；用户取消传播不吞 |
| `CommunityDownloadFeedbackClient.cs` | 118 | 下载反馈上报：持久化剥离 Token，上报时按登录态补取，未登录匿名尽力而为 |
| `CommunityDownloadGuard.cs` | 22 | 下载防护：响应体大小上限（防第三方 URL 内存耗尽） |
| `CommunityHttpDownloader.cs` | 355 | 统一下载器：服务器 stall 空闲超时（linked CTS），保持 is-a OperationCanceledException |
| `CommunityModCatalogClient.cs` | 20 | mod 目录客户端 |
| `CommunityPlayedTimeClient.cs` | 85 | 游玩时间上报：非关键路径，失败只记日志不抛 |
| `CommunityTranslateClient.cs` | 66 | /translate 封装：整篇投递、服务端 AI 保结构翻译+缓存 |
| `CommunityUnauthorizedNotifier.cs` | 32 | 401/403 广播：token 失效统一清登录态，调用点无需逐个处理 |
| `CommunityUploadClient.cs` | 258 | 发布上传链：取又拍云直传凭证→表单直传（仅 https+*.upyun.com）→登记 |
| `HttpClientProvider.cs` | 28 | 共享 HttpClient 集中创建（社区与远程导入超时策略并存） |
| `IModpackSourceResolver.cs` | 10 | 整合包源解析接口 |
| `ModpackSourceResolver.cs` | 160 | 整合包源解析：取消传播不触发 fileId 兜底；改流式读防慢网超时 |
| `PostIconDecoder.cs` | 23 | 帖子图标解码：Resize 异常时释放已分配位图防泄漏 |

## Infrastructure\Integration（7，下载→本地导入）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityUploadFileProvider.cs` | 177 | 上传文件提供：导出失败清理临时文件再抛；未加载 mod 回退记录路径 |
| `ICommunityUploadFileProvider.cs` | 7 | 上传文件提供接口 |
| `IModpackItemImporter.cs` | 10 | 整合包数据导入接口：false=无处导入，调用方必须计失败 |
| `ModDependencyParser.cs` | 23 | 依赖声明解析：DependencyRanges 引擎解析保证非 null，富信息走旁路字典 |
| `ModpackItemImporter.cs` | 72 | 单项导入：模组元数据校验+游戏内容写入集中于此 |
| `PendingLocalModActions.cs` | 206 | "重启后执行"的本地 mod 动作清单（local-mod-pending-actions.json） |
| `PendingLocalModCompatibilityOverrideCache.cs` | 56 | 兼容性覆盖缓存：插入序伪 LRU 淘汰（防已卸载包名无限累积） |

## Infrastructure\Modpacks（2）

| 文件 | 行 | 职责 |
|---|---|---|
| `ModpackDataFiles.cs` | 306 | 整合包数据文件落地：mod 用事务替换（Delete+Move），本体用 MoveFileSafely（备份/回滚） |
| `ModpackPresenceManager.cs` | 83 | 在场快照捕获与失效（导入/扫描触发） |

## Infrastructure\Persistence（10，落盘）

| 文件 | 行 | 职责 |
|---|---|---|
| `CommunityCredentialStore.cs` | 429 | 凭据加密存储 v4：每服一文件，魔数 SCBPAUTH4，含旧格式迁移 |
| `CommunityDownloadQueuePersistence.cs` | 147 | 下载队列持久化：按名恢复下载源；已导入项恢复改判 Completed |
| `CommunityDownloadQueueStore.cs` | 20 | 队列存取：枚举字符串序列化，兼容旧数字格式 |
| `CommunityPlayedTimeStore.cs` | 47 | 游玩时间本地存 |
| `CommunityStoragePaths.cs` | 20 | 社区本地存储路径集中维护 |
| `JsonFileStore.cs` | 164 | 统一 JSON 读写：先写临时文件再替换目标 |
| `LocalModReviewStore.cs` | 30 | 本地 mod 评价存 |
| `ModpackActivationState.cs` | 124 | 整合包启用态：静态直供；探测式读取，单条失败跳过 |
| `ModpackRegistry.cs` | 581 | 整合包磁盘协议与解析缓存的所有者 |
| `ModpackStateStore.cs` | 21 | 整合包状态存取 |

## Models\Api（7，线协议）

| 文件 | 行 | 职责 |
|---|---|---|
| `ApiEnvelope.cs` | 12 | {code,data,msg} 标准信封，各响应空壳继承 |
| `AuthModels.cs` | 37 | v4 凭据 payload：登录数据+归属服务器（自描述） |
| `CommunityModels.cs` | 109 | 社区通用响应模型 + BasicApiResponse |
| `FilePublishedModels.cs` | 23 | 发布成功响应（复用 PostModels 子集，缺省 null） |
| `PlayedTimeModels.cs` | 33 | 游玩时间上报 wire 模型（camelCase 契约键） |
| `PostModels.cs` | 215 | 帖子模型：服务端计数字段类型不稳，FlexibleString/FlexibleInt 归一化 |
| `UploadModels.cs` | 45 | 上传模型 + 又拍云凭证请求 |

## Models\Persistence（4，落盘模型）

| 文件 | 行 | 职责 |
|---|---|---|
| `DownloadQueueModels.cs` | 32 | 队列持久化状态：源按名解析，Imported 改判 Completed |
| `LocalModModels.cs` | 32 | 本地 mod 评价数据 |
| `LocalResourceModels.cs` | 36 | 本地资源子系统核心数据模型 |
| `ModpackModels.cs` | 114 | ModpackManifest 清单模型：展示性可选字段旧清单显示"无"；同名跳过=不算成功不算失败 |
