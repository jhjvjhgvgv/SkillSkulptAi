# SkillSculpt AI — Adaptive Micro-Learning Platform

SkillSculpt AI delivers personalized 5-minute learning modules ("Micro-Sculpts") powered by a lightweight recommendation engine. This repository contains a FastAPI prototype with in-memory storage that showcases the core personalization loop.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API locally:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
4. Open the interactive docs at http://localhost:8000/docs.

### Example flow

```bash
# Create a user profile
curl -X POST http://localhost:8000/users \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "u1",
    "name": "Ava",
    "role": "sales",
    "learning_style": "auditory",
    "gaps": ["security", "pricing"],
    "strengths": ["demo delivery"]
  }'

# Add two micro-sculpts
curl -X POST http://localhost:8000/sculpts \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "s1",
    "title": "Security Basics for Sales",
    "role_tags": ["sales"],
    "topics": ["security"],
    "modality": "auditory"
  }'

curl -X POST http://localhost:8000/sculpts \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "s2",
    "title": "Pricing Objections",
    "role_tags": ["sales"],
    "topics": ["pricing"],
    "modality": "visual"
  }'

# Request ranked recommendations
curl http://localhost:8000/recommendations/u1

# Record a completion with score, objective, and format context
curl -X POST "http://localhost:8000/events?user_id=u1&sculpt_id=s1&score=0.6&objective_id=CMP-Q3-DRP&hesitation=true&failure_reason=confused%20compliance%20dates&content_format=article"

# Fetch progress snapshot
curl http://localhost:8000/progress/u1

# Get the latest knowledge gap payload (used to prime generation prompts)
curl http://localhost:8000/knowledge-gap/u1
```

## Architecture

- **FastAPI app (`app/main.py`)** — exposes routes for users, micro-sculpts, recommendations, knowledge gaps, and progress tracking.
- **Personalization (`app/personalization.py`)** — ranks micro-sculpts by learning style, skill gaps, role alignment, and urgent objectives derived from knowledge-gap analysis, returning rationales alongside each recommendation.
- **Models (`app/models.py`)** — Pydantic schemas for users, micro-sculpts, learning events, recommendations, and knowledge-gap payloads (with formatted prompt helpers).
- **In-memory store (`app/store.py`)** — simple persistence for prototyping; replace with a database or vector store for production.

## Deployment checklist

The prototype runs locally with `uvicorn`, but deploying it for real users requires a few additional pieces:

1. **Runtime & process management**
   - Use Python 3.11+ and run behind a production ASGI server, e.g.
     ```bash
     gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --log-level info
     ```
   - Place it behind a reverse proxy (NGINX, ALB) to handle TLS termination and request buffering.

2. **Configuration & secrets**
   - Provide environment variables for `PORT`, `LOG_LEVEL`, database URLs, and any API keys (manage secrets with your cloud provider or Vault—do not hardcode).

3. **Persistent storage**
   - Swap `InMemoryStore` for a durable backend (e.g., Postgres for user/state data plus Redis or a vector store for content/embedding search).
   - Run migrations or bootstrap scripts to seed starter micro-sculpts and roles.

4. **Observability**
   - Enable structured logging, request metrics, and traces (e.g., OpenTelemetry) and set up alerts on latency, error rate, and recommendation throughput.
   - Add a container/image health check that calls `/health`.

5. **Security & compliance**
   - Enforce HTTPS, CORS rules, and authentication (API key or JWT) on all non-health endpoints.
   - Apply rate limits and audit logging, especially for enterprise tenants.

6. **Scaling & resilience**
   - Use horizontal auto-scaling on CPU/latency, and configure timeouts/retries between the API layer and downstream stores.
   - Add background jobs or a task queue for heavier personalization/model updates so the API stays responsive.

## Testing

Run unit tests for the recommendation logic:

```bash
pytest
```

## Business context

### I. Core Value Proposition

#### Problem Solved
Professionals and businesses struggle with one-size-fits-all training platforms that have low engagement and poor knowledge retention, wasting time and money.

#### Unique Solution
A micro-learning platform that uses a proprietary AI model to continuously analyze user performance, learning style, and real-world job role to instantly generate personalized, 5-minute learning modules (Micro-Sculpts).

#### Core Value
Maximum Knowledge Retention in Minimum Time. Users only learn exactly what they need, exactly when they need it.

### II. Customer Segments & Relationships

#### Target Customers (B2B Focus)
Mid-to-large-sized enterprises in high-stakes, rapidly changing industries (e.g., Financial Services, Tech/SaaS, Healthcare), specifically targeting HR/Training departments and department heads.

#### Early Adopters
SaaS sales teams who require rapid, up-to-date training on new product features and compliance regulations.

#### Customer Relationships
- **High-touch:** Dedicated account manager for enterprise clients.
- **Low-touch:** In-app AI chatbot for immediate user support and learning guidance.

### III. Channels & Key Metrics

#### Channels (How We Reach Customers)
- **Direct Sales:** Targeted B2B outreach to HR/Training departments.
- **Integrations:** API partnerships with existing HRIS/LMS platforms (e.g., Workday, Cornerstone).
- **Thought Leadership:** Publish white papers on the ROI of adaptive learning and AI in L&D.

#### Key Metrics
- Active Daily/Monthly Users (ADU/MAU).
- Knowledge Retention Score (KRS): Proprietary score tracking how well users remember and apply learned material.
- Enterprise Churn Rate: Rate at which companies renew their annual subscription.

### IV. Revenue Streams & Cost Structure

#### Revenue Streams (Subscription-Based Model)
- **Starter/Standard Tier:** Per-user/per-month fee for access to the core platform and basic analytics.
- **Enterprise Tier (Premium):** Higher per-user fee for custom AI model training on company-specific content, dedicated API integration support, and advanced analytics/executive reporting dashboards.
- **Consulting Services (Add-On):** One-time fee for initial content migration and custom curriculum design.

#### Cost Structure
- **Key Fixed Costs:** Salaries for AI engineers, data scientists, and product developers.
- **Key Variable Costs:** Cloud hosting/compute costs for running personalization algorithms that scale with active users.
- **Sales/Marketing:** Customer acquisition costs for high-value enterprise customers.

### V. Key Activities, Resources & Partners

#### Key Activities
AI model maintenance and improvement, content curation/vetting, and ensuring platform reliability/uptime.

#### Key Resources
Proprietary AI algorithm, expert content library, and data on user learning patterns.

#### Key Partners
Content providers/subject matter experts for course expansion and HRIS/LMS platforms for seamless data integration.

#### Unfair Advantage
A continuous feedback loop: every user interaction improves the AI model, strengthening the personalization engine and creating a moat that static-content competitors cannot replicate.
