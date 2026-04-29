# Prompt Generator Skill

Codex skill for generating single-label Qwen/Qwen3-VL visual data-mining prompt JSON for autonomous-driving front-camera images.

The generated prompt follows the project pattern used by `visible_invisible_night_20260211.json`: the deliverable is a top-level JSON object with one `prompt` field, and the embedded prompt instructs the vision model to return only `{"result":[...],"reason":[...]}`.

## What It Does

- Generates production-style prompt JSON for image-level data mining.
- Targets autonomous-driving front-view visual recognition tasks.
- Enforces a single-label output pattern: one English label or `None`.
- Keeps `result` and `reason` as list fields for downstream pipeline compatibility.
- Includes positive and `None` examples in generated prompts.

## Install

Place this folder under your Codex skills directory:

```text
C:\Users\28349\.codex\skills\prompt-generator
```

Expected structure:

```text
prompt-generator/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── prompt-format.md
│   └── visible-invisible-night-example.json
└── scripts/
    └── validate_prompt_json.py
```

Restart Codex or refresh skills if the skill does not appear immediately.

## Usage

Invoke the skill explicitly:

```text
$prompt-generator 帮我生成一个地锁识别的数据挖掘 prompt
```

The default output should be complete JSON content:

```json
{
  "prompt": "..."
}
```

## Scope

This first version is single-label only.

If a task needs multiple labels that may co-occur in one image, split it into multiple single-label prompts. For example, instead of one prompt that returns both `traffic_cone` and `barrier`, create separate prompts for each target.

## Validation

Validate a generated prompt JSON file:

```bash
python scripts/validate_prompt_json.py path/to/prompt.json
```

Validate the bundled reference example:

```bash
python scripts/validate_prompt_json.py references/visible-invisible-night-example.json
```

## Repository Contents

- `SKILL.md`: Skill trigger description and operating instructions.
- `references/prompt-format.md`: Required prompt JSON format and generation rules.
- `references/visible-invisible-night-example.json`: Concrete reference prompt in the target format.
- `scripts/validate_prompt_json.py`: Structural validator for generated prompt JSON.
- `agents/openai.yaml`: UI metadata for Codex.
