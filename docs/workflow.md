# 🧠 The Correct Conceptual Model

Think of your architecture in **4 clean layers**:

```text
Workflow
   │
   └─ Component (logical unit / business step)
         ├─ Activity 1 (atomic side-effect)
         ├─ Activity 2 (atomic side-effect)
         └─ Activity N (atomic side-effect)
```

### 1️⃣ Workflow

- **Role:** Orchestrator.
- Decides **sequence**, approvals, retries (if needed globally), and state storage.
- Determines which **component** to run for each plan step.
- Does **not know the internal activities** inside a component; just calls “run component”.

---

### 2️⃣ Component

- **Role:** Logical business unit.
- **Contains multiple atomic activities** that together implement a business function.
- **Owns per-activity retry, logging, metrics, audit trail** for its internal activities.
- **Does not perform the actual integration directly**; it delegates to activities via adapters.
- Can be tested independently: component orchestrates its internal activities deterministically.

**Example:** `call_plumber_component`

- Activity 1: `llm_activity` → generate dispatch text
- Activity 2: `plumber_dispatch_activity` → call plumber API
- Activity 3: `human_feedback_activity` → let human verify what’s done

The component orchestrates the internal flow **deterministically**, including retries and logging for each internal activity.

---

### 3️⃣ Activity

- **Role:** Atomic execution unit (one thing only).
- **Durable, observable, retryable** via Temporal.
- Stateless in business logic — receives input, executes, returns output.
- Can be **factory-tested** in isolation using adapters.

**Example:**

- `llm_activity` → call OpenAI API
- `send_notification_activity` → call Resend API
- `generate_pdf_activity` → PDF creation

Activities never know about the bigger business goal; they just do one thing well.

---

### 4️⃣ Adapter

- **Role:** Low-level integration detail.
- Handles API calls, authentication, idempotency, etc.
- Used by activities, not by components or workflow.
- Testable in isolation (mock external system).

---

# ✅ Key Points You’ve Got Right

1. **Component wraps multiple activities** → Correct. Each component can be 1…N activities.
2. **Activities execute only one thing** → Correct. Each activity is atomic.
3. **Component owns per-activity retry, logging, metrics** → Correct. This is what gives you clear observability.
4. **Workflow only orchestrates at component level** → Correct. Workflow doesn’t orchestrate internal activity steps of the component (component does that internally).

---

# ⚡ Visualization

```
Workflow
 └── CallPlumberComponent
       ├── LLMActivity
       │      └── Adapter (OpenAI API)
       ├── PlumberDispatchActivity
       │      └── Adapter (Plumber REST API)
       └── HumanFeedbackActivity
              └── Adapter (internal UI)
```

- Each **activity** is observable in Temporal (you can decide if you expose internal ones or just component-level logs).
- Each **component** can manage internal retries, logging, metrics, and audit trails.
- Workflow orchestrates **components**, not individual activities.

---

# 💡 Recommendation on Your Component DB

Yes — remove the old “API-only” component definition from the DB layer if you’re moving to **business-level components**.

- The new **component abstraction** is higher-level: a container for multiple activities with internal orchestration and observability.
- Activities are now **atomic units** — testable, durable, retryable, pluggable.
- You still can have **dynamic API components** for non-critical integrations, but the new architecture is clean, scalable, and audit-ready.

---

# 🧠 Bottom Line

- Components → **business-level logical unit**, can contain multiple activities, own internal logging, retry, metrics.
- Activities → **atomic execution unit**, only one thing, durable via Temporal.
- Workflow → orchestrates **components**, decides order, approvals, and high-level retries.
- Adapter → low-level implementation detail used by activities.

This gives you:

✔ Per-integration retry
✔ Clear observability
✔ Clean metrics
✔ Strong audit trail
✔ Fault isolation
