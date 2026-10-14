# Biz Retro × Reconstruction Skill Training：PoC v0

> **状态（2026-10-14）：实验基础设施与独立合成测试集就绪，模型训练和 A/S/B/C 推理尚未执行。** 此目录处于 \`evaluations/\` 下，属于离线研究资产；严禁让正式分析流程加载这里的训练数据、测试答案或评审材料。

## 1. 唯一要回答的问题

给定相同的现有 Biz Retro Skill、开发样本和模型条件，**通过重建失败案例得到的增量 Skill（C），能否比直接阅读案例归纳的增量 Skill（B）更可靠地改善此前未见过的会议审计？**

同时必须检验它是否优于现有 Skill（S）。优秀的原版 Skill 是本项目真正的强基线。

| 实验臂 | 推理时加载的内容 | 目的 |
| --- | --- | --- |
| A · Generic | 通用会议审计指令 | 观察模型已有能力与任务难度 |
| S · Frozen | 当前 \`SKILL.md\` + Mode C 相关 references | 代表现有产品能力 |
| B · Distill | S + 从训练案例直接归纳的候选增量 Skill | 检验直接归纳是否有效 |
| C · Reconstruct | S + 先自行分析、对比专家检查点、再修订的候选增量 Skill | 研究论文提出的额外训练收益 |

固定基线：主分支提交 \`bbd2c41379cf8b0d4a492d9c209ba3ff07ead3ca\`；原始 \`SKILL.md\` blob \`284a4096c8df4a08b3a367794126f1e8989a473d\`。**不要为本实验修改现有 Skill**。训练得到的增量规则保存在独立文件，先评价后决定是否吸收。

## 2. 数据和当前限制

- **开发/训练种子**：仓库原有的 \`tests/cases/case-01\` 至 \`case-06\`，使用各自 \`input.md\` 和 \`expected-checks.md\`。这些案例参与过原 Skill 的开发，只有流水线联调意义，**不能作为证明持续学习有效的独立训练证据**。
- **新测试集**：\`holdout/h01\` 至 \`h06\`，2026-10-14 创建的六个合成商业场景。每个案例只有带行号的源材料。对应人工检查点在 \`holdout-gold.json\`，推理输入从不包含此文件。
- **新测试集覆盖**：真正得到审批的试点；会后群消息改写结论；转化率分母变化；顾问强硬行为与利益冲突误归因；低可信说话人标签；职责清晰的真正并行推进。
- **重要限制**：合成案例规模只有 6，作者本人设计了标注标准，仍存在作者偏好和数据构造偏差。初轮只能定位机制问题与风险，**不能作统计显著或真实业务泛化主张**。扩展研究需要独立标注的真实、多行业案例，和额外的全新训练案例。

## 3. 实验操作

所有命令在仓库根目录执行。脚本只使用 Python 标准库，完全不调用 LLM、Codex 或付费 API。

### 3.1 准备训练提示包

\`\`\`bash
python3 evaluations/skill-training-poc/run_poc.py train-pack \
  --out /tmp/biz-train-pack
\`\`\`

每个开发案例生成三份材料：

1. \`B-distill-XX.md\`：向模型提供同一案例的源材料与人工专家检查点，让它直接修订累计的 \`B-delta.md\`。
2. \`C-forward-XX.md\`：向模型提供冻结的 Biz Retro 协议与案例源材料，得到**真实的、完整的**重建报告。
3. \`C-backward-XX.md\`：再提供本轮 C 的真实报告、同一案例的专家检查点与上轮 \`C-delta.md\`，要求从具体错误归纳并更新规则。

按案例 01→06 顺序分别滚动更新 B、C 的 delta，记录每轮报告、修订内容、模型版本、推理参数和实际 token/美元成本。B 与 C 使用相同开发案例、顺序、冻结 Skill 和 delta 字数上限。C 多了 Forward 调用，必须公开报告训练成本；如果要做严格同成本对照，允许 B 在相同训练预算内进行额外迭代，并预先记录预算上限。

**禁止把测试集结果当作迭代反馈。** 如果一次测试后想修改规则，必须更换新的测试集才可再次宣称泛化。

### 3.2 构造四组模型输入

\`\`\`bash
python3 evaluations/skill-training-poc/run_poc.py prepare \
  --arms A,S,B,C \
  --delta-b /tmp/B-delta.md \
  --delta-c /tmp/C-delta.md \
  --out /tmp/biz-test-prompts
\`\`\`

目前还没有训练得到的 delta 文件，所以可以先执行：

\`\`\`bash
python3 evaluations/skill-training-poc/run_poc.py prepare \
  --arms A,S --out /tmp/biz-test-prompts
\`\`\`

脚本会验证冻结 \`SKILL.md\` 指纹，并输出每组 6 个模型输入与 \`manifest.json\`（含输入哈希）。生成的 Prompt 只包含测试 **input**，不会打开 \`holdout-gold.json\`。

**重要隔离要求**：用独立且无仓库工具权限的模型会话执行这些 prompt。不要让 Codex/Claude Code 在整个仓库根目录自主搜索；评测材料和答案就在这个仓库里，工具扫描会导致答案泄漏。不要在测试推理时使用训练案例或此前测试输出作为会话历史。

固定一个模型、版本、temperature、最大输出 token、任务提示和输出格式；最初运行一次全组联调，后续建议跨 3 个独立随机种子复跑。保留完整报告文本及真实调用成本。

模型结果保存为：

\`\`\`text
/tmp/biz-outputs/
  A/h01-authorized-pilot.md
  S/h01-authorized-pilot.md
  B/h01-authorized-pilot.md
  C/h01-authorized-pilot.md
  ...其他案例同名...
\`\`\`

### 3.3 匿名化与人工评价

\`\`\`bash
python3 evaluations/skill-training-poc/run_poc.py blind \
  --outputs /tmp/biz-outputs \
  --blind-dir /tmp/biz-blind-reports \
  --mapping /tmp/biz-private-mapping.json
\`\`\`

评阅者只看 \`biz-blind-reports\` 的报告、对应源材料与 \`holdout-gold.json\` 的标准。分组映射单独保存，不给评阅者。每份输出都记一条 JSONL 评价：

\`\`\`json
{"blind_id":"h01-authorized-pilot-<随机码>","covered":["r1","r2","r3"],"violations":[],"supported_claims":5,"unsupported_claims":0,"valid_anchors":5,"invalid_anchors":0,"unsupported_high_risk_claims":0}
\`\`\`

字段定义：

- \`covered\`：输出实际覆盖且正确的 required 检查点 ID；空话、仅套模板不给分。
- \`violations\`：明确触犯 forbidden 的检查点 ID，按 major / critical 区分严重度。
- \`supported_claims\` / \`unsupported_claims\`：报告中独立、对决策有影响的实质性断言数量。同一事实重复出现只记一次，推论应标明推论性质。
- \`valid_anchors\` / \`invalid_anchors\`：引用源行且引用确实支持断言的数量/无效锚点数量。
- \`unsupported_high_risk_claims\`：缺少依据却将动机、腐败、采购授权等高风险推测升级成事实的断言数量；这类断言也计入 \`unsupported_claims\`。

建议双人独立评价、分歧仲裁。第一轮允许单人，但必须明确标记。

\`\`\`bash
python3 evaluations/skill-training-poc/run_poc.py score \
  --reviews /tmp/biz-review.jsonl \
  --mapping /tmp/biz-private-mapping.json \
  --out /tmp/biz-scored.json
\`\`\`

**探索性汇总指标**：Gold 事实判断召回（60%）、实质断言精确率（30%）、证据锚点准确率（10%），扣除 major（8分）、critical（18分）与无据高风险断言（12分/条）。这个综合分数用于快速排查，不应替代分别披露的原始指标。评分工具会标出缺少评审的实验臂，防止把未完成评价当成全量结果。

## 4. 预先锁定的结果解释

- **C 相对 B、S 都更好，且高风险误报不增加**：有继续扩大重建训练的价值。
- **C 优于 B，却弱于 S**：理论方法有信号，但暂时不值得替换成熟 Skill。
- **B、C 基本一致且都优于 S**：技能增量可能有价值，重建方法额外收益不足。
- **C 召回提高但关键误报上升**：按安全回退处理，不能以综合分掩盖假阳性风险。
- **S 近乎满分**：测试集天花板太低，须加更困难、含信息缺口的案例。

第一轮预设的继续研究门槛：C 对 S 和 B 在至少 4/6 个独立案例中具有正向实质差异，且 critical 误报为 0；至少在 2 个负对照案例中维持判断克制。此门槛仅用于决定是否扩样，**不是论文假设获得统计验证**。增加真实独立案例至 20～30 个以后再进行重复试验与置信区间分析。

## 5. 当前边界与下一步

当前可交付的是：冻结基线、六个新测试输入及隐藏检查点、训练提示生成器、独立模型输入生成器、匿名盲评与统计脚本、自动化工具测试。

**尚未完成**：真实模型 Forward、B/C delta 的训练、24 份 A/S/B/C 测试报告、人工评分，以及任何模型增益结论。

下一次执行时，从 \`train-pack\` 开始记录运行；不要修改 \`SKILL.md\`，也不要发布未经验证的新规则。原有 \`evaluations/ablation-2026-07/\` 的结论和 2026-10-12 勘误保持不动。
