<h1 align="center"> Mudda AI Workflow Platform </h1>
<p align="center"> Automated, AI-Driven Workflow Orchestration for Civic Issue Resolution </p>

<p align="center">
  <img alt="Build" src="https://img.shields.io/badge/Build-Passing-brightgreen?style=for-the-badge">
  <img alt="Tests" src="https://img.shields.io/badge/Tests-100%25%20Coverage-success?style=for-the-badge">
  <img alt="Contributions" src="https://img.shields.io/badge/Contributions-Welcome-orange?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
</p>
<!-- 
  **Note:** These are static placeholder badges. Replace them with your project's actual badges.
  You can generate your own at https://shields.io
-->

## 📖 Table of Contents
*   [Overview](#-overview)
*   [Key Features](#-key-features)
*   [Tech Stack & Architecture](#-tech-stack--architecture)
*   [Project Structure](#-project-structure)
*   [Getting Started](#-getting-started)
*   [Usage](#-usage)
*   [Contributing](#-contributing)
*   [License](#-license)

---

## ⭐ Overview

The Mudda AI Workflow Platform is an intelligent system designed to streamline and automate the entire lifecycle of complex civic issue resolution. It transforms unstructured problem statements into traceable, executable, and reliable workflow plans, bridging the gap between identifying a problem and executing a solution.

### The Problem

> Current approaches to resolving complex, multi-stakeholder civic issues (e.g., infrastructure failures, public service deficiencies) are often manual, opaque, and highly inefficient. Planning a resolution requires identifying necessary actions, coordinating disparate service components, and reliably tracking state across long execution times. This complexity leads to delays, inconsistent outcomes, and a lack of accountability, hindering effective governance and citizen engagement.

### The Solution

Mudda eliminates this organizational bottleneck by introducing an AI-powered planning and orchestration layer. Using the Gemini AI, the system automatically analyzes a given problem statement, selects the most relevant, reusable operational components, and constructs a robust, multi-step `WorkflowPlan`. The execution of these plans is managed by Temporal, ensuring durability, fault tolerance, and clear observability of every step taken towards resolution.

This platform provides a comprehensive user interface for monitoring system health, visualizing execution progress, and managing the library of reusable components that form the foundation of all resolution strategies.

### Architecture Overview

The platform employs a robust **Microservices** and **Component-based Architecture**. The frontend is powered by `react`, providing a highly interactive and responsive web application experience. The core business logic and API services are handled by a high-performance `fastapi` backend. Workflow generation leverages advanced AI modeling (`google-generativeai`), and execution guarantees are provided by the `temporalio` orchestration engine, ensuring that complex, long-running processes complete reliably.

---

## ✨ Key Features

The Mudda AI Workflow Platform provides cutting-edge capabilities focused on accelerating the resolution of civic issues through intelligent automation and robust execution management.

### 🧠 Intelligent Workflow Generation
The system utilizes a two-step AI process (`generate_workflow_plan` in `ai_service.py`) to move from a raw idea to an executable plan:
*   **Component Selection:** Automatically analyzes the `ProblemStatementRequest` and selects the most relevant functional components available in the system.
*   **Plan Synthesis:** Generates a detailed, sequenced `WorkflowPlanSchema` complete with individual steps and required inputs, ready for immediate execution.
*   **Benefit:** Instantly convert ambiguous problems into actionable, structured project plans, drastically reducing planning time.

### ⚙️ Durable Execution Orchestration
Leveraging Temporal, the platform ensures that resolution workflows run reliably, regardless of infrastructure failures or external service outages:
*   **Fault Tolerance:** Workflows are stateful and resume automatically, preventing data loss or partial execution.
*   **Long-Running Processes:** Manages workflows that span days or weeks, such as those related to infrastructure projects or bureaucratic processes.
*   **Traceability:** Every `WorkflowExecution` is tracked meticulously, providing clear oversight into the current state and history of civic resolution efforts.
*   **Benefit:** Achieve guaranteed delivery and completion of complex, multi-stage resolution plans with full audit capabilities.

### 🧩 Reusable Component Library Management
The system is built on a library of modular, atomic service components (`Component` model in `component.py`):
*   **CRUD Operations:** Users can `create_component`, `get_component`, and `list_components` via the API and UI (`CreateComponentModal.tsx`).
*   **AI Integration:** A dedicated `ComponentForSelection` schema ensures components are formatted minimally for the AI to efficiently choose the optimal set for a given problem.
*   **Benefit:** Promotes standardization and reuse of functional units (e.g., "Notify Citizen API," "Submit Permit Request Service"), accelerating workflow creation and increasing system reliability.

### 📊 Real-Time Dashboard and Analytics
The frontend provides a rich set of visualization tools for operational insight:
*   **Dashboard View:** The `dashboard` area features a centralized summary using components like `StatsGrid.tsx`, `DashboardHeader.tsx`, and `RecentActivity.tsx`.
*   **Operational Metrics:** Track crucial KPIs such as `IssueCategories` and `ResolutionTrend` over time.
*   **Geographic Visualization:** The platform features components like `GeographicMap.tsx` and `GeographicMapSection.tsx` for spatial analysis of issue distribution and resolution efforts.
*   **Benefit:** Provides decision-makers with a single pane of glass to monitor system performance, identify critical trends, and understand the real-world impact of executed workflows.

### 📈 Detailed Workflow Visualization
*   **Workflow Graph:** The `WorkflowGraph.tsx` component allows users to visually inspect the structure of a generated `WorkflowPlan`, including the sequence of steps and component dependencies.
*   **Execution Details:** `WorkflowDetailsModal.tsx` provides deep-dive information on the status of a specific execution, including input/output and logs for each step.
*   **Benefit:** Enhances transparency and simplifies the debugging and auditing process for all resolution activities.

---

## 🛠️ Tech Stack & Architecture

The Mudda AI Workflow Platform is built on a modern, high-performance, and scalable technology stack designed for microservices architecture and complex data handling.

| Technology | Domain | Purpose | Why it was Chosen |
| :--- | :--- | :--- | :--- |
| **react** | Frontend | Interactive, component-driven User Interface (UI). | Provides a scalable framework for complex data visualization (Graphs, Tables, Maps) and responsive dashboards. |
| **fastapi** | Backend API | Core API for CRUD operations, service routing, and high-speed data delivery. | Chosen for its speed, robust Pydantic data validation, and automatic interactive documentation capabilities. |
| **google-generativeai** | AI Service | Powers the `AIService` for generating complex `WorkflowPlan` JSON structures from natural language. | Essential for the core value proposition of intelligent planning and component selection. |
| **temporalio** | Workflow Orchestration | Guarantees durable, fault-tolerant execution of long-running, multi-step civic resolution workflows. | Ensures execution state is preserved across failures, making workflows reliable and traceable. |
| **sqlalchemy** | Data Layer | Object Relational Mapper (ORM) for defining and interacting with data models (`Component`, `WorkflowPlan`, `WorkflowExecution`). | Provides an efficient, Pythonic way to manage database interactions and enforce data integrity. |
| **pydantic** | Data Validation | Used extensively across both models and schemas for runtime data type checking and validation. | Crucial for ensuring consistency between the AI-generated JSON output and the internal system schemas. |
| **psycopg2-binary** | Database Driver | PostgreSQL database adapter. | Facilitates robust and efficient connection to the relational database for storing model data. |

---
---

## 🚀 Getting Started

To set up the Mudda AI Workflow Platform locally, you will need to initialize both the Python backend and the TypeScript frontend environments.

### Prerequisites

You must have the following software installed:

1.  **Python 3.10+**
2.  **Node.js (LTS)** and **npm/yarn**
3.  **Database System (Implied):** A PostgreSQL instance is required, as indicated by the `psycopg2-binary` dependency.
4.  **Temporal Server:** A running Temporal server instance is required to execute the workflows defined in `temporal_workflows.py`.

### Backend Installation

Navigate to the `backend/` directory to set up the FastAPI application and required services.

1.  **Install Python Dependencies:**
    Use the provided `requirements.txt` to install all necessary Python packages, including `fastapi`, `temporalio`, and `google-generativeai`.

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

2.  **Configuration:**
    The application relies on settings defined in `config.py`. You will need to configure database connection strings, Temporal server endpoints, and Gemini API keys (required for `gemini_client.py`).

    ```bash
    # Based on the env_example file provided in the analysis
    cp env_example .env
    # Edit the .env file with your specific configuration details
    ```

3.  **Database Setup:**
    The project uses `sqlalchemy` and requires migration, although `alembic` setup files are not explicitly shown, the dependency exists. Initialize and run migrations to create the tables for `Component`, `WorkflowPlan`, and `WorkflowExecution`.

### Frontend Installation

Navigate to the `frontend/` directory to set up the Next.js application.

1.  **Install Node Dependencies:**

    ```bash
    cd frontend
    npm install
    # OR
    yarn install
    ```

2.  **Start the Frontend Server:**
    The frontend is the primary user interface (`web_app`) for interacting with the platform.

    ```bash
    npm run dev
    # OR
    yarn dev
    ```

### Running Services

To operate the full platform, three core services must be running concurrently:

1.  **FastAPI Backend API (`main.py`):** Handles all HTTP requests from the frontend, manages CRUD operations for components/workflows, and serves as the intermediary for AI generation.
2.  **Temporal Worker (`temporal_worker.py`):** This is the core process that polls the Temporal server, executes the `WorkflowActivities`, and manages the actual step-by-step resolution logic defined in `temporal_workflows.py`.
3.  **Frontend UI Server:** Provides the interactive dashboard and management interfaces.

---

## 🔧 Usage

As a unified `web_app`, the primary usage involves interacting through the responsive frontend interface after all services are running.

### 1. Accessing the Platform

Once the frontend server is running, access the dashboard via your local browser (typically `http://localhost:3000`). The core navigation is provided by the `Sidebar.tsx` component, allowing users to access:

*   **Dashboard:** (Accessed via `/dashboard`) - Utilize the `StatsGrid` and `ResolutionTrend` visualizations for monitoring.
*   **Components:** (Accessed via `/components`) - Manage the reusable library of operational components.
*   **Workflows:** (Accessed via `/workflows`) - Generate new workflow plans and monitor executions.

### 2. Managing Components

Components are the building blocks of every workflow plan.

*   **Creating a New Component:** Use the `CreateComponentModal.tsx` to define a new operational unit (e.g., a specific API call, a human approval step). This component is then stored in the database (`component.py`) and made available for AI selection (`component_schema.py: ComponentForSelection`).
*   **Viewing Details:** The `ComponentDetailsModal.tsx` allows users to inspect the schema, description, and usage history of any component.

### 3. Generating a Workflow Plan

This is the central function of the platform, transforming a civic problem into an executable plan:

1.  Navigate to the **Workflows** page.
2.  Initiate the workflow generation process (via `GenerateWorkflowModal.tsx`).
3.  Submit a detailed problem statement (`ProblemStatementRequest`).
4.  The system calls the `workflow_service.py` which delegates to `ai_service.py`.
5.  The AI service performs component selection and workflow generation, returning a validated `WorkflowGenerationResponse` containing the `WorkflowPlanSchema`.
6.  The generated plan is visualized using the `WorkflowGraph.tsx`, allowing the user to review the sequence before execution.

### 4. Executing and Monitoring Workflows

Once a plan is approved, it can be executed:

1.  The user initiates execution via the UI, triggering the `execute_workflow` function in `workflow_service.py`, which communicates with the Temporal manager.
2.  The `MuddaWorkflow` is started on the Temporal server.
3.  Monitor the progress in the **Workflows Table** (`WorkflowsTable.tsx`).
4.  For detailed analysis, open the `WorkflowDetailsModal.tsx` to view the status of individual steps as the execution progresses, ensuring complete transparency and accountability.

---

## 🤝 Contributing

We welcome contributions to improve the Mudda AI Workflow Platform! Your input helps make this project better for everyone, particularly those striving to improve civic processes.

### How to Contribute

1.  **Fork the repository** - Click the 'Fork' button at the top right of this page
2.  **Create a feature branch**
    ```bash
    git checkout -b feature/amazing-feature
    ```
3.  **Make your changes** - Improve code, documentation, or features. Focus on separate concerns within the `frontend/` or `backend/` directories.
4.  **Test thoroughly** - Ensure all new and existing functionality works as expected. While formal test scripts are not provided in the analysis, you can use `example_usage.py` for API testing.
    ```bash
    # Run tests on the backend
    python backend/example_usage.py
    # Run tests on the frontend
    npm test
    ```
5.  **Commit your changes** - Write clear, descriptive commit messages
    ```bash
    git commit -m 'Feat: Implement enhanced geographic filtering for dashboard'
    ```
6.  **Push to your branch**
    ```bash
    git push origin feature/amazing-feature
    ```
7.  **Open a Pull Request** - Submit your changes for review against the main branch.

### Development Guidelines

*   ✅ **Code Style:** Follow the existing Python (PEP 8 for backend) and TypeScript/React conventions.
*   📝 **Documentation:** Add docstrings to new functions and classes, especially within the critical `services/` and `temporal/` directories.
*   🧪 **Testing:** Verify all new `routers/` endpoints and `services/` logic.
*   📚 **Schema Updates:** If modifying models or schemas, ensure changes are reflected in both Pydantic schemas (`schemas/`) and TypeScript types (`frontend/lib/type.ts`).
*   🔄 **Dependencies:** Only introduce verified, stable dependencies.
*   🎯 **Atomic Commits:** Keep commits focused on a single logical change.

### Ideas for Contributions

We are looking for help in key areas to expand the platform's capabilities:

*   🐛 **Bug Fixes:** Address issues related to workflow serialization or execution reliability.
*   ✨ **New Features:** Implement advanced features for the AI service, such as constraint checking for workflow plans.
*   📖 **Documentation:** Improve setup guides, explain the Temporal workflow structure (`MuddaWorkflow`), and detail the Component API.
*   🎨 **UI/UX:** Enhance the visualization of the `WorkflowGraph.tsx` or improve accessibility of the dashboards.
*   ⚡ **Performance:** Optimize database queries within `workflow_service.py` and `component_service.py`.

### Code Review Process

*   All submissions require review by maintainers before merging.
*   Maintainers will provide constructive feedback focused on quality and adherence to architecture standards.
*   Once approved, your Pull Request will be merged and you'll be credited in the release notes.

### Questions?

Feel free to open an issue for any questions regarding development, bugs, or feature ideas.

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

### What this means:

- ✅ **Commercial use:** You can use this project commercially
- ✅ **Modification:** You can modify the code to suit your specific needs
- ✅ **Distribution:** You can distribute this software to others
- ✅ **Private use:** You can use this project privately for internal systems
- ⚠️ **Liability:** The software is provided "as is," without warranty of any kind. The authors are not liable for damages or other claims.
- ⚠️ **Trademark:** This license does not grant trademark rights to the project name or logo.

---

<p align="center">Made with ❤️ by the Shubh Pundir</p>
<p align="center">
  <a href="#">⬆️ Back to Top</a>
</p>
