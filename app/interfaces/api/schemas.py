from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    user_id: str = "demo"


class ChatResponse(BaseModel):
    trace_id: str
    conversation_id: str
    response: str


class HealthResponse(BaseModel):
    status: str
    environment: str
