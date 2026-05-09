# Qwen Vision Mining Prompt Format

Use this reference to generate prompt JSON for autonomous-driving front-camera visual data mining.

## Top-Level File Shape

The deliverable is a JSON file with exactly one top-level field:

```json
{
  "prompt": "..."
}
```

The `prompt` value is the full instruction sent to Qwen/Qwen3-VL. Do not output a bare prompt string unless the user explicitly asks for that.

The embedded `prompt` must stay under 7000 tokens. If a draft is too long, compress examples and duplicated exclusions first; do not remove output-format constraints or core hard-negative boundaries.

## Embedded Prompt Structure

Every prompt must contain these four sections in order:

1. Expert role and task sentence.
2. `### 场景定义与判定规则`
3. `### 输出格式要求`
4. `### 参考示例`

Default opening sentence:

```text
你是专业的自动驾驶前视视觉识别专家，需基于1920×1080前视摄像头高清图片，精准判断/识别{任务名称}，仅输出指定格式的JSON结果，无任何多余文字。
```

Use `判断` for scene classification and `识别` for object/mark detection.

## Label Rules

- Default to single-label: each model output contains exactly one result label.
- Labels must be English identifiers.
- Prefer `snake_case` for generated labels.
- Preserve user-provided label spelling when supplied.
- Always include `None` unless the user explicitly provides a closed class set with no negative class.
- Use `None` exactly, not `none`, `null`, `无`, or `其他`.
- Use multi-label only when the user explicitly needs co-occurring categories in one image and the downstream parser accepts list outputs.

## Judgment Rule Pattern

For each positive class:

```text
1. **中文名（english_label）**：
   - 判定条件：...
   - 输出：result字段为["english_label"]，reason字段说明...
```

For `None`:

```text
N. **无（None）**：
   - 判定条件：画面中不存在目标，或不满足上述任一类别的判定条件。
   - 输出：result字段为["None"]，reason字段说明未检测到目标或不属于目标场景。
```

For ambiguous cases, add exclusion rules under the relevant class. If a key condition is unclear, prefer `None` unless the prompt defines a stricter positive exception.

## Output Format Section

Include these requirements, adapted with the allowed labels:

```text
### 输出格式要求
- 严格返回JSON格式，result和reason字段均为列表结构（[]）；
- result字段内容仅为："label_a"、"label_b"或"None"；
- result字段每次只能输出一个标签，不允许同时输出多个标签；
- reason字段为中文描述，需明确说明：①识别/判断结果 ②判定依据（如位置、数量、可见视觉特征、排除原因等）。
```

For object detection tasks, ask `reason` to include position and count. For scene classification, ask it to include scene type and boundary conditions.

For production mining prompts, also require `reason` to include valid scope and hard-negative reasoning when relevant: whether the target lies inside the allowed region, whether lighting/occlusion/blur permits judgment, and why common look-alikes are excluded.

## Reference Examples

Include at least two valid JSON examples:

- One positive example.
- One `None` example.

Example for an object:

```text
示例1（检测到地锁）：
{"result":["parking_lock"],"reason":["1920×1080图像检测到地锁，画面中部偏右停车位区域可见折叠三角形金属结构，数量为1个，具有金属连杆和铰链等典型地锁特征"]}

示例2（未检测到地锁）：
{"result":["None"],"reason":["1920×1080图像未检测到地锁，画面中仅可见普通停车场地面和车位线，无折叠金属结构、机械连杆或地锁装置"]}
```

Example JSON lines may be compact (`{"result":["x"],...}`) or spaced like the legacy examples, but the final model output must still be strict JSON.

Keep examples targeted. Prefer one clear positive, one boundary positive when needed, and one or more hard `None` examples over a long list of repetitive positives.

## Multi-Label Requests

Prefer splitting co-occurring targets into separate single-label prompts. If the user explicitly asks for one multi-label prompt:

- `result` is a list of all visible allowed labels.
- The list is ordered, usually left-to-right then top-to-bottom when location matters.
- Repeated categories are not repeated.
- `None` is used only when no allowed label appears, and must not be mixed with positive labels.
- The output section must say this clearly, and examples must include at least one multi-label positive and one `None`.
