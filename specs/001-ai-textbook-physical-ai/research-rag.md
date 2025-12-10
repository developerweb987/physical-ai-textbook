# Research: RAG Chatbot for AI-Native Textbook

## Decision: RAG Architecture Approach
**Rationale**: Using OpenAI API with Qdrant vector database provides a reliable, scalable solution for textbook content retrieval. This approach allows for both global (entire book) and selected-text modes while maintaining response accuracy and speed.
**Alternatives considered**:
- Self-hosted models (higher maintenance, lower reliability)
- Multiple provider load balancing (unnecessary complexity for initial implementation)
- Simple keyword search (insufficient for understanding context and semantics)

## Decision: Global vs Selected-Text Modes Implementation
**Rationale**: Implementing both modes using the same underlying RAG infrastructure but with different context windows allows for flexible querying. Global mode retrieves from entire textbook corpus, while selected-text mode restricts to highlighted/selected content.
**Alternatives considered**:
- Single unified mode (less flexible for different use cases)
- Separate implementations (more complex to maintain consistency)
- Precomputed answers (less dynamic and adaptive to new content)

## Decision: Content Chunking Strategy
**Rationale**: Using semantic chunking based on document structure (sections, paragraphs) with overlap ensures context preservation while allowing effective retrieval. Chunks of 512-1024 tokens provide good balance between context and precision.
**Alternatives considered**:
- Fixed-size token chunks (may split related content)
- Sentence-level chunks (too granular, may miss context)
- Full-section chunks (too large, reduces precision)

## Decision: Embedding Model Selection
**Rationale**: Using OpenAI's text-embedding-3-small model provides good balance of cost, speed, and quality for textbook content. It's well-suited for technical content like Physical AI and Robotics.
**Alternatives considered**:
- text-embedding-3-large (higher cost, marginal quality improvement)
- Self-hosted models like SentenceTransformers (higher maintenance, potentially lower quality)
- Older embedding models (lower quality for technical content)

## Decision: Response Validation and Citations
**Rationale**: Implementing source citations with page/chapter references ensures academic rigor and allows students to verify information. Response validation includes accuracy checking against source material.
**Alternatives considered**:
- No citations (violates academic accuracy requirements)
- Generic references (not specific enough for textbook use)
- Manual verification only (not scalable)

## Decision: Session Management and Context
**Rationale**: Implementing conversation sessions with configurable history length allows for context-aware responses while respecting privacy and performance requirements. Anonymous sessions for casual users and authenticated sessions for personalized experiences.
**Alternatives considered**:
- No session context (less conversational quality)
- Permanent session storage (privacy concerns)
- Fixed context windows (less flexible for different use cases)

## Decision: API Rate Limiting and Caching
**Rationale**: Implementing intelligent caching for common queries and rate limiting per user/IP prevents abuse while optimizing costs and performance. Cache TTL based on content update frequency.
**Alternatives considered**:
- No caching (higher costs, slower responses)
- Aggressive caching (stale information risk)
- No rate limiting (potential for abuse and high costs)