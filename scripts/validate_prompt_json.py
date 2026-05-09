#!/usr/bin/env python3
"""Validate a Qwen vision mining prompt JSON file."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


DEFAULT_MAX_PROMPT_TOKENS = 7000

REQUIRED_SUBSTRINGS = [
    "result",
    "reason",
    "None",
    "JSON",
    "### 输出格式要求",
    "### 参考示例",
]


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"cannot read file: {exc}") from exc


def _extract_example_json(prompt: str) -> list[dict]:
    examples: list[dict] = []
    for match in re.finditer(r'\{[^{}]*"result"[^{}]*"reason"[^{}]*\}', prompt):
        raw = match.group(0)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            examples.append(parsed)
    return examples


def _requires_list_structure(prompt: str) -> bool:
    list_phrases = [
        "列表结构",
        "字段值均为列表",
        "均为列表",
        "均为list",
        "[]",
    ]
    return any(phrase in prompt for phrase in list_phrases)


def _estimate_prompt_tokens(prompt: str) -> tuple[int, str]:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except Exception:
        tiktoken = None

    if tiktoken is not None:
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(prompt)), "tiktoken:cl100k_base"
        except Exception:
            pass

    cjk_chars = len(re.findall(r"[\u3400-\u9fff]", prompt))
    ascii_chunks = re.findall(r"[A-Za-z0-9_]+", prompt)
    ascii_tokens = sum(max(1, math.ceil(len(chunk) / 3)) for chunk in ascii_chunks)
    symbol_tokens = len(re.findall(r"[^\sA-Za-z0-9_\u3400-\u9fff]", prompt))
    return cjk_chars + ascii_tokens + symbol_tokens, "heuristic"


def validate(
    path: Path,
    allow_multi_label: bool = False,
    max_prompt_tokens: int = DEFAULT_MAX_PROMPT_TOKENS,
) -> list[str]:
    errors: list[str] = []
    data = _load_json(path)

    if not isinstance(data, dict):
        return ["top-level JSON must be an object"]

    keys = set(data.keys())
    if keys != {"prompt"}:
        errors.append('top-level JSON must contain exactly one field: "prompt"')

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append('"prompt" must be a non-empty string')
        return errors

    if max_prompt_tokens > 0:
        token_count, token_method = _estimate_prompt_tokens(prompt)
        if token_count > max_prompt_tokens:
            errors.append(
                f"prompt exceeds {max_prompt_tokens}-token limit: "
                f"estimated {token_count} tokens ({token_method})"
            )

    for token in REQUIRED_SUBSTRINGS:
        if token not in prompt:
            errors.append(f'prompt is missing required text: {token}')

    if '"result"' not in prompt and "result字段" not in prompt:
        errors.append('prompt must explicitly define the "result" field')
    if '"reason"' not in prompt and "reason字段" not in prompt:
        errors.append('prompt must explicitly define the "reason" field')
    if not _requires_list_structure(prompt):
        errors.append("prompt must require result and reason to be list structures")
    if "无任何多余文字" not in prompt and "无多余文字" not in prompt:
        errors.append("prompt must forbid extra model output text")

    examples = _extract_example_json(prompt)
    if len(examples) < 2:
        errors.append("prompt must include at least two parseable JSON examples")

    saw_none = False
    saw_positive = False
    for idx, example in enumerate(examples, start=1):
        result = example.get("result")
        reason = example.get("reason")
        if not isinstance(result, list):
            errors.append(f"example {idx}: result must be a list")
            continue
        if not result:
            errors.append(f"example {idx}: result must not be empty")
            continue
        if not allow_multi_label and len(result) != 1:
            errors.append(f"example {idx}: single-label prompts must have exactly one result value")
            continue
        if allow_multi_label and "None" in result and len(result) > 1:
            errors.append(f'example {idx}: "None" must not be mixed with positive labels')
            continue
        value = result[0]
        if not isinstance(value, str):
            errors.append(f"example {idx}: result value must be a string")
        elif value == "None":
            saw_none = True
        else:
            saw_positive = True
        if not isinstance(reason, list) or not all(isinstance(item, str) for item in reason):
            errors.append(f"example {idx}: reason must be a list of strings")

    if examples and not saw_none:
        errors.append('examples must include a ["None"] case')
    if examples and not saw_positive:
        errors.append("examples must include at least one positive non-None case")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-multi-label",
        action="store_true",
        help="Allow examples whose result list contains multiple positive labels",
    )
    parser.add_argument(
        "--max-prompt-tokens",
        type=int,
        default=DEFAULT_MAX_PROMPT_TOKENS,
        help="Maximum allowed prompt token estimate; use 0 to disable",
    )
    parser.add_argument("path", type=Path, help="Path to a prompt JSON file")
    args = parser.parse_args()

    try:
        errors = validate(
            args.path,
            allow_multi_label=args.allow_multi_label,
            max_prompt_tokens=args.max_prompt_tokens,
        )
    except ValueError as exc:
        print(f"FAIL: {args.path}: {exc}", file=sys.stderr)
        return 1

    if errors:
        print(f"FAIL: {args.path}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
