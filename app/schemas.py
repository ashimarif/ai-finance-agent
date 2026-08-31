from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    thread_id: str = Field(..., example="user_session_1", description="Unique conversation session ID")
    message: str = Field(..., example="I paid $100 for dinner with Dan and Lee. Split it evenly.", description="User instruction or expense message")

class ChatResponse(BaseModel):
    thread_id: str
    status: str
    response: str