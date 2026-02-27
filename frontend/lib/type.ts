import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface WorkflowStep {
  step_id: string;
  activity_id?: string;
  component_id?: string;
  description: string;
  inputs: Record<string, any>;
  outputs: string[];
  next: string[];
  requires_approval?: boolean;
}

export interface WorkflowPlan {
  workflow_name: string;
  description: string;
  steps: WorkflowStep[];
}

export interface Workflow {
  workflow_id: string;
  workflow_plan: WorkflowPlan;
  status: string;
  created_at: string;
}

export interface ProblemStatementRequest {
  problem_statement: string;
}

export interface ComponentActivity {
  activity_name: string;
  description?: string;
  retry_policy?: {
    initial_interval?: number;
    backoff_coefficient?: number;
    maximum_interval?: number;
    maximum_attempts?: number;
    non_retryable_error_types?: string[];
  };
  timeout?: number;
  metadata?: Record<string, any>;
}

export interface Component {
  id: string;
  name: string;
  description?: string;
  category?: string;
  version?: string;
  is_active?: boolean;
  activities: ComponentActivity[];
  config?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface ComponentCreateRequest {
  name: string;
  description?: string;
  category?: string;
  version?: string;
  activities: ComponentActivity[];
  config?: Record<string, any>;
}
