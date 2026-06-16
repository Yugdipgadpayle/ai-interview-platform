"""Interview session and answer endpoints."""

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_current_user, get_interview_repository, get_interview_service
from app.models.user import User
from app.repositories.interview_repository import InterviewRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.interview import AnswerRead, AnswerSubmit, InterviewCreate, InterviewRead
from app.services.interview_service import InterviewService

router = APIRouter()


@router.post("", response_model=InterviewRead, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: InterviewCreate,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    return await service.create_session(current_user.id, payload)


@router.get("", response_model=PaginatedResponse[InterviewRead])
async def list_interviews(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    repo: InterviewRepository = Depends(get_interview_repository),
):
    pagination = PaginationParams(page=page, size=size)
    items, total = await repo.list_sessions(current_user.id, pagination.offset, pagination.size)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{session_id}", response_model=InterviewRead)
async def get_interview(
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    return await service.get_session(session_id, current_user.id)


@router.post("/questions/{question_id}/answers", response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    question_id: int,
    payload: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    return await service.submit_answer(current_user.id, question_id, payload)
