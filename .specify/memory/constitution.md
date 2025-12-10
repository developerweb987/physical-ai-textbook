<!-- SYNC IMPACT REPORT
Version change: N/A → 1.0.0
Added sections: All principles and sections for AI-Native Textbook project
Removed sections: None (new constitution)
Modified principles: N/A (new constitution)
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/*.md: ✅ updated
- README.md: ⚠ pending
Follow-up TODOs: None
-->

# AI-Native Textbook for Teaching Physical AI & Humanoid Robotics Constitution

## Core Principles

### AI/Spec-driven Development
All development follows AI/Spec-driven workflow using Spec-Kit Plus and Claude Code; Every feature must be planned through /sp.requirements → /sp.specify → /sp.plan → /sp.task workflow before implementation; All changes must be testable and follow systematic approach

### Academic Rigor and Technical Accuracy
Content must maintain university-level engineering standards with technical accuracy in robotics, humanoid mechanics, sensors, locomotion, control systems, and Physical AI; No hallucinated simplifications that conflict with academic correctness; All technical claims must be verifiable

### Modular and Reusable Architecture
All AI-agent-related logic must be separated into dedicated modules for maintainability; Subagents and Agent Skills must be reusable across multiple chapters; Systematic integration of AI Agents, RAG, and personalization within the textbook

### Accessibility and Clarity
Content must be clear and accessible to university-level engineering students; All complex concepts should be explained with hands-on, practical examples; Modular content structure for flexible learning paths

### End-to-End Integration Testing
Focus areas requiring integration tests: RAG chatbot functionality (global and selected-text-only modes), Docusaurus deployment pipeline, Personalization systems, Dynamic translation features

### Versioning and Deployment Standards
All features must be deployed on GitHub Pages via Docusaurus; Version control follows semantic versioning with clear release notes; Backwards compatibility maintained for core textbook functionality

## Technical Standards

Technology stack: Docusaurus for textbook, RAG for chatbot, BetterAuth for authentication (optional), React for UI components; Code quality: All code must pass linting, testing, and security checks; Performance: Pages must load within 3 seconds, RAG responses within 5 seconds

## Development Workflow

All features must follow Spec-Kit Plus workflow: requirements → spec → plan → tasks; Code reviews required for all PRs; Tests must pass before merging; Documentation must be updated with each feature

## Governance

All PRs/reviews must verify compliance with academic correctness and technical accuracy; Complexity must be justified with educational value; Use Spec-Kit Plus templates for all planning artifacts; Constitution supersedes all other practices; Amendments require documentation and team approval

**Version**: 1.0.0 | **Ratified**: 2025-12-10 | **Last Amended**: 2025-12-10