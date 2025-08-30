import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func

# Import the Base class from our new database.py file
from ..database import Base

class VoteType(str, enum.Enum):
    """
    This Python Enum ensures that the 'vote' column in the database
    can only contain these specific string values. It mirrors the
    Pydantic model in the API layer for consistency.
    """
    TRUSTWORTHY = "trustworthy"
    MISLEADING = "misleading"
    NOT_SURE = "not_sure"

class Vote(Base):
    """
    SQLAlchemy ORM model for a user's vote on a piece of content.
    This class will be mapped to a 'votes' table in the database.
    """
    __tablename__ = "votes"

    # Define the columns of the 'votes' table
    id = Column(Integer, primary_key=True, index=True)

    url = Column(String, nullable=False, index=True)

    vote = Column(Enum(VoteType), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<Vote(id={self.id}, url='{self.url[:30]}...', vote='{self.vote.value}')>"
