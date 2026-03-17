from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manual_entries = relationship("ManualEntry", back_populates="container")


class ProblemCategory(Base):
    __tablename__ = "problem_categories"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("problem_categories.id"), nullable=True)
    depth = Column(Integer, nullable=False)  # 1=大分類, 2=中分類
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    children = relationship("ProblemCategory", backref="parent", remote_side=[id])
    details = relationship("ProblemDetail", back_populates="category")
    manual_entries = relationship("ManualEntry", back_populates="category")


class ProblemDetail(Base):
    __tablename__ = "problem_details"

    id = Column(Integer, primary_key=True)
    category_id = Column(
        Integer, ForeignKey("problem_categories.id"), nullable=False
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("ProblemCategory", back_populates="details")


class ManualEntry(Base):
    __tablename__ = "manual_entries"

    id = Column(Integer, primary_key=True)
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=False)
    category_id = Column(
        Integer, ForeignKey("problem_categories.id"), nullable=False
    )
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    container = relationship("Container", back_populates="manual_entries")
    category = relationship("ProblemCategory", back_populates="manual_entries")
    templates = relationship("ResponseTemplate", back_populates="manual_entry")


class ResponseTemplate(Base):
    __tablename__ = "response_templates"

    id = Column(Integer, primary_key=True)
    manual_entry_id = Column(
        Integer, ForeignKey("manual_entries.id"), nullable=False
    )
    section_type = Column(
        Enum("investigation", "process", "summary", name="section_type_enum"),
        nullable=False,
    )
    body = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manual_entry = relationship("ManualEntry", back_populates="templates")
    sub_responses = relationship("SubResponse", back_populates="template")


class SubResponse(Base):
    __tablename__ = "sub_responses"

    id = Column(Integer, primary_key=True)
    template_id = Column(
        Integer, ForeignKey("response_templates.id"), nullable=False
    )
    detail_id = Column(
        Integer, ForeignKey("problem_details.id"), nullable=True
    )
    condition_label = Column(String(200), nullable=True)
    position = Column(
        Enum("before", "after", name="position_enum"), nullable=False
    )
    body = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    template = relationship("ResponseTemplate", back_populates="sub_responses")
    detail = relationship("ProblemDetail")


class ResponseHistory(Base):
    __tablename__ = "response_history"

    id = Column(Integer, primary_key=True)
    manual_entry_id = Column(
        Integer, ForeignKey("manual_entries.id"), nullable=False
    )
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=False)
    category_id = Column(
        Integer, ForeignKey("problem_categories.id"), nullable=False
    )
    detail_id = Column(
        Integer, ForeignKey("problem_details.id"), nullable=False
    )
    generated_text = Column(Text, nullable=False)
    edited_text = Column(Text, nullable=True)
    created_by = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    history_subs = relationship("ResponseHistorySub", back_populates="history")


class ResponseHistorySub(Base):
    __tablename__ = "response_history_subs"

    id = Column(Integer, primary_key=True)
    response_history_id = Column(
        Integer, ForeignKey("response_history.id"), nullable=False
    )
    sub_response_id = Column(
        Integer, ForeignKey("sub_responses.id"), nullable=False
    )

    history = relationship("ResponseHistory", back_populates="history_subs")
