# Technology Stack Documentation

This document provides a detailed overview of the technologies, frameworks, and libraries used in the Smart Code Review project.

## 🎨 Frontend

The frontend is built with **React** and **TypeScript**, focusing on performance and a modern user experience.

- **Framework**: [React](https://react.dev/) (v18) with [Vite](https://vitejs.dev/) for fast build tooling.
- **Language**: [TypeScript](https://www.typescriptlang.org/) for type safety.
- **Styling**: 
  - [Tailwind CSS](https://tailwindcss.com/) for utility-first styling.
  - [Shadcn UI](https://ui.shadcn.com/) for accessible, reusable components (based on Radix UI).
  - `class-variance-authority` (CVA) for managing component variants.
- **State Management & Data Fetching**:
  - [TanStack Query (React Query)](https://tanstack.com/query/latest) for server state management and caching.
  - React Context API for global UI state.
- **Routing**: [React Router](https://reactrouter.com/) (v6).
- **Visualization**: [Recharts](https://recharts.org/) for dashboard charts and graphs.
- **Icons**: [Lucide React](https://lucide.dev/).
- **Forms**: [React Hook Form](https://react-hook-form.com/) with [Zod](https://zod.dev/) for schema validation.
- **Utilities**: `date-fns` for date manipulation.

## ⚙️ Backend

The backend is a high-performance **Python** application designed for asynchronous processing.

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) for building high-performance APIs with automatic docs (Swagger UI).
- **Language**: Python 3.11+.
- **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (v2.0) for database interactions.
- **Task Queue**: [Celery](https://docs.celeryq.dev/) for background processing (e.g., long-running code analysis).
- **Message Broker**: [Redis](https://redis.io/) (used by Celery).
- **Web Server**: [Uvicorn](https://www.uvicorn.org/) (ASGI server).
- **Authentication/Integrations**:
  - `PyGithub` for interacting with the GitHub API.
  - `python-dotenv` for environment configuration.

## 🤖 AI & Logic

- **LLM Provider**: [OpenRouter](https://openrouter.ai/) accessing **DeepSeek R1** models.
- **Client**: OpenAI Python SDK (configured for OpenRouter).
- **Static Analysis**: 
  - [Tree-sitter](https://tree-sitter.github.io/) for robust code parsing.
  - [Semgrep](https://semgrep.dev/) for static analysis and security checks.

## 🗄️ Database & Storage

- **Primary Database**: [PostgreSQL](https://www.postgresql.org/) (Production) / SQLite (Local Dev).
- **Cache/Broker**: Redis.

## 🚀 DevOps & Tools

- **Containerization**: [Docker](https://www.docker.com/) & Docker Compose for orchestration.
- **Linting**: ESLint (Frontend).
- **Formatting**: Prettier (Frontend - implied).
- **Package Managers**: 
  - `npm` (Frontend)
  - `pip` (Backend)

## 📁 Key Directory Structure

- `/frontend`: React application source code.
- `/analysis_engine`: Core logic for code review and LLM interaction.
- `/routes`: FastAPI route handlers (API endpoints).
- `/static`: Static assets served by the backend (e.g., favicons).
- `main.py`: Entry point for the backend application.
- `models.py`: Database schema definitions.
