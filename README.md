# Mudda AI Workflow System

This project implements an intelligent civic issue resolution system that uses AI agents to dynamically generate and orchestrate workflows.

## Backend Architecture

The backend is built with **FastAPI** and utilizes a sophisticated AI-driven engine to plan and execute workflows.

### 🔍 Core Concepts

#### 1. The Two-Agent AI Engine
The heart of the system uses a **two-step Generative AI process** (running on Gemini 2.5 Flash) to translate natural language problem statements into executable technical plans. This creates a more robust and token-efficient generation process:

*   **Agent 1: The Component Selector** ("Mudda AI Component Selector")
    *   **Input**: User's problem statement (e.g., "Water leakage in Sector 4").
    *   **Task**: Analyzes the problem and filters the massive library of available API components (tools) down to just the relevant ones.
    *   **Goal**: Reduces noise and context window usage for the planning phase.

*   **Agent 2: The Workflow Plan Maker** ("Mudda AI Plan Maker")
    *   **Input**: Problem statement + *Selected* Component details (Schemas, Endpoints).
    *   **Task**: Constructs a valid **Directed Acyclic Graph (DAG)**. It maps specific component actions to steps, defines data inputs/outputs, and handles logic like human approval requirements.
    *   **Result**: An executable JSON workflow plan.

#### 2. Temporal.io Orchestration
Once a plan is generated and approved, it is not executed by a simple script. It is handed off to **Temporal.io**, a durable execution engine.

*   **Reliability**: Temporal ensures that if a step fails (network error, service down), it retries automatically.
*   **Human-in-the-Loop**: The workflow supports long-running processes, such as waiting for a human officer to approve a budget or verify a fix, which might take days.
*   **State Management**: Every step's input and output is recorded, allowing full auditability of the government process.


### 🚀 How it Works Flow

1.  **Request**: User submits a problem statement via API.
2.  **Generation**: `AIService` invokes Agent 1 to pick tools, then Agent 2 to build the plan.
3.  **Review**: The plan is saved as a `DRAFT`.
4.  **Execution**: Upon trigger, the plan is converted into a Temporal Workflow.
5.  **Processing**: The Temporal Worker executes steps sequentially or in parallel, making actual API calls to the defined components.

## Getting Started

1.  Navigate to `backend/`.
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Set up environment variables (Gemini API Key, DB Connection, Temporal Host).
4.  Run the API: `uvicorn main:app --reload`.
5.  Run the Temporal Worker: `python temporal_worker.py`.
