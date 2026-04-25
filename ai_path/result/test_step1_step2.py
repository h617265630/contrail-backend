"""
Test Step 1 & Step 2 and save results to ai_path/result/
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "ai_path" / ".env")

from ai_path.pipeline import run_step1, run_step2


async def main():
    topic = "LLM 大模型"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = Path(__file__).parent  # ai_path/result/

    print("=" * 70)
    print("STEP 1: 生成大纲")
    print("=" * 70)

    start = time.time()
    step1_result = await run_step1(
        topic=topic,
        level="intermediate",
        learning_depth="standard",
        content_type="mixed",
        practical_ratio="balanced",
        resource_count="standard",
    )
    step1_time = time.time() - start

    outline = step1_result["outline"]

    # 保存 Step 1 结果
    step1_file = result_dir / f"step1_outline_{timestamp}.json"
    with open(step1_file, "w", encoding="utf-8") as f:
        json.dump({
            "topic": outline.topic,
            "level": outline.level,
            "overview": outline.overview,
            "total_duration_hours": outline.total_duration_hours,
            "sections": [s.model_dump() for s in outline.sections],
            "search_results_count": len(step1_result["search_results"]),
            "discovered_urls": step1_result["discovered_urls"],
        }, f, ensure_ascii=False, indent=2)

    print(f"\n耗时: {step1_time:.2f}s")
    print(f"主题: {outline.topic}")
    print(f"章节数: {len(outline.sections)}")
    print(f"结果已保存: {step1_file}")

    print("\n" + "=" * 70)
    print("STEP 2: 展开章节子节点")
    print("=" * 70)

    start = time.time()
    step2_result = await run_step2(
        outline=outline,
        topic=topic,
        level="intermediate",
    )
    step2_time = time.time() - start

    expanded_outline = step2_result["expanded_outline"]

    # 保存 Step 2 结果
    step2_file = result_dir / f"step2_expanded_{timestamp}.json"
    with open(step2_file, "w", encoding="utf-8") as f:
        json.dump({
            "topic": expanded_outline.topic,
            "level": expanded_outline.level,
            "overview": expanded_outline.overview,
            "total_duration_hours": expanded_outline.total_duration_hours,
            "sections": [s.model_dump() for s in expanded_outline.sections],
            "total_sub_nodes": sum(len(s.sub_nodes) for s in expanded_outline.sections),
        }, f, ensure_ascii=False, indent=2)

    print(f"\n耗时: {step2_time:.2f}s")
    print(f"章节数: {len(expanded_outline.sections)}")
    print(f"总子节点数: {sum(len(s.sub_nodes) for s in expanded_outline.sections)}")
    print(f"结果已保存: {step2_file}")

    # 打印汇总
    print("\n" + "=" * 70)
    print("汇总")
    print("=" * 70)
    print(f"Step 1: {step1_time:.2f}s")
    print(f"Step 2: {step2_time:.2f}s")
    print(f"总计: {step1_time + step2_time:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
