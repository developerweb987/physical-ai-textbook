# Quickstart Guide: Personalization Features for AI-Native Textbook

## Prerequisites

- Node.js 18+ for Docusaurus
- Python 3.11+ for backend services
- PostgreSQL 12+ for user data storage
- Redis for session management (optional but recommended)
- OpenAI API key (for translation and personalization logic)

## Setup

### 1. Environment Configuration

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Update the following variables in backend/.env:
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL="postgresql://username:password@localhost:5432/ai_textbook"
REDIS_URL="redis://localhost:6379"
PERSONALIZATION_ENABLED=true
```

### 2. Database Setup

```bash
# Run database migrations
cd backend
python -m alembic upgrade head
```

### 3. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ai-textbook-web
npm install
```

## Configuration

### 1. Personalization Settings

```bash
# Configure personalization in backend/settings/personalization.py
MAX_RECOMMENDATIONS = 10
RECOMMENDATION_CACHE_TTL = 3600  # 1 hour
TRANSLATION_CACHE_TTL = 86400    # 24 hours
DATA_RETENTION_YEARS = 2
```

### 2. User Profile Initialization

```bash
# Initialize default user profile schema
cd backend
python -c "
from api.models.user import StudentProfile
from api.database import get_db
from sqlalchemy.orm import Session

db: Session = next(get_db())
# Schema is created automatically via Alembic migrations
print('Student profile schema initialized')
"
```

## API Usage Examples

### 1. Create/Update User Profile

```bash
curl -X POST http://localhost:8000/api/v1/personalization/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "technical_background": "intermediate",
    "field_of_study": "robotics",
    "learning_goals": ["professional"],
    "current_knowledge_level": "familiar",
    "learning_preferences": ["hands_on", "visual"],
    "language_preferences": ["en", "ur"]
  }'
```

### 2. Get Personalized Recommendations

```bash
curl -X GET "http://localhost:8000/api/v1/personalization/recommendations?limit=5" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

### 3. Get Personalized Content Adaptations

```bash
curl -X GET "http://localhost:8000/api/v1/personalization/content/CHAPTER_ID_HERE" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

### 4. Request Content Translation

```bash
curl -X POST http://localhost:8000/api/v1/personalization/translation \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "content": "Physical AI combines principles of physics with artificial intelligence to create robots that can interact with the physical world.",
    "target_language": "ur",
    "content_type": "text"
  }'
```

## Frontend Integration

### 1. Personalization Components

```javascript
// Initialize the personalization with API configuration
const personalization = new PersonalizationInterface({
  apiUrl: 'http://localhost:8000/api/v1',
  authToken: 'user_auth_token'
});

// Get personalized recommendations
const recommendations = await personalization.getRecommendations();

// Update user profile
const profile = await personalization.updateProfile({
  technical_background: 'intermediate',
  learning_preferences: ['visual', 'hands_on']
});
```

### 2. Translation Features

```javascript
// Initialize translation functionality
const translator = new TranslationService({
  apiUrl: 'http://localhost:8000/api/v1',
  authToken: 'user_auth_token'
});

// Translate content to Urdu
const translated = await translator.translate(
  'Physical AI concepts explained in detail',
  'ur'
);
```

## Testing the Personalization Features

### 1. Profile Management

```bash
# 1. Create a user profile
curl -X POST http://localhost:8000/api/v1/personalization/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TEST_TOKEN" \
  -d '{"technical_background":"intermediate","field_of_study":"robotics","learning_goals":["academic"],"current_knowledge_level":"familiar","learning_preferences":["hands_on"],"language_preferences":["en","ur"]}'

# 2. Verify profile was created
curl -X GET http://localhost:8000/api/v1/personalization/profile \
  -H "Authorization: Bearer TEST_TOKEN"

# 3. Get recommendations based on profile
curl -X GET http://localhost:8000/api/v1/personalization/recommendations \
  -H "Authorization: Bearer TEST_TOKEN"
```

### 2. Content Adaptation

```bash
# Get adapted content for a specific chapter
curl -X GET "http://localhost:8000/api/v1/personalization/content/CHAPTER_ID" \
  -H "Authorization: Bearer TEST_TOKEN"
```

## Troubleshooting

- If personalization features are not working, check that `PERSONALIZATION_ENABLED=true` in your environment
- If translation requests fail, verify your OpenAI API key is valid and has sufficient quota
- If recommendations are not appearing, ensure the user profile has been created with sufficient information
- For database connection issues, check that PostgreSQL is running and credentials are correct

## Performance Considerations

- Personalization calculations are cached for improved performance
- Translation results are cached to reduce API calls to external services
- Profile updates trigger background jobs to recalculate recommendations
- Monitor database performance as user data grows