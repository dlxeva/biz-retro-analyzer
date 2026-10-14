# Biz Retro Skill Training：真实模型实验执行手册

> 2026-10-14。已完成**模拟模型**的端到端验证，尚未运行付费模型。此前消融研究存在评分循环性等勘误，不能以旧分数宣称本轮模型能力提升。

## 研究目标

四组对照：A（通用提示词）、S（冻结现有 Biz Retro）、B（在 S 上直接蒸馏的增量规则）、C（在 S 上根据自身重建错误学习的增量规则）。B/C 使用完全相同的开发案例和冻结 Skill，每轮都调用模型两次，各自累计并版本化 Delta。

**调用预算：** 6 个训练案例 × 4 次模型调用 = 24 次；6 个独立测试案例 × 4 组 = 24 次，总计 48 次。B/C 的实际输入输出 Token 可能不同，必须单独报告。所有推理均为没有工具、没有历史对话的新调用。

第 i 轮 C Forward 输入 = 冻结 Skill + 已经学到的 C Delta(i−1) + 当前原材料。此阶段严禁提供该案例专家答案。只有 Forward 完成后，Backward 才接收 Forward 的真实输出、专家检查点及旧 Delta，并生成更新后的 Skill；下一轮 Forward 确实会加载此版本。

B 第一次直接学习源材料和专家检查点；第二次只审查第一次归纳的规则，因此总调用数与 C 持平，但没有进行业务重建。如模型输出 NO_CHANGE，则保留上一轮 Delta；若六轮都没有学到新规则，B/C 测试应回退成与 S 完全相同的输入，并如实标注零进步结果。

## 环境与数据边界

1. Python 3.8+；从仓库根目录运行 evaluations/skill-training-poc/train_loop.py。
2. 现有开发集 tests/cases/case-01 至 case-06 早已影响过 Skill 设计，训练仅属于工程验证；六个新合成测试案例也只能作为方向性信号。要证明真实业务泛化，必须补充新的独立训练材料、真实盲测案例和独立人工标注。
3. 所有实验输出目录必须放在仓库外。训练提示包含部分案例专家检查点，评测提示永远只含测试源材料和对应组 Skill。模型通过独立 Chat Completions API 使用时不附带任何仓库检索工具。
4. 不把 API 密钥、真实客户私有原文、训练追踪记录或个人数据提交到公开 GitHub。
5. --authorize-api-spend 明确允许可能计费的请求；--max-api-calls 限制每轮预先许可的调用次数，--max-output-tokens 限制单次输出长度。这些参数无法保证具体美元上限。请先查明选用模型价格并自行决定是否执行。本仓库 CI 不会调用任何付费模型。

## 步骤一：真实模型训练

例如在自己的可信环境使用 OpenRouter。先由你自己安全配置 OPENROUTER_API_KEY 环境变量，再将 YOUR_MODEL_ID 改成已确定且支持标准 Chat Completions 的模型版本。不要将密钥发到聊天或写进 Git。

~~~bash
python3 evaluations/skill-training-poc/train_loop.py train \
  --provider chat-completions \
  --endpoint https://openrouter.ai/api/v1/chat/completions \
  --api-key-env OPENROUTER_API_KEY \
  --model YOUR_MODEL_ID \
  --authorize-api-spend \
  --max-api-calls 24 \
  --max-output-tokens 3000 \
  --out /tmp/biz-skill-train-v1
~~~

输出中检查：manifest.json 的 complete=true、calls=24；每一轮 C-forward.prompt.md 的 C Delta 都等于上一轮训练结果；C-forward 不包含本轮专家检查点。B-delta.md、C-delta.md 只允许可复用规则，不能包含案例中的特殊人物和答案。calls.jsonl 保留每次调用的 Prompt/Response SHA、实际模型版本和 Token（如服务商返回）。

可先执行单案例的兼容性与成本测试：

~~~bash
python3 evaluations/skill-training-poc/train_loop.py train \
  --provider chat-completions \
  --endpoint https://openrouter.ai/api/v1/chat/completions \
  --api-key-env OPENROUTER_API_KEY \
  --model YOUR_MODEL_ID \
  --authorize-api-spend \
  --max-cases 1 \
  --max-api-calls 4 \
  --out /tmp/biz-skill-one-case
~~~

单案例结果将显示 complete=false，评测入口不会接收它作为完整训练结果。如果已经自行接入可信本地模型，也可以使用 --provider command --command "python3 /绝对路径/model_client.py"；客户端从 stdin 接收完整 Prompt、向 stdout 返回纯文本。不调用 Codex。

## 步骤二：四组隔离评测

务必使用与训练相同的模型版本。评测时不调用任何评分器，也不会读取隐藏答案文件：

~~~bash
python3 evaluations/skill-training-poc/train_loop.py eval \
  --provider chat-completions \
  --endpoint https://openrouter.ai/api/v1/chat/completions \
  --api-key-env OPENROUTER_API_KEY \
  --model YOUR_MODEL_ID \
  --authorize-api-spend \
  --max-api-calls 24 \
  --max-output-tokens 3000 \
  --training-dir /tmp/biz-skill-train-v1 \
  --out /tmp/biz-skill-eval-v1
~~~

输出：/tmp/biz-skill-eval-v1/outputs/A、S、B、C，每组 6 份案例报告，合计 24 份。每份 Prompt 与响应都有独立存档和 SHA-256。

## 步骤三：匿名盲评和统计

~~~bash
python3 evaluations/skill-training-poc/run_poc.py blind \
  --outputs /tmp/biz-skill-eval-v1/outputs \
  --blind-dir /tmp/biz-skill-blind \
  --mapping /tmp/biz-private-map.json
~~~

评审者不能接触组别映射。应按 holdout-gold.json 的 Required/Forbidden 检查点标注，并独立统计事实召回、高风险误报、实际引用准确率、人工审查成本。JSONL 单行示例：

~~~json
{"blind_id":"h01-authorized-pilot-ANONID","covered":["r1","r2"],"violations":[],"supported_claims":4,"unsupported_claims":0,"valid_anchors":4,"invalid_anchors":0,"unsupported_high_risk_claims":0}
~~~

~~~bash
python3 evaluations/skill-training-poc/run_poc.py score \
  --reviews /tmp/biz-review.jsonl \
  --mapping /tmp/biz-private-map.json \
  --out /tmp/biz-scores.json
~~~

只有所有组内的 6 份样本均已评分，该组才会显示 complete=true；四组全部完成才会显示 four_arm_complete=true。历史旧消融分数只提供定性参考。

## 下一阶段通过标准

- C 比 S、B 更好，重大误报没有增加：扩大到 20～30 个独立真实案例，多次重复，给出置信区间。
- B、C 差不多但都优于 S：Skill 增量可取，尚无重建训练额外价值的证据。
- C 主要靠更多 Token 获胜：继续匹配 Token 预算后再做机制判断。
- C 导致更多无依据动机指控：阻止增量 Skill 进入正式分析流程。
- 全程 NO_CHANGE：这是有信息量的零增益结果；检查任务是否太简单或现有 Skill 已饱和。

## 当前状态

- [x] 冻结基线与 Draft PR 隔离。
- [x] B/C 两次调用对照、逐轮更新、调用日志、Token 统计。
- [x] 6 个合成测试案例、44 项隐藏检查点和匿名评分。
- [x] 模拟模型端到端测试与 Python 3.8/3.12/Windows CI。
- [ ] 真正的模型推理、独立人工盲评和技能收益数据。
- [ ] 足够数量的独立真实材料与跨项目复现实验。
