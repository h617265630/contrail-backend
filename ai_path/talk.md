# Talk — Q&A with Claude

---

## Q1: 项目结构文档化

**User:** 把项目结构写到 structured.md 放到根目录（讲清楚有几个 stage）

**Claude:** 已创建 structured.md，包含完整目录结构和 6 个 stage 的数据流说明。

---

## Q2: 优化方向 & 免费替代工具

**User:** 这个效果我还算满意，能进一步优化吗，有免费的类似 tavily 的工具吗，然后我想要考虑节省成本（api方面）

**Claude:** 提出了几个优化方向和免费替代工具：
- Brave Search（2000次/月免费）
- Serper（10,000次/月免费）
- 节省成本的策略：缓存、LLM 分层降级、查询数动态调整

---

## Q3: 数据库缓存方案

**User:** 我可以把结果输入数据库吗，然后先查数据库是否有类似的问题，然后如果没有的话再去 ai 生成

**Claude:** 确认了需求后，提出了三条路：
- SQLite（轻量、本地）
- PostgreSQL（生产级）
- Qdrant / Chroma（向量相似度匹配）

---

## Q4: 向量数据库的推荐

**User:** 是不是使用向量数据库适合一点

**Claude:** 确认向量数据库更适合语义相似匹配，对比了方案，推荐 ChromaDB（单文件、本地、零服务）。

---

## Q5: RAG 的区别

**User:** RAG 呢？

**Claude:** 解释了 RAG 与当前 pipeline 的区别：
- 当前：Search → Summarize → Generate（实时爬网页）
- RAG：从本地文档库检索相关片段，再让 LLM 生成
- 用户需求更偏向：缓存复用（相似 topic 直接返回已有报告）

---

## Q6: API 法律风险

**User:** 使用 api 有法律风险吗

**Claude:** 分析了两类风险：
- 数据合规风险（用户输入进入第三方、网页内容版权）
- 各主要服务商（OpenAI、MiniMax、Tavily、Brave、Serper）的实际风险等级
- 结论：个人项目风险极低，商业化需注意 ToS 和 GDPR

---

## Q7: 订阅策略定价

**User:** 我既然要使用怎么多收费api，我的网站提供给用户的订阅策略该怎么定

**Claude:** 推荐了 Freemium + 3 层订阅模式：
- Free：3次/月
- Basic：$5/月，20次
- Pro：$15/月，100次
- Unlimited：$49/月

---

## Q8: 100次生成成本

**User:** 100 次生成需要多少成本呢，单论生成学习路径

**Claude:** 拆解了 6 个 stage 的 token 消耗：
- 单次生成总计约 46,400 input + 3,700 output tokens
- 用 GPT-4o-mini：$0.035/次
- 100次生成总成本约 **$3.5**（搜索用 Brave 免费额度）
- 定价 $15 的 Pro 档，利润率 76%

---

## Q9: 做到 app.py 里

**User:** 好的 做到app.py 里

**Claude:** 已实现订阅系统到 app.py：

**新建文件：`utils/subscription.py`**
- Tiers：Free(3次) / Basic(20次/$5) / Pro(100次/$15) / Unlimited($49)
- JSON 文件持久化用户 usage data
- 月度自动重置计数器
- 每次生成后 deduct quota
- 历史记录查看

**修改 app.py：**
- Sidebar 显示当前 plan、使用量进度条、剩余次数
- 到达限制时禁用按钮并提示升级
- 生成成功后 rerun 刷新 sidebar 计数
- 支持手动切换 tier 档位

---

## Q10: Tavily 免费额度不够

**User:** 关键是 tavily 我个人是 2000次/月免费，如果是给用户用的话，肯定是不够的

**Claude:** 确认了问题：
- 100 用户 × 100 次生成 = 10,000 次搜索/月
- Tavily 免费 2000 次完全不够
- Brave Search 同为 2000 次/月免费，也不够

**替代方案：**
- Serper：10,000 次/月免费（Google 搜索）
- Brave Search + Serper 混用，分摊额度
- 接入付费搜索 API（成本可控，按量计费）
- 搜索结果缓存复用（同一 topic 第二次不搜）

---

## Q11: 100次根本用不完

**User:** 一般专门想要学习一门知识的人是不太会用很多次路径生成的，所以100次应该是完全用不完的

**Claude:** 同意并重新算账：
- 用户实际行为：学一门知识通常生成 1-3 次就够用
- 100 次完全用不完，$15/Pro 档溢价极高（85-215倍）
- 建议：低价订阅 $2-3/月，反正成本接近零
- 核心转变：从卖"API 调用次数" → 卖"满足个性化需求的学习体验"

---

## Q12: 用户粘性与多版本学习路径

**User:** 我现在在考虑用户粘性和套餐额度的关系，我是不是可以添加生成多种路径的选择，比如说选择不同资源、难度、内容类型

**Claude:** 确认了方向：同一 topic，不同"版本"让用户愿意多生成几次。

**新增 4 个偏好选项：**

| 选项 | 值 | 说明 |
|------|-----|------|
| 学习深度 | quick / standard / deep | 快速入门 / 标准路径 / 深度系统 |
| 内容类型 | video / article / mixed | 视频为主 / 文章为主 / 混合 |
| 资源数量 | compact(5) / standard(10) / rich(15) | 精简 / 标准 / 丰富 |
| 实战比例 | theory_first / balanced / practice_first | 理论优先 / 平衡 / 实战优先 |

**商业价值：**
- 同一 topic，用户愿意生成 3-5 个不同版本才选定
- Free/Basic 档锁定为 standard 选项
- Pro/Unlimited 解锁全部偏好组合

**已实现：**
1. `models/schemas.py` — PipelineState 新增 4 个偏好字段
2. `pipeline/queries.py` — 根据 resource_count 动态调整查询数量，根据 content_type 调整查询类型偏好
3. `pipeline/organize.py` — 根据 learning_depth 调整章节数量和深度，根据 practical_ratio 调整组织结构
4. `pipeline/report.py` — 根据偏好调整报告风格（intro 长度、goal 风格、表格列数、emoji 密度）
5. `app.py` — 新增 4 个偏好选择器，Free/Basic 锁定为 standard，Pro 解锁全部选项
6. `utils/subscription.py` — record_generation 支持存储 preferences
