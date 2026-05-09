---
name: prompt-generator
description: Use when creating, refining, or validating Qwen/Qwen3-VL visual data-mining prompts for autonomous-driving front-camera images, especially image-level mining targets, front-view scene or object recognition, road anomaly mining, hard negative rules, or project prompts like visible_invisible_night_20260211.json.
---

# Prompt Generator

## Purpose

Generate production-style prompt JSON for autonomous-driving front-view image mining. The deliverable is normally a top-level JSON object with one `prompt` string, where the embedded prompt instructs the vision model to return only `{"result":[...],"reason":[...]}`.

Default to single-label mining: each image produces exactly one English label in `result`, or `["None"]`. Use multi-label only when the user explicitly asks for co-occurring categories and the downstream parser supports list outputs.

## Required References

- Read `references/prompt-format.md` before generating or revising a prompt.
- Read `references/mining-prompt-method.md` for production mining prompts, hard negatives, boundary cases, and evidence-driven `reason` requirements.
- Use `references/visible-invisible-night-example.json` as the highest-priority concrete format example when the user asks for the established project pattern.
- Use `scripts/validate_prompt_json.py` to validate any generated `.json` prompt file when saving one.
- Keep the embedded `prompt` under 7000 tokens.

## Workflow

1. Build a short task card before writing:
   - target concept and business goal;
   - allowed label set;
   - valid image source, camera, and region of interest;
   - positive visual evidence;
   - hard `None` exclusions and confusing non-targets;
   - ambiguity policy.
2. Choose or preserve labels:
   - Use a user-provided label exactly when given.
   - Otherwise generate a concise `snake_case` English label, such as `parking_lock` or `traffic_cone`.
   - Keep `None` exactly as uppercase `N`.
3. Write the prompt with four sections:
   - Expert role and image assumptions.
   - Scene/object definition and judgment rules.
   - Output format requirements.
   - Reference examples.
4. Make rules evidence-based:
   - positive rules must define location/scope, morphology, visibility quality, and key visual evidence;
   - `None` rules must explicitly cover off-scope locations, look-alikes, poor quality, occlusion, low light, and evidence-insufficient cases;
   - ambiguous cases should default to `None` unless the prompt defines a stricter positive exception.
5. Write examples as a calibration set:
   - at least one clear positive and one `None`;
   - add boundary positives and hard negatives for risk-heavy tasks like potholes, road-surface depression, poles, night visibility, lane markings, weather, occlusion, or small targets.
6. Compress before finalizing:
   - keep the embedded `prompt` under 7000 tokens;
   - remove repeated examples, duplicate exclusions, narrative background, and low-value wording before weakening judgment rules.
7. Return complete JSON file content by default:

```json
{
  "prompt": "..."
}
```

8. If the user asks to save the file, save it as UTF-8 JSON and run the validation script.

## Label Rules

- Prefer one prompt per mining target and one output label per image.
- If the user asks for multiple labels that can co-occur, recommend splitting into one prompt per target unless they explicitly need a multi-label prompt.
- If classes are mutually exclusive, generate one classification prompt with all class labels plus `None` when applicable.
- For multi-label prompts, require ordered, de-duplicated labels in `result`, forbid mixing `None` with positive labels, and validate with `--allow-multi-label`.

## Output Prompt Requirements

The embedded prompt must require the vision model to:

- Return strict JSON only, with no extra text.
- Return exactly two fields: `result` and `reason`.
- Make both fields list structures.
- Put only allowed English labels in `result`.
- Use `["None"]` when the target is absent or no class applies.
- Write `reason` in Chinese and include the decision basis.
- Include evidence, not just conclusions, in `reason`.

For target/object detection prompts, the `reason` requirement should ask for:

- Detection result.
- Position and count when visible.
- Key visual features.
- Domain/scope confirmation, such as main drivable road, parking slot, road edge, or pole type.
- Why `None` applies when absent, out of scope, ambiguous, occluded, too small, too far, blurred, or low-confidence.

For scene classification prompts, the `reason` requirement should ask for:

- Scene type.
- Key visual evidence.
- Required exclusion or boundary conditions.

## Quality Gate

Before finalizing a prompt, check:

- The positive label cannot be triggered by a single weak cue such as color, shadow, dark patch, or shape only.
- `None` contains realistic hard negatives from the domain, not just "target absent".
- Boundary cases are handled explicitly, such as image edge, no lane line, low light, manhole, repair patch, crack, ordinary pole, only cable, glare, rain, or occlusion.
- Examples do not contradict the rules and include enough negative calibration for expected false positives.
- The embedded `prompt` does not exceed 7000 tokens.
- The final file is UTF-8 JSON and examples are parseable JSON objects.

## Style Guidance

- Keep the prompt direct and rule-heavy; avoid marketing language.
- Use Chinese for all natural-language instructions inside the prompt.
- Use English only for labels in `result`.
- Use `1920x1080 front-camera high-resolution image` as the assumed source unless the user provides another image source.
- Preserve exact project field names: `prompt`, `result`, `reason`.
- In examples, use valid JSON lines such as `{"result":["parking_lock"],"reason":["..."]}`.

## Validation

When a prompt JSON is written to disk, run:

```bash
python scripts/validate_prompt_json.py path/to/prompt.json
```

For explicit multi-label prompts, run:

```bash
python scripts/validate_prompt_json.py --allow-multi-label path/to/prompt.json
```

Validation is a minimum structural check. Still inspect the prompt manually for business correctness, especially label names, valid scope, hard negatives, and judgment boundaries.
