"""
Service layer for Component operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Component
from schemas import ComponentCreateRequest, ComponentResponse, ComponentForSelection, ComponentForAI

'''
NOTE: I have added MCP like tools for System orchestration
 which are very much like API calls or microservices, 
 like sending email, booking something, 
 each of them have a reply to it as well. 
 So whenever each component gets executed, 
 it replies back and leaves linear paths inside 
 each component task of system orchestration service
'''

class ComponentService:
    """Service class for Component operations"""
    
    @staticmethod
    async def create_component(db: AsyncSession, component_data: ComponentCreateRequest) -> ComponentResponse:
        """Create a new component"""
        component = Component(
            name=component_data.name,
            description=component_data.description,
            category=component_data.category,
            version=component_data.version,
            activities=component_data.activities,
            config=component_data.config
        )
        
        db.add(component)
        await db.commit()
        await db.refresh(component)
        
        return ComponentResponse(
            id=str(component.id),
            name=component.name,
            description=component.description,
            category=component.category,
            version=component.version,
            is_active=component.is_active,
            activities=component.activities,
            config=component.config,
            created_at=component.created_at,
            updated_at=component.updated_at
        )
    
    @staticmethod
    async def get_component(db: AsyncSession, component_id: str) -> Optional[ComponentResponse]:
        """Get a component by ID"""
        from uuid import UUID
        
        # Convert string ID to UUID object
        try:
            uuid_id = UUID(component_id)
        except ValueError:
            return None
        
        result = await db.execute(select(Component).filter(Component.id == uuid_id))
        component = result.scalars().first()
        
        if not component:
            return None
        
        return ComponentResponse(
            id=str(component.id),
            name=component.name,
            description=component.description,
            category=component.category,
            version=component.version,
            is_active=component.is_active,
            activities=component.activities,
            config=component.config,
            created_at=component.created_at,
            updated_at=component.updated_at
        )
    
    
    @staticmethod
    async def get_components_by_ids(db: AsyncSession, component_ids: List[str]) -> List[ComponentForAI]:
        """Get full component details for selected component IDs by reusing get_component"""
        components_for_ai = []
        for component_id in component_ids:
            component_response = await ComponentService.get_component(db, component_id)
            if component_response and component_response.is_active:
                components_for_ai.append(
                    ComponentForAI(
                        id=component_response.id,
                        name=component_response.name,
                        description=component_response.description,
                        category=component_response.category,
                        version=component_response.version,
                        activities=component_response.activities,
                        config=component_response.config
                    )
                )
        return components_for_ai

    @staticmethod
    async def list_components(db: AsyncSession, active_only: bool = True) -> List[ComponentResponse]:
        """List all components"""
        query = select(Component)
        if active_only:
            query = query.filter(Component.is_active == True)
        result = await db.execute(query)
        components = result.scalars().all()
        return [
            ComponentResponse(
                id=str(component.id),
                name=component.name,
                description=component.description,
                category=component.category,
                version=component.version,
                is_active=component.is_active,
                activities=component.activities,
                config=component.config,
                created_at=component.created_at,
                updated_at=component.updated_at
            )
            for component in components
        ]
    
    @staticmethod
    async def get_components_for_selection(db: AsyncSession) -> List[ComponentForSelection]:
        """Get minimal component info (id, name, description) for component selection"""
        result = await db.execute(select(Component).filter(Component.is_active == True))
        components = result.scalars().all()
        return [
            ComponentForSelection(
                id=str(component.id),
                name=component.name,
                description=component.description
            )
            for component in components
        ]