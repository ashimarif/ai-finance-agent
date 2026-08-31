from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from app.schemas import ChatRequest, ChatResponse
from app.agent import agent_app
from app.database import init_db

# Ensure tables are initialized on startup
init_db()

app = FastAPI(
    title="Smart Finance & Bill-Splitting Agent API",
    version="1.0.0",
    description="Agentic AI system for managing personal expenses, group bill splits, and IOUs with PostgreSQL."
)

def extract_text_content(content) -> str:
    """Helper to safely extract string text from string or list format."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Extract text from block format [{'type': 'text', 'text': '...'}]
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        return "\n".join(text_parts)
    return str(content)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "finance-agent-engine"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        config = {"configurable": {"thread_id": req.thread_id}}
        user_input = {"messages": [HumanMessage(content=req.message)]}
        
        # Execute the agent workflow
        result = agent_app.invoke(user_input, config=config)
        
        # Get the final AI response and extract clean text
        final_message = result["messages"][-1]
        text_response = extract_text_content(final_message.content)
        
        return ChatResponse(
            thread_id=req.thread_id,
            status="success",
            response=text_response
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))