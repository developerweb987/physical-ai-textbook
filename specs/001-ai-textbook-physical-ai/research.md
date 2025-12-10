# Research: AI-Native Textbook for Physical AI & Humanoid Robotics

## Decision: Chapter Structure and Flow
**Rationale**: Following a logical progression from fundamentals to advanced topics to ensure students build knowledge systematically. Starting with mechanical systems provides physical intuition before moving to control systems and AI integration.
**Alternatives considered**:
- AI-first approach (introduce AI concepts early)
- Topic-agnostic approach (mix all topics together)
- Project-based approach (integrate all concepts in projects)

## Decision: Technical Depth Level
**Rationale**: Undergraduate engineering level provides the right balance of theoretical foundation and practical application for the target audience. This level ensures accessibility while maintaining academic rigor.
**Alternatives considered**:
- Advanced graduate level (too complex for beginners)
- High school level (insufficient for engineering students)
- Professional certification level (too narrow focus)

## Decision: Content Format Choice
**Rationale**: Combining diagrams, code examples, and pseudocode provides multiple learning modalities to accommodate different learning preferences. Diagrams for visual learners, code for hands-on practitioners, and pseudocode for algorithmic understanding.
**Alternatives considered**:
- Code-only approach (insufficient for conceptual understanding)
- Theory-only approach (lacks practical application)
- Video-only approach (not compatible with static textbook format)

## Decision: RAG Chatbot Architecture
**Rationale**: Using OpenAI API with Qdrant vector storage provides reliable performance with good fallback options. The selected-text-only mode requires careful implementation to ensure context isolation.
**Alternatives considered**:
- Self-hosted models (higher maintenance, lower reliability)
- Multiple provider load balancing (unnecessary complexity)
- Simple keyword search (insufficient for understanding context)

## Decision: Agent Reusability Framework
**Rationale**: Implementing Subagents and Skills as separate modules enables reusability across chapters while maintaining clear separation of concerns. This supports the modular architecture principle.
**Alternatives considered**:
- Monolithic agent implementation (not reusable)
- Hard-coded agent logic (not maintainable)
- Third-party agent framework (less control over customization)

## Decision: Deployment Architecture
**Rationale**: Separating static textbook content (GitHub Pages/Docusaurus) from dynamic services (backend) optimizes for both performance and functionality. Static content loads quickly while dynamic features are served by backend.
**Alternatives considered**:
- Fully static approach (no personalization or chatbot possible)
- Fully dynamic approach (slower performance, higher cost)
- Single integrated platform (less flexibility for scaling components independently)