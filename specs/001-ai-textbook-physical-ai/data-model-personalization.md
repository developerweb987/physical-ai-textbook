# Data Model: Personalization Features for AI-Native Textbook

**Feature**: AI-Native Textbook for Physical AI & Humanoid Robotics
**Date**: 2025-12-10
**Modeler**: AI Assistant

## Entity: StudentProfile

**Purpose**: Store user background information and learning preferences for personalization

**Fields**:
- **id**: UUID (primary key, required) - Unique identifier for the student profile
- **user_id**: UUID (foreign key to User, required) - Reference to the authenticated user
- **technical_background**: String (enum: "beginner", "intermediate", "advanced", "expert", required) - Student's technical experience level
- **field_of_study**: String (enum: "engineering", "computer_science", "robotics", "other", required) - Primary field of study
- **learning_goals**: Array of strings (required) - Student's learning objectives (e.g., "academic", "professional", "hobby")
- **current_knowledge_level**: String (enum: "novice", "familiar", "proficient", "expert", required) - Current understanding of Physical AI concepts
- **learning_preferences**: Array of strings (required) - Preferred learning styles (e.g., "visual", "hands_on", "theoretical", "practical")
- **language_preferences**: Array of strings (required) - Preferred languages (e.g., "en", "ur", "es", etc.)
- **accessibility_needs**: Array of strings (optional) - Any accessibility requirements (e.g., "high_contrast", "larger_text", "audio")
- **chapter_preferences**: Array of UUIDs (optional) - Preferred chapter topics or interests
- **recommended_chapters**: Array of UUIDs (optional) - Chapters recommended based on profile
- **learning_history**: JSON object (optional) - Track progress and completed chapters
- **personalization_enabled**: Boolean (default: true) - Whether personalization is enabled for this user
- **created_at**: DateTime (required) - When the profile was created
- **updated_at**: DateTime (required) - When the profile was last updated
- **data_retention_until**: DateTime (required) - When data should be deleted per retention policy

**Validation Rules**:
- technical_background must be one of the allowed enum values
- field_of_study must be one of the allowed enum values
- current_knowledge_level must be one of the allowed enum values
- learning_preferences must contain at least one valid value
- language_preferences must contain at least "en" as default
- data_retention_until must be set to 2 years from creation

**Relationships**:
- One-to-one with User model
- One-to-many with PersonalizationLog (tracking personalization decisions)
- Many-to-many with TextbookChapter through recommendations

## Entity: PersonalizationLog

**Purpose**: Track personalization decisions and recommendations for analysis and improvement

**Fields**:
- **id**: UUID (primary key, required) - Unique identifier for the log entry
- **student_profile_id**: UUID (foreign key to StudentProfile, required) - Reference to the student profile
- **chapter_id**: UUID (foreign key to TextbookChapter, required) - Chapter that was recommended or adapted
- **recommendation_type**: String (enum: "chapter_recommendation", "content_adaptation", "difficulty_adjustment", required) - Type of personalization
- **reasoning**: String (required) - Explanation for why this recommendation was made
- **confidence_score**: Float (0.0-1.0, required) - Confidence in the recommendation
- **was_accepted**: Boolean (required) - Whether the user accepted/used the recommendation
- **timestamp**: DateTime (required) - When the recommendation was made
- **created_at**: DateTime (required) - When the log entry was created

**Validation Rules**:
- recommendation_type must be one of the allowed enum values
- confidence_score must be between 0.0 and 1.0
- timestamp should not be in the future

**Relationships**:
- Many-to-one with StudentProfile
- Many-to-one with TextbookChapter

## Entity: ChapterRecommendation

**Purpose**: Store specific chapter recommendations for users based on their profiles

**Fields**:
- **id**: UUID (primary key, required) - Unique identifier for the recommendation
- **student_profile_id**: UUID (foreign key to StudentProfile, required) - Reference to the student profile
- **chapter_id**: UUID (foreign key to TextbookChapter, required) - Chapter being recommended
- **recommendation_score**: Float (0.0-1.0, required) - Score indicating relevance to user profile
- **reasons**: Array of strings (required) - Reasons for the recommendation (e.g., "prerequisite", "based_on_interests", "difficulty_match")
- **priority**: Integer (1-5, required) - Priority level of the recommendation (1=highest, 5=lowest)
- **is_active**: Boolean (default: true, required) - Whether the recommendation is currently active
- **expires_at**: DateTime (optional) - When the recommendation expires
- **created_at**: DateTime (required) - When the recommendation was created
- **updated_at**: DateTime (required) - When the recommendation was last updated

**Validation Rules**:
- recommendation_score must be between 0.0 and 1.0
- priority must be between 1 and 5
- expires_at should be in the future if specified

**Relationships**:
- Many-to-one with StudentProfile
- Many-to-one with TextbookChapter

## Entity: ContentAdaptation

**Purpose**: Store content adaptations for personalized learning experiences

**Fields**:
- **id**: UUID (primary key, required) - Unique identifier for the adaptation
- **student_profile_id**: UUID (foreign key to StudentProfile, required) - Reference to the student profile
- **chapter_id**: UUID (foreign key to TextbookChapter, required) - Chapter being adapted
- **content_element**: String (enum: "text", "diagram", "code", "exercise", "example", required) - Type of content being adapted
- **adaptation_type**: String (enum: "simplified", "expanded", "visual", "hands_on", "theoretical", required) - Type of adaptation
- **adapted_content**: Text (required) - The adapted content
- **original_content_ref**: String (required) - Reference to original content for tracking
- **confidence_score**: Float (0.0-1.0, required) - Confidence in the adaptation quality
- **is_active**: Boolean (default: true, required) - Whether the adaptation is currently active
- **created_at**: DateTime (required) - When the adaptation was created
- **updated_at**: DateTime (required) - When the adaptation was last updated

**Validation Rules**:
- adaptation_type must be one of the allowed enum values
- content_element must be one of the allowed enum values
- confidence_score must be between 0.0 and 1.0

**Relationships**:
- Many-to-one with StudentProfile
- Many-to-one with TextbookChapter

## Entity: TranslationCache

**Purpose**: Cache translated content to improve performance for multilingual features

**Fields**:
- **id**: UUID (primary key, required) - Unique identifier for the cache entry
- **original_content_id**: String (required) - Reference to original content (could be chapter, section, etc.)
- **target_language**: String (required) - Language code for translation (e.g., "ur", "es", "fr")
- **translated_content**: Text (required) - The translated content
- **translation_provider**: String (default: "openai", required) - Provider used for translation
- **cache_expires_at**: DateTime (required) - When the cached translation expires
- **created_at**: DateTime (required) - When the cache entry was created
- **updated_at**: DateTime (required) - When the cache entry was last updated

**Validation Rules**:
- target_language must be a valid language code
- cache_expires_at must be in the future

**Relationships**:
- No direct relationships, but references various content types through original_content_id