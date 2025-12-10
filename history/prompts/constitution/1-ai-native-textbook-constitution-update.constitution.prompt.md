---
id: 1
title: AI Native Textbook Constitution Update
stage: constitution
date: 2025-12-10
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: user
command: /sp.constitution
labels: [constitution, textbook, physical-ai, ai-native]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - .specify/templates/plan-template.md
 - .specify/templates/spec-template.md
 - .specify/templates/tasks-template.md
tests:
 - none
---

## Prompt

```
Project: AI-Native Textbook for Teaching Physical AI & Humanoid Robotics

Core principles:
- AI/Spec-driven development workflow using Spec-Kit Plus and Claude Code
- Clarity, accessibility, and academic rigor suitable for university-level engineering students
- Hands-on, practical, and modular content compatible with AI-native textbooks
- Technical accuracy in robotics, humanoid mechanics, sensors, locomotion, control systems, and Physical AI
- Systematic integration of AI Agents, RAG, and personalization within the textbook
- Reusability of Agents, Subagents, and Skills as a core architectural principle

Key standards:
- Book must be I-agent–related logic must be separated into dedicated modules for maintainability
- Personalization rules may not conflict with academic correctness (no hallucinated simplifications)

Success criteria:
- Fully functional Docusaurus textbook deployed on GitHub Pages
- Integrated RAG chatbot works end-to-end with both global and "selected-text-only" modes
- All chapters written, reviewed, and validated through Spec-Kit Plus workflows (/sp.requirements → /sp.specify → /sp.plan → /sp.task)
- Subagents and Agent Skills demonstrated and reusable in multiple chapters (bonus scoring)
- Optional: Working signup/signin system using BetterAuth with background-based personalization (bonus scoring)
- Optional: Dynamic chapter personalization and Urdu translation buttons fully functional (bonus scoring)
- Submission meets all hackathon scoring requirements (base + bonus points)
```

## Response snapshot

Updated the project constitution to reflect the AI-Native Textbook for Teaching Physical AI & Humanoid Robotics project. The new constitution includes:

1. Core Principles:
   - AI/Spec-driven Development
   - Academic Rigor and Technical Accuracy
   - Modular and Reusable Architecture
   - Accessibility and Clarity
   - End-to-End Integration Testing
   - Versioning and Deployment Standards

2. Technical Standards section
3. Development Workflow section
4. Governance section

Also updated template files to align with the new constitution:
- Updated plan-template.md with constitution checks
- Updated spec-template.md with functional requirements aligned to constitution
- Updated tasks-template.md with foundational tasks aligned to constitution

## Outcome

- ✅ Impact: Updated constitution to align with AI-Native Textbook project goals
- 🧪 Tests: none
- 📁 Files: 4 files updated to align with new constitution
- 🔁 Next prompts: Feature specification and planning using new constitution
- 🧠 Reflection: Constitution provides clear governance framework for Physical AI textbook development

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin feature specification using new constitution