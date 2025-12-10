# Data Model: AI-Native Textbook for Physical AI & Humanoid Robotics

## Entities

### Textbook Chapter
- **id**: UUID (primary key)
- **title**: String (required)
- **slug**: String (required, unique, URL-friendly)
- **content**: Markdown text (required)
- **learning_outcomes**: Array of strings (required)
- **diagrams**: Array of diagram references (optional)
- **code_examples**: Array of code blocks (optional)
- **exercises**: Array of exercise objects (optional)
- **chapter_number**: Integer (required, unique per textbook)
- **prerequisites**: Array of chapter IDs (optional)
- **created_at**: DateTime (required)
- **updated_at**: DateTime (required)
- **status**: Enum ['draft', 'review', 'published'] (required, default: 'draft')

### Student Profile
- **id**: UUID (primary key)
- **email**: String (required, unique)
- **name**: String (optional)
- **background**: String (optional, student's technical background)
- **learning_preferences**: JSON object (optional)
- **personalization_settings**: JSON object (optional)
- **chapter_progress**: Array of progress objects (optional)
- **created_at**: DateTime (required)
- **updated_at**: DateTime (required)
- **last_active**: DateTime (optional)
- **data_retention_until**: DateTime (required, 2 years from last activity)

### Chapter Progress
- **id**: UUID (primary key)
- **student_id**: UUID (foreign key to Student Profile)
- **chapter_id**: UUID (foreign key to Textbook Chapter)
- **completion_percentage**: Float (0-100)
- **time_spent_seconds**: Integer (optional)
- **last_accessed**: DateTime (optional)
- **exercises_completed**: Array of exercise IDs (optional)
- **created_at**: DateTime (required)
- **updated_at**: DateTime (required)

### Chatbot Interaction
- **id**: UUID (primary key)
- **student_id**: UUID (foreign key to Student Profile, nullable for anonymous)
- **query**: String (required)
- **response**: String (required)
- **context_mode**: Enum ['global', 'selected_text'] (required)
- **selected_text**: String (optional, for selected_text mode)
- **timestamp**: DateTime (required)
- **response_time_ms**: Integer (optional)
- **accuracy_score**: Float (0-1, optional, for quality tracking)

### Agent Skill
- **id**: UUID (primary key)
- **name**: String (required)
- **description**: String (optional)
- **skill_type**: Enum ['content_retrieval', 'explanation', 'exercise_help', 'personalization'] (required)
- **implementation**: String (required, code or configuration)
- **applicable_chapters**: Array of chapter IDs (optional)
- **created_at**: DateTime (required)
- **updated_at**: DateTime (required)
- **is_active**: Boolean (required, default: true)

## Relationships
- Student Profile (1) → (M) Chapter Progress
- Textbook Chapter (1) → (M) Chapter Progress
- Student Profile (0..1) → (M) Chatbot Interaction
- Agent Skill (1) → (M) Chapters (through applicable_chapters array)

## Validation Rules
- Chapter numbers must be unique within a textbook
- Email addresses must be valid format
- Completion percentage must be between 0 and 100
- Response time must be positive
- Accuracy score must be between 0 and 1
- Student data must be automatically deleted after retention period

## State Transitions
- Textbook Chapter: draft → review → published
- Agent Skill: inactive → active → inactive