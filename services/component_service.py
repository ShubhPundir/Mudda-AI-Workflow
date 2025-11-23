"""
Service layer for Component operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Component
from schemas import ComponentCreateRequest, ComponentResponse, ComponentForAI


class ComponentService:
    """Service class for Component operations"""
    
    @staticmethod
    def create_component(db: Session, component_data: ComponentCreateRequest) -> ComponentResponse:
        """Create a new component"""
        component = Component(
            name=component_data.name,
            description=component_data.description,
            type=component_data.type,
            category=component_data.category,
            endpoint_url=component_data.endpoint_url,
            http_method=component_data.http_method,
            query_template=component_data.query_template,
            rpc_function=component_data.rpc_function,
            auth_type=component_data.auth_type,
            auth_config=component_data.auth_config,
            request_schema=component_data.request_schema,
            response_schema=component_data.response_schema,
            path_params=component_data.path_params,
            query_params=component_data.query_params,
            version=component_data.version,
            owner_service=component_data.owner_service
        )
        
        db.add(component)
        db.commit()
        db.refresh(component)
        
        return ComponentResponse(
            id=str(component.id),
            name=component.name,
            description=component.description,
            type=component.type,
            category=component.category,
            endpoint_url=component.endpoint_url,
            http_method=component.http_method,
            query_template=component.query_template,
            rpc_function=component.rpc_function,
            auth_type=component.auth_type,
            auth_config=component.auth_config,
            request_schema=component.request_schema,
            response_schema=component.response_schema,
            path_params=component.path_params,
            query_params=component.query_params,
            version=component.version,
            owner_service=component.owner_service,
            is_active=component.is_active,
            created_at=component.created_at,
            updated_at=component.updated_at
        )
    
    @staticmethod
    def get_component(db: Session, component_id: str) -> Optional[ComponentResponse]:
        """Get a component by ID"""
        component = db.query(Component).filter(Component.id == component_id).first()
        
        if not component:
            return None
        
        return ComponentResponse(
            id=str(component.id),
            name=component.name,
            description=component.description,
            type=component.type,
            category=component.category,
            endpoint_url=component.endpoint_url,
            http_method=component.http_method,
            query_template=component.query_template,
            rpc_function=component.rpc_function,
            auth_type=component.auth_type,
            auth_config=component.auth_config,
            request_schema=component.request_schema,
            response_schema=component.response_schema,
            path_params=component.path_params,
            query_params=component.query_params,
            version=component.version,
            owner_service=component.owner_service,
            is_active=component.is_active,
            created_at=component.created_at,
            updated_at=component.updated_at
        )
    
    @staticmethod
    def list_components(db: Session, active_only: bool = True) -> List[ComponentResponse]:
        """List all components"""
        query = db.query(Component)
        if active_only:
            query = query.filter(Component.is_active == True)
        components = query.all()
        return [
            ComponentResponse(
                id=str(component.id),
                name=component.name,
                description=component.description,
                type=component.type,
                category=component.category,
                endpoint_url=component.endpoint_url,
                http_method=component.http_method,
                query_template=component.query_template,
                rpc_function=component.rpc_function,
                auth_type=component.auth_type,
                auth_config=component.auth_config,
                request_schema=component.request_schema,
                response_schema=component.response_schema,
                path_params=component.path_params,
                query_params=component.query_params,
                version=component.version,
                owner_service=component.owner_service,
                is_active=component.is_active,
                created_at=component.created_at,
                updated_at=component.updated_at
            )
            for component in components
        ]
    
    @staticmethod
    def get_components_for_ai(db: Session) -> List[ComponentForAI]:
        """Get components in format suitable for AI processing"""
        components = db.query(Component).filter(Component.is_active == True).all()
        return [
            ComponentForAI(
                id=str(component.id),
                name=component.name,
                description=component.description,
                type=component.type,
                category=component.category,
                endpoint_url=component.endpoint_url,
                http_method=component.http_method,
                query_template=component.query_template,
                rpc_function=component.rpc_function,
                auth_type=component.auth_type,
                auth_config=component.auth_config,
                request_schema=component.request_schema,
                response_schema=component.response_schema,
                path_params=component.path_params,
                query_params=component.query_params,
                version=component.version,
                owner_service=component.owner_service
            )
            for component in components
        ]
