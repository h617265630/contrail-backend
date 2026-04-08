#根据以下字段生成clip的模型：id，title,description,clip_path, from_video_id,start_time,end_time,clip_duration,clip_method,generated_by,createdtime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.path_item import PathItem
from app.models.resource import ResourceType,Resource

class Clip(Resource):
    __tablename__ = "clips"
    id = Column(Integer, ForeignKey('resources.id'), primary_key=True)
    start_time = Column(Float, nullable=False)  # in seconds
    end_time = Column(Float, nullable=False)    # in seconds
    clip_duration = Column(Float, nullable=False)  # in seconds
    clip_method = Column(String(50), nullable=False)  # e.g., 'manual', 'automatic'
    generated_by = Column(String(50), nullable=True)
    # key
    source_video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    
    #relationships
    # 存在继承（Resource）导致的多路径，明确使用 source_video_id 作为外键
    video = relationship(
        "Video",
        backref="clips",
        foreign_keys=[source_video_id],
        primaryjoin="Clip.source_video_id == Video.id",
    )
    
    # 多态配置
    __mapper_args__ = {
        'polymorphic_identity': ResourceType.CLIP,
    }
    def __repr__(self):
        return f"<Clip(id={self.id}, source_video_id='{self.source_video_id}')>"