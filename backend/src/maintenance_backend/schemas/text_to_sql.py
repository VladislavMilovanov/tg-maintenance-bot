"""Pydantic schemas for the Text-to-SQL feature."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TextToSqlRequest(BaseModel):
    """Natural language question to be answered via SQL."""

    question: str = Field(..., min_length=1, description="Natural language question")


class TextToSqlResponse(BaseModel):
    """Result of a natural language database query."""

    answer: str = Field(..., description="Natural language summary of results")
    sql_query: str | None = Field(
        default=None,
        description="The generated SQL query (for transparency)",
    )
    row_count: int = Field(default=0, description="Number of result rows returned")
    columns: list[str] = Field(default_factory=list, description="Column names")
    rows: list[list] = Field(
        default_factory=list,
        description="Result data: list of rows, each row is a list of values",
    )
    error: str | None = Field(
        default=None,
        description="Error message if the query could not be completed",
    )
