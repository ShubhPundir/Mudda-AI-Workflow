"""
Temporal worker for executing Mudda AI workflows
"""
import asyncio
import os
from temporal_workflows import start_temporal_worker


async def main():
    """Start the Temporal worker"""
    print("Starting Mudda AI Temporal Worker...")
    print("=" * 50)
    
    # Check environment variables
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    print(f"Temporal Host: {temporal_host}")
    print(f"Temporal Namespace: {temporal_namespace}")
    print(f"Task Queue: mudda-ai-workflows")
    print("\nWorker is starting...")
    
    try:
        await start_temporal_worker()
    except KeyboardInterrupt:
        print("\nWorker stopped by user")
    except Exception as e:
        print(f"Worker error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
