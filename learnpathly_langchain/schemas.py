from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Intent(BaseModel):
    goal: str = Field(description="Learning goal")
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    focus: list[str] = Field(default_factory=list)
    language: str = "zh"
    time_budget: str = ""


class Resource(BaseModel):
    type: Literal["github", "youtube", "official_doc", "article", "course"]
    title: str
    url: HttpUrl
    description: str = ""
    source_score: float = 0.0


class LearningSubNode(BaseModel):
    """子节点 - 对应模版中的 0.1, 1.1 等"""
    order_code: str = Field(description="编号，如 0.1, 1.1")
    title: str
    description: str = ""
    learning_points: list[str] = Field(default_factory=list, description="学习重点列表")
    resources: list[Resource] = Field(default_factory=list)


class LearningNode(BaseModel):
    """主节点 - 对应模版中的 0, 1, 2 等阶段"""
    order_code: str = Field(description="编号，如 0, 1, 2")
    title: str
    description: str = ""
    key_points: list[str] = Field(default_factory=list, description="核心知识列表")
    subnodes: list[LearningSubNode] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)


class LearningPhase(BaseModel):
    """推荐学习阶段"""
    phase: str = Field(description="阶段名称，如 第1阶段")
    duration: str = Field(description="建议时长，如 2周")
    nodes: list[str] = Field(default_factory=list, description="该阶段包含的节点编号")


class AbilityModel(BaseModel):
    """能力模型"""
    category: str = Field(description="能力分类，如 前端能力")
    skills: list[str] = Field(default_factory=list)


class TutorialSnippet(BaseModel):
    title: str = ""
    language: str = ""
    snippet: str = ""
    source_url: str = ""


class TutorialContext(BaseModel):
    """教程研究上下文"""
    query: str = ""
    key_knowledge: list[str] = Field(default_factory=list, description="具体的技术知识点，如 LLM、RAG、LangChain、Prompt Engineering")
    suggested_nodes: list[str] = Field(default_factory=list, description="建议的主节点名称，如 LLM基础、RAG应用、LangChain开发")
    subnode_titles: dict[str, list[str]] = Field(default_factory=dict, description="每个主节点下的具体子节点技术名称，key是主节点名")
    code_snippets: list[TutorialSnippet] = Field(default_factory=list)
    reference_links: list[str] = Field(default_factory=list)


class LearningPathOutput(BaseModel):
    """最终输出结构"""
    title: str = Field(description="学习路径标题")
    description: str = Field(description="路径描述")
    nodes: list[LearningNode] = Field(description="所有学习节点")
    learning_phases: list[LearningPhase] = Field(default_factory=list, description="推荐学习阶段顺序")
    ability_model: list[AbilityModel] = Field(default_factory=list, description="能力模型")
    recommendations: list[str] = Field(default_factory=list, description="针对用户情况的建议")


class LearningPathRequest(BaseModel):
    query: str


class LearningPathResponse(BaseModel):
    data: LearningPathOutput
    warnings: list[str] = Field(default_factory=list)
