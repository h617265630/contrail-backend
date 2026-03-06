"""项目逻辑说明：learningpath

这个模块用于描述 learningpath 项目的产品逻辑（非实现细节）。
目标是：便于阅读、便于协作沟通；同时也可以被代码 import，用结构化数据表达项目规则。
"""

from __future__ import annotations

import json
from typing import Any, Dict


PROJECT_LOGIC: Dict[str, Any] = {
    "project": {
        "name": "learningpath",
        "purpose": "用户用来建立自己的学习路径，追踪学习进度，最终达成框架式学习的目的。",
        "core_concepts": {
            "learningpath": "一个框架式/路径式学习计划，由步骤与资源组成。",
            "resource": "学习资源的引用（常见为外部链接）。",
            "progress": "用户对学习路径的学习进度追踪（如：已完成/进行中等）。",
        },
        "data_visibility": {
            "public": {
                "definition": "数据库里标记为 public 的数据，所有用户可见（公共数据）。",
                "scope": "首页与 Resources 页面展示的数据来源。",
            },
            "private": {
                "definition": "用户个人拥有/收藏/创建的数据，只对当前用户可见。",
                "scope": "用户管理页（MyResource / MyLearningPath）以及学习进度追踪。",
            },
        },
    },
    "feature_logic": {
        "create_resource_by_external_link": {
            "description": "用户可以通过添加外部链接，创建属于自己的资源（resource）。",
            "inputs": [
                "url",
                "title（可选）",
                "category/tags（可选）",
                "notes（可选）",
            ],
            "output": "生成一条由用户拥有的 Resource（通常默认为私有数据）。",
        },
        "home_public_learningpaths": {
            "description": "首页根据 learningpath 的分类与具体需求，展示数据库中所有 public 的 learningpath（公共数据）。",
            "data_source": "LearningPath where is_public=True（公共区）",
            "filter_keys": ["category", "needs/requirements"],
        },
        "resources_public_resources": {
            "description": "Resources 页面根据分类与具体需求，展示数据库中所有 public 的 resources（公共数据）。",
            "data_source": "Resource where is_public=True（公共区）",
            "filter_keys": ["category", "needs/requirements"],
        },
        "user_management": {
            "description": "用户管理页面：管理用户自己的资源/学习路径，以及与公共区交互形成的收藏数据。",
            "pages": {
                "myresource": {
                    "description": "对应用户自己添加的 resource：包含从 Resources 公共页面添加的收藏，以及通过 Add Resource 外链创建的数据。",
                    "data_source": "UserResource（当前用户拥有/收藏）",
                    "requires_auth": True,
                },
                "my_learningpath": {
                    "description": "对应用户自己创建的 learningpath，以及从公共区添加/收藏的所有 learningpath。",
                    "data_source": "UserLearningPath（当前用户创建/收藏）",
                    "requires_auth": True,
                },
            },
        },
        "progress_tracking": {
            "description": "用户对自己的学习路径进行进度追踪（仅与用户身份相关，属于私有数据）。",
            "requires_auth": True,
            "scope": {
                "applies_to": "用户已创建/收藏的 LearningPath（UserLearningPath）",
                "data_visibility": "private",
            },
            "capabilities": {
                "mark_step_complete": {
                    "description": "在 learningpath 详情中对单个步骤/条目进行完成勾选或取消勾选。",
                    "inputs": ["learningpath_id", "step_id", "is_complete"],
                    "side_effects": ["更新该用户的 step 完成状态", "可能触发整体进度百分比重新计算"],
                },
                "mark_phase_complete": {
                    "description": "当 learningpath 设计了阶段（phase/milestone）时，允许对阶段进行完成标记。",
                    "inputs": ["learningpath_id", "phase_id", "is_complete"],
                },
                "progress_summary": {
                    "description": "提供学习路径进度汇总（例如：完成百分比、已完成步骤数、最后学习时间）。",
                    "outputs": ["completed_steps", "total_steps", "percent", "last_activity_at"],
                },
            },
        },
    },
    "page_logic": {
        "home": {
            "goal": "发现与浏览公共 LearningPath。",
            "shows": "所有 public 的 LearningPath（公共数据）",
            "query": "LearningPath where is_public=True",
            "filters": ["category", "needs/requirements"],
        },
        "resources": {
            "goal": "发现与浏览公共 Resources。",
            "shows": "所有 public 的 Resource（公共数据）",
            "query": "Resource where is_public=True",
            "filters": ["category", "needs/requirements"],
        },
        "learningpath_detail": {
            "goal": "展示学习路径详情；对已添加到个人区的 learningpath 支持进度追踪操作。",
            "shows": ["LearningPath 详情", "步骤/资源列表", "（可选）阶段/里程碑"],
            "public_view": {
                "description": "当浏览公共区 learningpath 时，仅展示内容本身，不展示或写入用户进度。",
                "data_source": "LearningPath where is_public=True",
            },
            "user_view": {
                "description": "当该 learningpath 已在用户区（创建/收藏）时，允许展示并更新用户进度。",
                "requires_auth": True,
                "data_source": ["UserLearningPath（当前用户）", "Progress（当前用户）"],
                "actions": ["mark_step_complete", "mark_phase_complete"],
            },
        },
        "user_management": {
            "goal": "管理用户个人数据（资源/学习路径/进度）。",
            "requires_auth": True,
            "subpages": {
                "myresource": {
                    "shows": "当前用户的资源（创建/收藏）",
                    "includes": [
                        "从公共 Resources 收藏",
                        "通过 Add Resource 外链创建",
                    ],
                },
                "my_learningpath": {
                    "shows": "当前用户的学习路径（创建/收藏）",
                    "includes": ["用户创建", "从公共 LearningPaths 收藏"],
                },
                "progress": {
                    "shows": "当前用户所有学习路径的进度汇总（面板/列表）。",
                    "requires_auth": True,
                    "data_source": ["UserLearningPath（当前用户）", "Progress（当前用户）"],
                    "filters": ["category", "status（进行中/已完成）"],
                },
                "stats": {
                    "shows": "当前用户的学习统计（可选）。",
                    "requires_auth": True,
                    "metrics": ["已完成学习路径数", "总完成步骤数", "连续学习天数（可选）"],
                },
            },
        },
    },
}


def get_project_logic() -> Dict[str, Any]:
    return PROJECT_LOGIC


def main() -> None:
    print(json.dumps(PROJECT_LOGIC, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
