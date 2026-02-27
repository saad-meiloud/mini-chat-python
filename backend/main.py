from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from contextlib import asynccontextmanager
import os
# 
from database import get_db, init_db, Conversation, Message
from core.response_generator import response_generator
from core.image_analyzer import image_analyzer
from core.gemini_client import get_gemini_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    # Initialize Gemini client
    try:
        gemini_client = get_gemini_client()
        if gemini_client:
            print("✅ Gemini API client initialized successfully")
        else:
            print("⚠️ Warning: Gemini API client not initialized. Check GOOGLE_API_KEY in .env")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize Gemini client: {e}")
    yield
    # Shutdown (if needed)
    pass

app = FastAPI(title="Mini Chatbot API", lifespan=lifespan)

# Serve static files (uploaded images)
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. In production, specify the frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MessageRequest(BaseModel):
    conversation_id: Optional[int] = None
    content: str

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    conversation_id: int
    role: str
    content: str
    image_path: Optional[str] = None
    created_at: datetime

class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

class ChatResponse(BaseModel):
    message: MessageResponse
    conversation: ConversationResponse

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mini Chatbot API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    content: str = Form(...),
    conversation_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint. Processes user message and optional image, returns bot response.
    """
    try:
        # Validate input
        if not content.strip() and not image:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get or create conversation
        if conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(title=content[:50] if content else "Nouvelle conversation")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save user message
        image_path = None
        image_data = None
        
        if image:
            # Save uploaded image
            timestamp = datetime.now().timestamp()
            safe_filename = image.filename.replace(" ", "_") if image.filename else "image"
            image_path = f"{upload_dir}/{conversation.id}_{timestamp}_{safe_filename}"
            
            image_bytes = await image.read()
            
            # Validate image
            if len(image_bytes) == 0:
                raise HTTPException(status_code=400, detail="Image file is empty")
            
            # Check image size (max 20MB for Gemini API)
            if len(image_bytes) > 20 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Image file is too large (max 20MB)")
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            image_data = image_bytes
            print(f"📸 Image uploaded: {image.filename}, size: {len(image_bytes)} bytes")
        
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=content,
            image_path=image_path
        )
        db.add(user_message)
        db.commit()
        
        # Get conversation history for context
        history_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_messages[:-1]  # Exclude current user message
        ]
        
        # Generate bot response
        response_data = response_generator.generate_response(
            user_message=content,
            image_data=image_data,
            conversation_history=history
        )
        
        # Save bot response
        bot_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_data["content"]
        )
        db.add(bot_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(bot_message)
        db.refresh(conversation)
        
        return ChatResponse(
            message=MessageResponse.model_validate(bot_message),
            conversation=ConversationResponse.model_validate(conversation)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/conversations", response_model=List[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    """Get all conversations"""
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    return conversations

@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get a specific conversation"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages for a conversation"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    return messages

@app.put("/api/conversations/{conversation_id}")
def update_conversation(
    conversation_id: int,
    title: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.title = title
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse.model_validate(conversation)

@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete a conversation and all its messages"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete associated images
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    for msg in messages:
        if msg.image_path and os.path.exists(msg.image_path):
            try:
                os.remove(msg.image_path)
            except:
                pass
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}

@app.post("/api/conversations/new")
def create_new_conversation(db: Session = Depends(get_db)):
    """Create a new empty conversation"""
    conversation = Conversation(title="Nouvelle conversation")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ConversationResponse.model_validate(conversation)

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Check if port 8000 is available, if not use 8001
    port = 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result == 0:
        print(f"⚠️ Port {port} est déjà utilisé. Utilisation du port {port + 1}")
        port = 8001
    
    print(f"🚀 Démarrage du serveur sur http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
