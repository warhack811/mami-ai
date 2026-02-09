import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.agents.graph import app_graph
from app.models.user import User, Chat, Message
from app.services.memory import consolidate_memory_task
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()

async def stream_graph_response(inputs: dict, user_id: int, db: Session, chat_id: int):
    """
    Generator that yields SSE events from the LangGraph execution.
    """
    full_response = ""

    # We use astream to get updates from the graph
    # We are interested in the 'messages' key from the last node
    async for event in app_graph.astream_events(inputs, version="v1"):
        kind = event["event"]

        # Stream token generation from LLMs
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                full_response += content
                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

        # Notify when a tool is called
        elif kind == "on_tool_start":
            tool_name = event["name"]
            yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name})}\n\n"

        elif kind == "on_tool_end":
             yield f"data: {json.dumps({'type': 'tool_end', 'output': str(event['data'].get('output'))})}\n\n"

    # Once stream is done, save the full response
    if full_response:
        assistant_msg = Message(chat_id=chat_id, role="assistant", content=full_response)
        db.add(assistant_msg)
        db.commit()

        # Trigger Memory Consolidation via Celery
        consolidate_memory_task.delay(user_id, f"User: ...\nAssistant: {full_response}")

    yield "data: [DONE]\n\n"

@router.post("/chat/stream")
async def chat_stream_endpoint(
    message: str,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    # Ensure user/chat exists (Same logic as before)
    chat = db.query(Chat).filter(Chat.id == 1).first()
    if not chat:
        chat = Chat(id=1, title="General", owner_id=user_id)
        db.add(chat)
        db.commit()

    # Log user message
    user_msg = Message(chat_id=1, role="user", content=message)
    db.add(user_msg)
    db.commit()

    # Retrieve history
    history = db.query(Message).filter(Message.chat_id == 1).order_by(desc(Message.created_at)).limit(10).all()
    history = history[::-1]

    messages = []
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    inputs = {"messages": messages, "user_id": user_id, "next_step": "", "context": ""}

    return StreamingResponse(
        stream_graph_response(inputs, user_id, db, 1),
        media_type="text/event-stream"
    )

# WebSocket for Desktop Client (Keep existing)
@router.websocket("/ws/desktop/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from desktop {client_id}: {data}")
            await websocket.send_text(f"Server received: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
