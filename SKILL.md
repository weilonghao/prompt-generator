---
name: prompt-generator
description: Generate single-label Qwen/Qwen3-VL visual data-mining prompt JSON for autonomous-driving front-camera images. Use when the user asks to create, write, refine, or validate a prompt for visual recognition, image-level data mining, autonomous-driving front-view scene/object detection, or a prompt in the same format as visible_invisible_night_20260211.json.
---

# Prompt Generator

## Purpose

Generate production-style prompt JSON for autonomous-driving front-view image mining. The output format follows `visible_invisible_night_20260211.json`: a top-level JSON object with one `prompt` string, where the embedded prompt instructs the vision model to return only `{"result":[...],"reason":[...]}`.

This first version is single-label only. Each image must produce exactly one English label in `result`, or `["None"]`.

## Required References

- Read `references/prompt-format.md` before generating or revising a prompt.
- Use `references/visible-invisible-night-example.json` as the highest-priority concrete format example when the user asks for the established project pattern.
- Use `scripts/validate_prompt_json.py` to validate any generated `.json` prompt file when saving one.

## Workflow

1. Identify the mining target, positive label, and negative/None condition from the user request.
2. Choose or preserve the English label:
   - Use a user-provided label exactly when given.
   - Otherwise generate a concise `snake_case` English label, such as `parking_lock` or `traffic_cone`.
   - Keep `None` exactly as uppercase `N`.
3. Write a prompt with four sections:
   - Expert role and image assumptions.
   - Scene/object definition and judgment rules.
   - Output format requirements.
   - Reference examples.
4. Return complete JSON file content by default:

```json
{
  "prompt": "..."
}
```

5. If the user asks to save the file, save it as UTF-8 JSON and run the validation script.

## Single-Label Rules

- Do not generate multi-label prompts in this first version.
- If the user asks for multiple labels that can co-occur in one image, explain that this skill is single-label and recommend splitting the task into one prompt per target.
- If the user asks for mutually exclusive classes, generate one single-label classification prompt with all class labels plus `None` when applicable.
- The embedded model-output examples must not show `result` with multiple labels, such as `["a","b"]`.

## Output Prompt Requirements

The embedded prompt must require the vision model to:

- Return strict JSON only, with no extra text.
- Return exactly two fields: `result` and `reason`.
- Make both fields list structures.
- Put exactly one allowed English label in `result`.
- Use `["None"]` when the target is absent or no class applies.
- Write `reason` in Chinese and include the decision basis.
- Prefer examples that include a positive case and a `None` case.

For target/object detection prompts, the `reason` requirement should ask for:

- Detection result.
- Position and count when visible.
- Key visual features.
- Why `None` applies when absent.

For scene classification prompts, the `reason` requirement should ask for:

- Scene type.
- Key visual evidence.
- Required exclusion or boundary conditions.

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

Validation is a minimum structural check. Still inspect the prompt manually for business correctness, especially label names and judgment boundaries.
