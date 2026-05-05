"""
Legal chat endpoints with RAG-based Q&A.
"""
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import text
from backend.auth import get_current_user
from backend.legalai.database import LegalAISession
from backend.legalai.qa_agent import ask_with_rag

router = APIRouter(prefix="/api/legalai/chat", tags=["Legal Chat"])


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    domains: Optional[List[str]] = None


class NewSessionRequest(BaseModel):
    title: Optional[str] = None
    agent_type: str = "qa"


@router.post("/ask")
async def ask_question(req: ChatRequest, current_user=Depends(get_current_user)):
    """Ask a tax/legal question with RAG retrieval."""
    if len(req.question.strip()) < 5:
        raise HTTPException(400, "Câu hỏi quá ngắn")

    result = await ask_with_rag(
        question=req.question,
        session_id=req.session_id,
        domains=req.domains,
    )

    # Persist to chat session if a session_id was provided
    if req.session_id:
        async with LegalAISession() as session:
            # User message
            await session.execute(
                text("""
                    INSERT INTO chat_messages
                        (id, session_id, role, content, citations, model)
                    VALUES
                        (:id, :session_id, 'user', :question, '[]'::jsonb, NULL)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "session_id": req.session_id,
                    "question": req.question,
                },
            )

            # Assistant message
            await session.execute(
                text("""
                    INSERT INTO chat_messages
                        (id, session_id, role, content, citations, model)
                    VALUES
                        (:id, :session_id, 'assistant', :content, :citations::jsonb, :model)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "session_id": req.session_id,
                    "content": result["answer"],
                    "citations": json.dumps(result["citations"]),
                    "model": result.get("model"),
                },
            )

            # Touch session updated_at
            await session.execute(
                text("UPDATE chat_sessions SET updated_at = NOW() WHERE id = :id"),
                {"id": req.session_id},
            )

            await session.commit()

    return result


@router.post("/sessions")
async def create_session(req: NewSessionRequest, current_user=Depends(get_current_user)):
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    async with LegalAISession() as session:
        await session.execute(
            text("""
                INSERT INTO chat_sessions (id, user_email, title, agent_type)
                VALUES (:id, :email, :title, :agent_type)
            """),
            {
                "id": session_id,
                "email": current_user.email,
                "title": req.title or "Tư vấn thuế mới",
                "agent_type": req.agent_type,
            },
        )
        await session.commit()
    return {"session_id": session_id}


@router.get("/sessions")
async def list_sessions(current_user=Depends(get_current_user)):
    """List chat sessions for the current user."""
    async with LegalAISession() as session:
        result = await session.execute(
            text("""
                SELECT id, title, agent_type, created_at, updated_at
                FROM chat_sessions
                WHERE user_email = :email
                ORDER BY updated_at DESC
                LIMIT 50
            """),
            {"email": current_user.email},
        )
        rows = result.mappings().all()
    return {"sessions": [dict(r) for r in rows]}


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str, current_user=Depends(get_current_user)):
    """Get all messages in a session (user must own it)."""
    async with LegalAISession() as session:
        result = await session.execute(
            text("""
                SELECT m.id, m.role, m.content, m.citations, m.model, m.created_at
                FROM chat_messages m
                JOIN chat_sessions s ON s.id = m.session_id
                WHERE m.session_id = :sid AND s.user_email = :email
                ORDER BY m.created_at ASC
            """),
            {"sid": session_id, "email": current_user.email},
        )
        rows = result.mappings().all()
    return {"messages": [dict(r) for r in rows]}
