from .schemas import LearningPathOutput


def validate_output(output: LearningPathOutput) -> list[str]:
    warnings: list[str] = []

    if len(output.nodes) < 3:
        warnings.append("学习节点少于 3，建议补充阶段划分。")

    if len(output.nodes) > 8:
        warnings.append("学习节点多于 8，建议合并以增强执行性。")

    for node in output.nodes:
        if not node.resources:
            warnings.append(f"节点 '{node.title}' 没有资源。")

    return warnings
