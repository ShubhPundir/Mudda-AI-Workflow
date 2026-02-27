# Architecture Decisions

This document captures the architectural rationale behind design patterns used within the application, specifically focusing on the intersection of service integration, dependency injection, and Temporal.io activity execution.

---

## 1. Factory & Adapter Pattern

The application utilizes the **Factory** and **Adapter** patterns for all infrastructure boundary integrations (e.g., LLM generation, PDF rendering, Email dispatching, and external API requests).

### Why the Adapter Pattern?
The core business logic of the application (such as Temporal workflows and activities) must remain agnostic to the specific external providers being used. 

* **Without Adapters:** If an activity directly imports and uses the `resend` SDK or the `google.genai` SDK, swapping providers (e.g., moving from Resend to AWS SES, or Gemini to OpenAI) requires rewriting and retesting core business activities.
* **With Adapters:** We define a consistent abstract interface (e.g., `EmailService` or `LLMService`). The business logic interacts exclusively with this interface. Concrete adapter classes wrap the specific provider SDKs and fulfill the contract. This allows us to swap providers purely through configuration (e.g., changing `.env` variables) with zero risk to workflow stability.

### Why the Factory Pattern?
Factories act as the central decision-making hub for *which* adapter to instantiate based on environment configuration. Instead of activities checking environment variables like `EMAIL_PROVIDER == "aws_ses"`, the factory handles this logic and returns the pre-configured adapter.

---

## 2. Managing Object Lifecycles (Singleton vs. Instance per Call)

Temporal activities are executed repeatedly inside long-running worker processes. If our factories instantiated a *new* service client on every single activity execution, it would result in:
1. **Memory Bloat:** Continually allocating heavy SDK client objects.
2. **Connection Exhaustion:** Opening new HTTP/TCP connection pools to external providers rather than reusing existing ones.
3. **Performance Degradation:** Repeatedly executing initialization logic (like parsing credentials).

To prevent this, the service adapters must act as **Singletons**—only one instance of each adapter should exist per Python process.

---

## 3. The Implementation Choice: Class-Level Caching vs. Singleton Objects

When implementing the Singleton pattern for these factories in Python, we had two distinct approaches. 

### Approach A: The Singleton Factory Object
In this approach, we force the Factory *itself* to be a Singleton object, and we access the service through an instance of that factory.

```python
# The Singleton Factory Object
class LLMFactory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
            cls._instance.service = None 
        return cls._instance

    def get_llm_service(self) -> LLMService:
        if self.service is None:
             self.service = GeminiLLMAdapter()
        return self.service

# Usage
factory = LLMFactory() # Returns the same factory object every time
_llm_service = factory.get_llm_service()
```

### Approach B: The Static Factory with Class-Level Caching (Chosen Approach)
In this approach, the Factory remains a static namespace (we never instantiate it), and we cache the instantiated adapter directly on the class itself using `@classmethod`.

```python
# The Static Factory Class
class LLMFactory:
    _service_instance = None

    @classmethod
    def get_llm_service(cls) -> LLMService:
        if cls._service_instance is None:
            cls._service_instance = GeminiLLMAdapter()
        return cls._service_instance

# Usage
_llm_service = LLMFactory.get_llm_service()
```

---

## Rationale for Choosing Approach B (Static Factory with Class-level Cache)

We chose **Approach B** for the codebase for the following pragmatic and objective reasons:

**1. The "Pythonic" Philosophy (Simplicity over Indirection)**
In languages like Java or C#, making a Factory a singleton object is often necessary because all state and logic *must* belong to an object instance. In Python, however, **classes themselves are objects** that can hold state natively (like `cls._service_instance`). Creating a Singleton Factory object *just* to manage a Singleton Service object introduces unnecessary indirection (a singleton managing a singleton).

**2. Zero Refactoring for Consumers**
Activities were already invoking static methods like `LLMFactory.get_llm_service()`. By using Approach B, we injected Singleton caching into the deepest layer of the factories without requiring a single line of code change in consuming activities or routers. Approach A would have required updating all consumers to instantiate the factory first (`LLMFactory().get_llm_service()`).

**3. State Encapsulation Alignment**
A factory's specialized job is strictly to evaluate context and route instantiation requests. It has no long-lived behavioral state of its own (e.g., it doesn't hold TCP sockets, database connection strings, or process data). Because the factory has no distinct lifecycle state that requires instance encapsulation, instantiating it provides zero architectural value.

**4. Performance**
While the performance difference is extremely microscopic, Approach B is technically faster. It resolves the class attribute once and completely bypasses the overhead of intercepting Python's `__new__` initialization sequence every time a module imports the service.

### Conclusion
The Class-Level Caching static factory prevents memory bloat while preserving a clean, functional API that aligns tightly with Python's object model natively without Java-style boiler-plating.
