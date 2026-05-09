# Production Vision Mining Prompt Method

Use this reference when turning a vague visual mining request into a prompt that can survive real autonomous-driving data noise.

## Task Card First

Write a short internal task card before drafting the prompt:

| Field | What to decide |
|---|---|
| Target | What should be mined, in Chinese plus the English label. |
| Business scope | Why the data is useful and what should not be collected. |
| Source | Camera, resolution, sensor, frame type, region of interest. |
| Positive evidence | Required visible cues, not just a name. |
| Valid location | Main lane, drivable paved road, parking slot, road edge, sky, roadside, etc. |
| Hard None | Look-alikes, off-scope regions, poor quality, ambiguity, occlusion, lighting issues. |
| Ambiguity policy | Usually conservative: if any key condition is unclear, output `None`. |

Do not start from examples alone. Examples calibrate the rules; they do not replace rules.

Keep the final embedded `prompt` under 7000 tokens. Spend the budget on decision boundaries, hard negatives, and evidence requirements; cut narrative context, repeated synonyms, and redundant examples.

## Rule Pattern

A strong mining prompt has a positive gate and a `None` gate.

Positive gate:

```text
1. **中文目标名（english_label）**：
   - 只有当{有效范围}内存在{目标}时，才输出english_label。
   - 必须满足：①位置/范围 ②形态/结构 ③清晰度/尺寸 ④排除易混淆项。
   - 特殊边界：说明靠近图像边缘、低光照、遮挡、无车道线、裂纹/修补/井盖/线缆等场景如何判。
   - 输出：result字段为["english_label"]；reason说明数量、位置、范围确认和关键视觉证据。
```

None gate:

```text
2. **无有效目标（None）**：
   - 目标不存在，或位置、形态、尺寸、清晰度、照明、遮挡任一关键条件不足时输出None。
   - 排除：列出真实业务中的高频误检项和离域区域。
   - 输出：result字段为["None"]；reason说明未检测到目标或被排除原因。
```

## Hard None Library

Choose domain-specific hard negatives instead of generic "not found":

| Target type | Common hard negatives |
|---|---|
| Road pothole / depression | crack, alligator crack, sealed joint, flat repair patch, color difference, oil stain, wet mark, puddle, shadow, night dark spot, tire mark, manhole, worn lane marking, off-road shoulder, sidewalk, parking area. |
| Pole / utility object | streetlight, traffic light pole, sign pole, camera pole, advertising pole, flagpole, gantry, bridge pier, guardrail post, tree trunk, cable without a visible connected pole. |
| Night visibility | dusk, tunnel, bright headlight-only region, remote weak light spot, one completely dark image edge, overexposure, motion blur. |
| Weather / visibility | wet road without rain, windshield dirt, glare, fog-like overexposure, dust on lens, backlight haze, normal cloudy sky. |
| Road markings | worn texture, repair line, shadow, curb edge, vehicle body reflection, temporary construction mark, duplicate category occurrence. |

## Example Set

Use examples as a calibration set:

- Required: one clear positive and one `None`.
- Add boundary positive when the target is valid but easy to wrongly exclude, such as near image edge or no lane line.
- Add hard `None` when a look-alike is easy to wrongly include.
- For low-light tasks, include one example requiring the model to explain whether lighting is sufficient.
- For road-surface tasks, include examples for cracks, repair patches, manholes, puddles, shadows, and off-scope regions when relevant.

Each example must be a valid JSON object and must obey the same label policy as the prompt.

If examples push the prompt near 7000 tokens, keep the most diagnostic cases: one clear positive, one boundary positive, one hard negative, and one `None` for absence or insufficiency.

## Reason Contract

`reason` should force evidence. For positives, require:

- recognition result;
- target count and approximate position;
- valid region or business scope confirmation;
- key visual evidence;
- why common confounders do not explain it when relevant.

For `None`, require:

- absence or exclusion result;
- the strongest exclusion reason;
- whether the issue is location, morphology, scale, clarity, light, occlusion, or ambiguity.

If a prompt needs a conservative output policy, state it explicitly: "若位置、尺寸、形态、边界或光照任一关键条件不明确，输出None。"

## Multi-Label Exception

Default to single-label prompts. If the user explicitly needs co-occurring labels in one image:

- State that `result` is an ordered, de-duplicated list of all visible allowed labels.
- Sort by spatial order when useful, such as left-to-right then top-to-bottom.
- Forbid `None` from appearing with any positive label.
- Ensure every example with multiple labels is intentional.
- Validate with `--allow-multi-label`.
