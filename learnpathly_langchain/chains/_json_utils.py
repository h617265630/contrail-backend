import json
import re


def _strip_think_tags(text: str) -> str:
    return re.sub(r"<think>[\s\S]*?</think>", "", text).strip()


def _raw_decode_first(text: str) -> dict | list | None:
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in ("{", "["):
            try:
                obj, _ = decoder.raw_decode(text, i)
                return obj
            except json.JSONDecodeError:
                continue
    return None


def extract_json(text: str) -> dict | list:
    text = _strip_think_tags(text)
    block = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if block:
        result = _raw_decode_first(block.group(1))
        if result is not None:
            return result
    result = _raw_decode_first(text)
    if result is not None:
        return result
    return json.loads(text.strip())


def unwrap_if_nested(data: dict | list, schema_name: str) -> dict | list:
    if isinstance(data, dict) and list(data.keys()) == [schema_name]:
        return data[schema_name]
    return data
