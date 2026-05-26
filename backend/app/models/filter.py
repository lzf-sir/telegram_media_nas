"""
Filter Rule Model - Advanced filtering system
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy import Enum as SQLEnum
import enum

from app.database import Base


class FilterOperator(str, enum.Enum):
    """Filter operator enum"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"
    BETWEEN = "between"


class FilterCondition(Base):
    """Single filter condition"""

    __tablename__ = "filter_conditions"

    id = Column(Integer, primary_key=True, index=True)

    # Condition info
    field = Column(String, nullable=False)  # e.g., "file_size", "media_type", "caption", "date"
    operator = Column(SQLEnum(FilterOperator), nullable=False)
    value = Column(JSON, nullable=True)  # Can be string, number, list, etc.
    value2 = Column(JSON, nullable=True)  # For "between" operator

    # Grouping
    filter_group_id = Column(Integer, ForeignKey("filter_groups.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FilterGroup(Base):
    """Filter group - combines multiple conditions with AND/OR logic"""

    __tablename__ = "filter_groups"

    id = Column(Integer, primary_key=True, index=True)

    # Group info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Logic - how to combine conditions
    logic = Column(String, default="AND")  # "AND" or "OR"

    # Conditions (relationship)
    conditions = relationship("FilterCondition", backref="group", cascade="all, delete-orphan")

    # Preset filters
    is_preset = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "logic": self.logic,
            "conditions": [c.to_dict() for c in self.conditions] if self.conditions else [],
            "is_preset": self.is_preset,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
