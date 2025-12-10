from sqlalchemy.orm import Session
from ..models.content import TextbookChapter, ChapterProgress
from ..models.user import StudentProfile
from typing import List, Optional
from datetime import datetime
import uuid

class ChapterService:
    """Service class for managing textbook chapters and related operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_chapter(self,
                      title: str,
                      slug: str,
                      content: str,
                      learning_outcomes: List[str],
                      chapter_number: int,
                      diagrams: Optional[List[str]] = None,
                      code_examples: Optional[List[str]] = None,
                      exercises: Optional[List[str]] = None,
                      prerequisites: Optional[List[uuid.UUID]] = None,
                      status: str = 'draft') -> TextbookChapter:
        """Create a new textbook chapter."""
        chapter = TextbookChapter(
            title=title,
            slug=slug,
            content=content,
            learning_outcomes=learning_outcomes,
            diagrams=diagrams or [],
            code_examples=code_examples or [],
            exercises=exercises or [],
            chapter_number=chapter_number,
            prerequisites=prerequisites or [],
            status=status
        )
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)
        return chapter

    def get_chapter_by_id(self, chapter_id: uuid.UUID) -> Optional[TextbookChapter]:
        """Get a chapter by its ID."""
        return self.db.query(TextbookChapter).filter(TextbookChapter.id == chapter_id).first()

    def get_chapter_by_slug(self, slug: str) -> Optional[TextbookChapter]:
        """Get a chapter by its slug."""
        return self.db.query(TextbookChapter).filter(TextbookChapter.slug == slug).first()

    def get_all_chapters(self, status: Optional[str] = None) -> List[TextbookChapter]:
        """Get all chapters, optionally filtered by status."""
        query = self.db.query(TextbookChapter)
        if status:
            query = query.filter(TextbookChapter.status == status)
        return query.order_by(TextbookChapter.chapter_number).all()

    def update_chapter_progress(self,
                               student_id: uuid.UUID,
                               chapter_id: uuid.UUID,
                               completion_percentage: float,
                               exercises_completed: Optional[List[str]] = None,
                               time_spent_seconds: Optional[int] = None) -> ChapterProgress:
        """Update or create chapter progress for a student."""
        progress = self.db.query(ChapterProgress).filter(
            ChapterProgress.student_id == student_id,
            ChapterProgress.chapter_id == chapter_id
        ).first()

        if progress:
            # Update existing progress
            progress.completion_percentage = completion_percentage
            progress.exercises_completed = exercises_completed or progress.exercises_completed
            progress.time_spent_seconds = time_spent_seconds or progress.time_spent_seconds
            progress.last_accessed = datetime.utcnow()
        else:
            # Create new progress record
            progress = ChapterProgress(
                student_id=student_id,
                chapter_id=chapter_id,
                completion_percentage=completion_percentage,
                exercises_completed=exercises_completed or [],
                time_spent_seconds=time_spent_seconds
            )
            self.db.add(progress)

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_student_progress(self, student_id: uuid.UUID) -> List[ChapterProgress]:
        """Get all chapter progress for a specific student."""
        return self.db.query(ChapterProgress).filter(
            ChapterProgress.student_id == student_id
        ).all()

    def get_chapter_progress(self, chapter_id: uuid.UUID) -> List[ChapterProgress]:
        """Get all progress records for a specific chapter."""
        return self.db.query(ChapterProgress).filter(
            ChapterProgress.chapter_id == chapter_id
        ).all()