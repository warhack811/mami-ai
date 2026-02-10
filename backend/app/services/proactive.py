import asyncio
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.connection_manager import manager
from app.models.user import User

async def proactive_loop():
    """
    Background loop to check for nudge opportunities.
    """
    print("Starting Proactive Nudge Loop...")
    while True:
        try:
            now = datetime.datetime.now()

            # 1. Simple Daily Greeting (Example logic)
            # In production, check DB for last_interaction time.
            if now.hour == 9 and now.minute == 0:
                await broadcast_nudge("Good morning! Ready to conquer the day?")

            # 2. Check Goals (Placeholder)
            # goals = db.query(Goal).filter(Goal.due_date <= now).all()
            # for goal in goals: ...

            await asyncio.sleep(60) # Check every minute
        except Exception as e:
            print(f"Proactive Loop Error: {e}")
            await asyncio.sleep(60)

async def broadcast_nudge(message: str):
    # Send to all connected desktops (or specific users)
    # This is a broadcast for prototype simplicity.
    for client_id in manager.active_connections:
        await manager.send_command(client_id, "nudge", {"message": message})
