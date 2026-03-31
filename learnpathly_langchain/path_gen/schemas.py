from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class ResourceLink(BaseModel):
    """外部资源链接"""
    url: str = Field(description="资源URL地址，支持 GitHub、YouTube、官方文档等")


class SubNode(BaseModel):
    """子学习节点"""
    title: str = Field(description="子节点标题，如 React 组件生命周期、Hooks 进阶等")
    description: str = Field(description="详细描述，包含知识点、原理、实践步骤等，至少80字")
    resources: list[ResourceLink] = Field(default_factory=list, description="支撑该子节点的外部资源链接")


class LearningNode(BaseModel):
    """关键学习节点（整体概览中的一个节点）"""
    title: str = Field(description="关键学习点标题，如 React 基础、状态管理、路由等")
    description: str = Field(description="该学习点的详细介绍，包含核心概念、关键步骤、常见误区等，至少80字")
    sub_nodes: list[SubNode] = Field(default_factory=list, description="该节点下的子学习点列表")
    resources: list[ResourceLink] = Field(default_factory=list, description="支撑该节点的外部资源链接（GitHub仓库、YouTube视频、官方文档等）")


class LearningPathResult(BaseModel):
    """学习路径生成结果"""
    title: str = Field(description="学习路径标题，如 React 全栈学习路径")
    summary: str = Field(description="整体概览，2-3句话介绍整个学习路径的核心内容和学习方法")
    nodes: list[LearningNode] = Field(description="关键学习点列表（整体概览）")


class GenerateRequest(BaseModel):
    """生成学习路径的请求"""
    query: str = Field(description="用户输入，如 我想要学习react 全栈")
