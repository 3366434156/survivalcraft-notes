# Mod 示例 · 自定义特效（粒子+音效）

> 域: SC引擎 · 更新: 2026-11-01 · 状态: 端到端示例；挖掘任意方块时炸开一圈粒子环+播放音效；行号 2026-11-01 实读

## 目标

自定义一个一次性粒子系统（扩散环），挂 `OnBlockDug` 钩子在**挖掉任意方块**的位置播放，同时走 `SubsystemAudio` 位置系播一个原版音效。复用原版粒子图集，零美术资产。

## 前置知识

- [07-粒子系统](01-引擎/07-粒子系统.md)：ParticleSystem 基类与生命周期三形态
- [08-音频系统](01-引擎/08-音频系统.md)：3D 位置音效与 minDistance 语义
- [24-机制全链](01-引擎/24-机制全链.md)链 1：挖掘链上本示例的挂点位置（第 5 步）
- [12-ModAPI与加载链](01-引擎/12-ModAPI与加载链.md)：钩子注册窗口

## 原理 30 秒

1. **粒子系统的契约**（Game/ParticleSystem.cs:5，`ParticleSystem<T> : ParticleSystemBase`）：构造时 `base(数量)` 预分配粒子数组；**`Simulate(dt)` 每帧被调，返回 `true` 即"系统结束"被自动移除**（SubsystemParticles.cs:95-105；Simulate 抛异常=记日志+移除，不崩局 :100-104）；`Draw` 基类全包——按 `Texture`/`TextureSlotsCount` 自动建批次、按粒子 `BillboardingMode` 做公告板（ParticleSystem.cs:47-162），容量上界 `MaxQuadDemand` 自动=粒子数（:45），不用重写。
2. **粒子本体**（Game/Particle.cs:4-27）：只有 12 个字段——`IsActive/Position/Size/Color/TextureSlot/BillboardingMode/UseAdditiveBlending` 等；自定义字段（寿命/速度）靠**继承 `Game.Particle` 加字段**（原版范式 FireParticleSystem.cs:5-12）。
3. **发射**：`Project.FindSubsystem<SubsystemParticles>().AddParticleSystem(系统实例)`（SubsystemParticles.cs:35）。粒子贴图用 `ContentManager.Get<Texture2D>("Textures/FireParticle")` + `TextureSlotsCount=3`（原版火焰同款，FireParticleSystem.cs:34-35）。
4. **挂点**：`OnBlockDug` 钩子在挖掘完成帧派发（ComponentMiner.cs:286-294），参数里有落点 `digValue`；钩子方法里 `componentMiner.Project` 取世界（Component.cs:16）。
5. **位置音效**：`SubsystemAudio.PlaySound(名,音量,音调,position,minDistance,autoDelay)`（SubsystemAudio.cs:98/:103）；`minDistance`=满音量半径（配方"音频"节）。

## 制品

### 目录树（.scmod = zip 容器）

```
example-ripple.scmod
├── modinfo.json
└── ExampleRipple.dll        ← zip 根层
```

### modinfo.json（完整）

```json
{
    "Name": "示例：挖掘涟漪",
    "Version": "1.0.0",
    "ApiVersion": "1.8",
    "Author": "SC笔记示例",
    "Description": "挖掘方块时播放自定义扩散环粒子与音效。演示一次性粒子系统与位置音效。",
    "PackageName": "example-ripple",
    "LoadOrder": 10000,
    "GameplayImpactLevel": "Cosmetic"
}
```

### ExampleRipple.cs（完整，逐行注明出处）

```csharp
using Engine;                                   // Log/ContentManager/Color/Vector3
using Engine.Graphics;                          // Texture2D
using Game;                                     // ParticleSystem/Game.Particle/SubsystemParticles/ModLoader

namespace MyCompany.ExampleRipple {
    public class ExampleRippleLoader : ModLoader {
        int m_digCount;                         // 演示期日志限流：只报前 3 次

        public override void __ModInitialize() {
            ModsManager.RegisterHook("OnBlockDug", this);   // 派发点 ComponentMiner.cs:286-294
        }

        public override void OnBlockDug(ComponentMiner componentMiner, BlockPlacementData digValue, int cellValue,
            ref int durabilityReduction, ref bool mute, ref int playerDataDugAdd) {   // 签名照抄 ModLoader.cs:1260-1267
            Vector3 center = new(digValue.CellFace.X + 0.5f, digValue.CellFace.Y + 0.5f, digValue.CellFace.Z + 0.5f);
            SubsystemParticles particles = componentMiner.Project.FindSubsystem<SubsystemParticles>(true);   // Project 来源 Component.cs:16
            particles.AddParticleSystem(new RippleParticleSystem(center));   // 发射 SubsystemParticles.cs:35
            SubsystemAudio audio = componentMiner.Project.FindSubsystem<SubsystemAudio>(true);
            audio.PlaySound("Audio/PickableCollected", 0.7f, -0.4f, center, 2f, false);  // 重载签名 SubsystemAudio.cs:103；参数形态照抄 ComponentPickableGathererPlayer.cs:46
            if (++m_digCount <= 3) {
                Log.Information($"Ripple #{m_digCount} at {center}");   // 验证锚点，正式版删
            }
        }
    }

    // 一次性扩散环：0.5s 内 24 粒从中心向外扩并淡出，全部死后 Simulate 返回 true 自毁
    public class RippleParticleSystem : ParticleSystem<RippleParticleSystem.P> {
        public class P : Game.Particle {        // 继承加字段，范式 FireParticleSystem.cs:5-12
            public float TimeToLive;
            public Vector3 VelocityDir;         // 扩散方向（自定义字段，基类 Draw 不读它，只有 Simulate 用）
        }

        const float Duration = 0.5f;

        public RippleParticleSystem(Vector3 center) : base(24) {    // 预分配 24 粒，ParticleSystem.cs:35-40
            Texture = ContentManager.Get<Texture2D>("Textures/FireParticle");   // 原版火焰图集 FireParticleSystem.cs:34
            TextureSlotsCount = 3;              // 该图集 3×3 槽位（slot0~8），同 :35
            for (int i = 0; i < Particles.Length; i++) {
                P p = Particles[i];
                float angle = MathF.PI * 2f * i / Particles.Length;
                p.IsActive = true;
                p.Position = center + new Vector3(0.2f * MathF.Cos(angle), 0f, 0.2f * MathF.Sin(angle));   // 从 0.2 半径起爆
                p.VelocityDir = new Vector3(MathF.Cos(angle), 0.3f, MathF.Sin(angle));                     // 扩散方向（自定义字段）
                p.Size = new Vector2(0.12f);
                p.Color = new Color(255, 230, 140, 255);
                p.BillboardingMode = ParticleBillboardingMode.Horizontal;  // 水平环用水平公告板
                p.UseAdditiveBlending = true;      // 加色发光感（批次自动归 AdditiveBatch，ParticleSystem.cs:131）
                p.TextureSlot = 0;
                p.TimeToLive = Duration;
            }
        }

        public override bool Simulate(float dt) {
            bool anyAlive = false;
            foreach (P p in Particles) {
                if (!p.IsActive) continue;
                p.TimeToLive -= dt;
                if (p.TimeToLive <= 0f) {
                    p.IsActive = false;            // 基类 Draw 只画 IsActive（ParticleSystem.cs:81）
                    continue;
                }
                anyAlive = true;
                p.Position += p.VelocityDir * 2.2f * dt;              // 外扩
                p.Size = new Vector2(p.Size.X + 0.9f * dt);           // 放大
                float a = p.TimeToLive / Duration;                    // 1→0 线性淡出
                p.Color = new Color((int)(255 * a), (int)(230 * a), (int)(140 * a), 255);
            }
            return !anyAlive;                       // true=本系统结束→被自动移除，SubsystemParticles.cs:95-105
        }
    }
}
```

> 另注：`OnBlockDug` 只在玩家挖掘时派发——爆炸/活塞等途径破坏的方块不走这里（那些直接调 `DestroyCell`，见 [24-机制全链](01-引擎/24-机制全链.md)链 2 注）。

## 打包清单

1. dll 在 zip 根层；扩展名全小写；无 0 字节/重名条目（12 页包结构节）。
2. `__ModInitialize` 只做 RegisterHook；`OnBlockDug` 走钩子表**必须注册**（钩子总表例外清单里没有它）。
3. 改代码必须重启整个进程（Reboot 不卸载程序集，12 页坑表）。

## 验证（日志锚点 + 游戏内）

| 锚点 | 出处 |
|---|---|
| `[示例：挖掘涟漪](Version: 1.0.0) Loaded 2 resource files.` | ModEntity.cs:275 |
| `[示例：挖掘涟漪] Handling assembly [ExampleRipple, …]` | LoadingScreen.cs:281 |
| `Ripple #1 at <x,y,z>`（挖第一块时） | 本示例 m_digCount |

游戏内：生存/创造模式挖任意方块——方块碎屑之外多一圈黄色扩散环（0.5s）+ "叮"拾取音效。失败对照：有碎屑没环 = 钩子没触发（查是否 RegisterHook/名字拼错）；环卡住不消失 = `Simulate` 忘了返回 `!anyAlive`（系统永不自毁）；声音随距离不衰减 = `minDistance` 传太大（满音量半径语义，配方"音频"节）。

## 该示例踩的坑

- **Simulate 里抛异常**：引擎只 `Log.Error` 后把整个系统移除（SubsystemParticles.cs:100-104）——特效"闪一下就没了"多半是这里，去日志搜 `Particle`。
- **粒子不动/全挤在一点**：忘记每帧改 `Position`（基类不替你做物理，FireParticleSystem 也是自己在 Simulate 里 `Position.Y += Speed*dt`，:50）；或 `BillboardingMode` 选了 `None` 又没设 Right/Up 向量（四顶点全零=不可见）。
- **淡出用 Color.A==0 但没效果**：加色混合批次看的是 RGB 亮度（BlendState.Additive，ParticleSystem.cs:56），要同时缩 RGB——本示例按 alpha 缩 RGB 的写法照抄即可。
- **在钩子里每帧发射**：`OnBlockDug` 只在"挖掉那一帧"发一次，天然限频；若换成 `TerrainChangeCell` 这类高频钩子，务必自己节流（参照配方"音频"节防音效风暴的每帧上限思路）。
- **Texture 忘设 TextureSlotsCount**：UV 计算除 0（ParticleSystem.cs:78 `1f/TextureSlotsCount`）→ NaN 全屏白块。Texture 换新图时两个都要设（setter 只清批次缓存 :22-31）。
- **想常驻循环特效**（火把光环这类）：返回恒 false 会常驻占批次——学原版"可见门控"：不在玩家视野/距离外时跳过生成（FireParticleSystem.cs:41 `m_visible || m_age<2f` 门控，:72 帧尾清标志），必要时 `RemoveParticleSystem` 手动移除（SubsystemParticles.cs:48-51）。

## 快查路由

| 我想… | 去/看 |
|---|---|
| 查粒子挂到方块破坏之外的事件 | [Mod钩子总表](Mod钩子总表.md)（OnBlockDug/OnProjectileHit 等）+ [24-机制全链](01-引擎/24-机制全链.md)找挂点 |
| 常驻粒子（火焰/烟） | [07-粒子系统](01-引擎/07-粒子系统.md)"生成率累积器/常驻共享池"节 |
| 自定义弹道拖尾 | `SubsystemArrowBlockBehavior.cs:14`（AddTrail 一行注册） |
| 3D 漂浮伤害文字 | `HitValueParticleSystem.cs:55-111`（唯一 3D 文字粒子，双路批次） |
| 跟随实体的特效 | `OnFireParticleSystem.cs:26-77`+`ComponentOnFire.cs:60-83`（组件每帧喂位置） |
| 换自己的粒子贴图 | `Assets/Textures/*.png` 装进包后同路径 `Get<Texture2D>`；图集排布=横排槽位，`TextureSlotsCount`=每行槽位数 |
