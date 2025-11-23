"""
Pydantic schemas for Component model
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime


class ComponentSchema(BaseModel):
    """Schema for component data"""
    id: str
    name: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    endpoint_url: str
    http_method: Optional[str] = None
    query_template: Optional[str] = None
    rpc_function: Optional[str] = None
    auth_type: Optional[str] = "NONE"
    auth_config: Optional[Dict[str, Any]] = {}
    request_schema: Optional[Dict[str, Any]] = {}
    response_schema: Optional[Dict[str, Any]] = {}
    path_params: Optional[Union[Dict[str, Any], List[Any], List[str]]] = {}
    query_params: Optional[Dict[str, Any]] = {}
    version: Optional[str] = "1.0"
    owner_service: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ComponentCreateRequest(BaseModel):
    """Request schema for creating a new component"""
    name: str = Field(..., description="Friendly name of the component")
    description: Optional[str] = Field(None, description="What the API/component does")
    type: str = Field(..., description="Component type: REST, RPC, or GraphQL")
    category: Optional[str] = Field(None, description="Optional category like 'Issue Management'")
    endpoint_url: str = Field(..., description="Full URL with optional variables like {issue_id}")
    http_method: Optional[str] = Field(None, description="HTTP method for REST APIs")
    query_template: Optional[str] = Field(None, description="GraphQL query or mutation template")
    rpc_function: Optional[str] = Field(None, description="RPC function/method name")
    auth_type: Optional[str] = Field("NONE", description="Authentication type")
    auth_config: Optional[Dict[str, Any]] = Field({}, description="Authentication configuration")
    request_schema: Optional[Dict[str, Any]] = Field({}, description="Request payload structure")
    response_schema: Optional[Dict[str, Any]] = Field({}, description="Response structure")
    path_params: Optional[Union[Dict[str, Any], List[Any], List[str]]] = Field({}, description="Path parameters for templated URLs")
    query_params: Optional[Dict[str, Any]] = Field({}, description="Query parameters")
    version: Optional[str] = Field("1.0", description="Component version")
    owner_service: Optional[str] = Field(None, description="Owning microservice")


class ComponentResponse(BaseModel):
    """Response schema for component operations"""
    id: str
    name: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    endpoint_url: str
    http_method: Optional[str] = None
    query_template: Optional[str] = None
    rpc_function: Optional[str] = None
    auth_type: Optional[str] = "NONE"
    auth_config: Optional[Dict[str, Any]] = {}
    request_schema: Optional[Dict[str, Any]] = {}
    response_schema: Optional[Dict[str, Any]] = {}
    path_params: Optional[Union[Dict[str, Any], List[Any], List[str]]] = {}
    query_params: Optional[Dict[str, Any]] = {}
    version: Optional[str] = "1.0"
    owner_service: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ComponentForSelection(BaseModel):
    """Minimal schema for component selection (only id, name, description)"""
    id: str
    name: str
    description: Optional[str] = None


class ComponentForAI(BaseModel):
    """Schema for components formatted for AI processing (excludes audit fields)"""
    id: str
    name: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    endpoint_url: str
    http_method: Optional[str] = None
    query_template: Optional[str] = None
    rpc_function: Optional[str] = None
    auth_type: Optional[str] = "NONE"
    auth_config: Optional[Dict[str, Any]] = {}
    request_schema: Optional[Dict[str, Any]] = {}
    response_schema: Optional[Dict[str, Any]] = {}
    path_params: Optional[Union[Dict[str, Any], List[Any], List[str]]] = {}
    query_params: Optional[Dict[str, Any]] = {}
    version: Optional[str] = "1.0"
    owner_service: Optional[str] = None