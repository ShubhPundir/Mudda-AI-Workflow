import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List

logger = logging.getLogger(__name__)

class ExecutionEventBus:
    """
    In-memory async event bus for workflow execution status updates.
    Allows multiple SSE clients to subscribe to updates for a specific execution_id.
    """
    def __init__(self):
        # Map of execution_id -> list of subscriber queues
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, execution_id: str) -> AsyncGenerator[str, None]:
        """
        Subscribe to events for a specific execution_id.
        Yields SSE-formatted strings.
        """
        queue = asyncio.Queue()
        async with self._lock:
            if execution_id not in self._subscribers:
                self._subscribers[execution_id] = []
            self._subscribers[execution_id].append(queue)
            logger.info("New subscriber for execution_id=%s. Total: %d", 
                        execution_id, len(self._subscribers[execution_id]))

        try:
            while True:
                event = await queue.get()
                if event is None:  # Sentinel to close connection
                    break
                
                event_type = event.get("event", "message")
                data = event.get("data", {})
                
                yield f"event: {event_type}\n"
                yield f"data: {json.dumps(data)}\n\n"
        finally:
            async with self._lock:
                if execution_id in self._subscribers:
                    self._subscribers[execution_id].remove(queue)
                    if not self._subscribers[execution_id]:
                        del self._subscribers[execution_id]
                    logger.info("Subscriber disconnected from execution_id=%s", execution_id)

    async def publish(self, execution_id: str, event_type: str, data: dict):
        """
        Publish an event to all subscribers of a specific execution_id.
        """
        async with self._lock:
            if execution_id in self._subscribers:
                event = {"event": event_type, "data": data}
                for queue in self._subscribers[execution_id]:
                    await queue.put(event)

    async def close_stream(self, execution_id: str):
        """
        Send sentinel to all subscribers to close their connections.
        """
        async with self._lock:
            if execution_id in self._subscribers:
                for queue in self._subscribers[execution_id]:
                    await queue.put(None)

# Singleton instance
execution_event_bus = ExecutionEventBus()
