from pydantic import BaseModel, Field


class DatabaseExceptionDescription(BaseModel):
    connection_issue: str = Field(default="Unable to connect to the database. Please try again later.")
    connection_read_timeout: str = Field(default="Database connection is lost during an operation. Please try again later.")
    query_execution_issue: str = Field(default="Unable to execute the query")

    class config:
        populate_by_name = True
        arbitrary_types_allowed = True

class SourceRelatedPopouts(BaseModel):
    database_connectivity_sources : str = Field(default="Database Connective Issue")
    database_timeout_sources : str = Field(default = "Database Timeout Issue")
    error_sources: str = Field(default="Internal Server Error.")

    class config:
        populate_by_name = True
        arbitrary_types_allowed = True