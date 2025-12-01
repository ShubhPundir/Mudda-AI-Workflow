import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8081';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface WorkflowStep {
  step_id: string;
  component_id: string;
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

export interface Component {
  id: string;
  name: string;
  description?: string;
  type: string;
  category?: string;
  endpoint_url: string;
  http_method?: string;
  query_template?: string;
  rpc_function?: string;
  auth_type?: string;
  auth_config?: Record<string, any>;
  request_schema?: Record<string, any>;
  response_schema?: Record<string, any>;
  path_params?: Record<string, any> | any[] | string[];
  query_params?: Record<string, any>;
  version?: string;
  owner_service?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ComponentCreateRequest {
  name: string;
  description?: string;
  type: string;
  category?: string;
  endpoint_url: string;
  http_method?: string;
  query_template?: string;
  rpc_function?: string;
  auth_type?: string;
  auth_config?: Record<string, any>;
  request_schema?: Record<string, any>;
  response_schema?: Record<string, any>;
  path_params?: Record<string, any> | any[] | string[];
  query_params?: Record<string, any>;
  version?: string;
  owner_service?: string;
}
