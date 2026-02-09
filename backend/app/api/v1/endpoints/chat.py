from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.agents.graph import app_graph
from app.models.user import User, Chat, Message
from app.schemas.user import UserOut # Assuming we create this later or mock it
from langchain_core.messages import HumanMessage, AIMessage
import json

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    message: str,
    user_id: int = 1, # Placeholder for auth dependency
    db: Session = Depends(get_db)
):
    # Ensure user exists (Demo only)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, email="demo@mami.ai", hashed_password="hashed_secret", full_name="Demo User")
        db.add(user)
        db.commit()

    # Ensure chat exists
    chat = db.query(Chat).filter(Chat.id == 1).first()
    if not chat:
        chat = Chat(id=1, title="General", owner_id=user_id)
        db.add(chat)
        db.commit()

    # Log user message
    user_msg = Message(chat_id=1, role="user", content=message) # Hardcoded chat_id 1
    db.add(user_msg)
    db.commit()

    # Retrieve recent history
    history = db.query(Message).filter(Message.chat_id == 1).order_by(desc(Message.created_at)).limit(10).all()
    history = history[::-1] # Reverse to chronological order

    messages = []
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))

    # Run Agent Graph
    # Add current message if not in history yet (it should be since we just added it)
    # But wait, we query limit 10. If history is long, we get last 10.
    # The last one should be the current message.

    # Actually, we should check if history includes the current message.
    # Since we commit before query, it should include it.

    inputs = {"messages": messages, "user_id": user_id, "next_step": "", "context": ""}
    result = await app_graph.ainvoke(inputs)

    final_response = result["messages"][-1].content

    # Log assistant response
    assistant_msg = Message(chat_id=1, role="assistant", content=final_response)
    db.add(assistant_msg)
    db.commit()

    return {"response": final_response}

# WebSocket for Desktop Client
@router.websocket("/ws/desktop/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process command result from desktop
            print(f"Received from desktop {client_id}: {data}")
            # Identify if it's a heartbeat or a command result

            # Echo for now or send proactive command
            await websocket.send_text(f"Server received: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
