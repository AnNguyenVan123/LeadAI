# AI Customer Discovery & Lead CRM

## 1. Project Vision

Build an AI-native SaaS that helps developers, indie hackers, and early-stage founders find people who already experience the problem their startup solves, primarily through Reddit and later other online communities.

The product should evolve from a Reddit lead discovery tool into a full AI-powered lead intelligence and CRM platform.

### Core promise

> Find people who need your product — right when they're looking for it.

### Product positioning

> AI monitors online conversations, detects pain and buying intent, tells you who to talk to, when to reach out, and what to say.

The product is **not** intended to be a mass-spam or mass-DM tool. The focus is highly relevant, contextual, human-in-the-loop outreach.

---

# 2. Problem

Founders often struggle with customer acquisition and customer discovery.

Common workflow:

```text
Build product
    ↓
Launch
    ↓
Try Reddit / X / communities
    ↓
Manually search conversations
    ↓
Open hundreds of posts/comments
    ↓
Guess who might need the product
    ↓
Write messages manually
    ↓
Lose track of conversations
```

The core problem is not a lack of online conversations.

The problem is:

> **Finding the right person at the right moment and understanding why they are a good prospect.**

Reddit contains many people publicly discussing:

- frustrations
- unmet needs
- failed solutions
- requests for recommendations
- urgent problems
- dissatisfaction with existing products
- questions such as "How do I solve X?"
- requests such as "Is there a tool for X?"

These are potential customer signals.

---

# 3. Target Users / ICP

## Initial ICP

Focus on:

- Indie hackers
- Solo founders
- Technical founders
- Developers building SaaS
- Early-stage startup founders

Avoid targeting "all businesses" initially.

## Ideal customer characteristics

The ideal user:

- is actively building a product
- needs early customers or beta users
- does customer discovery manually
- searches communities for potential users
- has limited sales resources
- wants highly relevant prospects rather than large lead lists

---

# 4. Jobs To Be Done

Primary JTBD:

> When I am building a startup, I want to find people who have the problem I am solving, so I can talk to them and acquire my first customers.

Secondary JTBDs:

- Understand whether someone is actually a good prospect.
- Know which leads deserve attention first.
- Know what to say when contacting a prospect.
- Remember previous conversations.
- Know when to follow up.
- Avoid losing promising prospects.
- Turn customer discovery conversations into customers.

---

# 5. Core Product Loop

The product should follow this loop:

```text
DISCOVER
    ↓
QUALIFY
    ↓
ENGAGE
    ↓
NURTURE
    ↓
CONVERT
    ↓
LEARN
    ↓
DISCOVER better leads
```

## Discover

Find relevant posts and comments.

## Qualify

Determine whether the person:

- matches the ICP
- has the target problem
- experiences significant pain
- is actively seeking a solution
- shows buying intent

## Engage

Help the founder start a relevant conversation.

## Nurture

Track conversations and recommend follow-ups.

## Convert

Track trials, demos, signups, and customers.

## Learn

Use user behavior and conversion outcomes to improve lead ranking.

---

# 6. Product Architecture

High-level architecture:

```text
                    ┌─────────────────────┐
                    │      Next.js        │
                    │     Dashboard       │
                    └──────────┬──────────┘
                               │
                              API
                               │
                    ┌──────────▼──────────┐
                    │       FastAPI       │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
       PostgreSQL            Redis          Background Jobs
       + pgvector                              Workers
             │                                    │
             │                                    ├─ Data ingestion
             │                                    ├─ AI analysis
             │                                    ├─ Embeddings
             │                                    └─ Lead scoring
             │
             ▼
        Lead CRM
             │
             ▼
       AI Intelligence
             │
       ┌─────┼──────┐
       ▼     ▼      ▼
      LLM  Embed  Reranker
```

---

# 7. Recommended Technology Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

## Backend

- Python
- FastAPI

## Database

- PostgreSQL
- pgvector initially

Move to Qdrant later if vector-search complexity or scale requires it.

## Cache / Queue

- Redis
- Celery / Dramatiq / RQ or another background-job system

## AI

- LLM API for semantic analysis, classification, summaries, and outreach generation
- Embedding model for semantic retrieval
- Reranker for high-precision candidate ranking

## Analytics

- PostHog or equivalent product analytics

## Payments

- Stripe when monetization is validated

## Deployment

Potential setup:

- Next.js → Vercel
- FastAPI/workers → cloud backend
- PostgreSQL → managed PostgreSQL
- Redis → managed Redis

---

# 8. AI Lead Intelligence Engine

This is the core technical component and potential product moat.

Do not rely on a simple keyword search.

The system should understand the founder's startup and transform it into structured intent.

Example startup:

> "A productivity app for developers who get distracted while waiting for AI coding agents."

AI extracts:

```json
{
  "target_customer": "software developers",
  "problem": "distraction while using AI coding agents",
  "solution": "focus/productivity tool",
  "pain_signals": [
    "doomscrolling",
    "checking Reddit",
    "waiting for AI",
    "loss of focus"
  ],
  "intent_signals": [
    "looking for a tool",
    "asking for recommendations",
    "trying alternatives",
    "expressing frustration"
  ]
}
```

---

# 9. Search Pipeline

Do not send thousands of posts directly to an LLM.

Use a multi-stage pipeline:

```text
Startup idea
    ↓
AI understands ICP + problem
    ↓
Generate search intent
    ↓
Retrieve Reddit candidates
    ↓
Keyword / BM25 search
        +
Semantic embedding search
    ↓
Hybrid retrieval
    ↓
Top 50–100 candidates
    ↓
Reranker
    ↓
Top 20 candidates
    ↓
LLM qualification
    ↓
Top 10 high-quality leads
```

This keeps the system faster and cheaper while allowing expensive AI reasoning to focus on the most promising candidates.

---

# 10. Hybrid Search

Do not use embeddings alone.

Use:

```text
Keyword/BM25
      +
Semantic embeddings
      ↓
Hybrid ranking
      ↓
Reranker
```

Keyword search is useful for exact expressions such as:

- "looking for"
- "any tool"
- "how do I"
- "alternative to"
- "can't find"
- "frustrated with"

Semantic search captures paraphrases and concepts that do not use the exact keywords.

---

# 11. Lead Intent Detection

Intent detection is one of the most important product capabilities.

### Low intent

> "AI coding agents are making developers lazy."

Relevant topic, but weak customer intent.

### Medium intent

> "I keep getting distracted when coding."

Clear pain, but no explicit search for a solution.

### High intent

> "I've tried Forest and Freedom but still end up checking Reddit while waiting for Cursor. Is there anything that automatically blocks distractions?"

Strong signals:

- exact problem
- frustration
- existing solutions tried
- dissatisfaction
- active search for a solution

This should become a high-priority lead.

---

# 12. Lead Scoring

Initial scoring model:

```text
Lead Score =
    Problem Fit
  + Customer / ICP Fit
  + Pain
  + Buying Intent
  + Recency
  + Engagement
```

Example:

```text
Problem Fit       96
Pain              94
Intent            92
ICP Fit           95
Recency           88
Engagement        81
--------------------
Overall           93
```

The exact weighting should be treated as a hypothesis and improved using real conversion data.

---

# 13. Lead Data Model

Each lead should contain structured intelligence:

```json
{
  "lead_id": "...",
  "source": "reddit",
  "profile": "...",
  "problem": "...",
  "pain_level": 0.94,
  "solution_seeking": 0.92,
  "purchase_intent": 0.91,
  "customer_fit": 0.95,
  "recency": 0.88,
  "lead_score": 0.93,
  "existing_solutions": [],
  "recommended_action": "contact_now"
}
```

---

# 14. AI Recommendation Engine

The product should not only say:

> "Here is a lead."

It should say:

> **"Here is what you should do next."**

Examples:

### High intent

```text
🔥 CONTACT NOW

Reason:
The person explicitly asked for a solution
and described the exact problem your product solves.

Recommended action:
Comment first and be helpful.
```

### Medium intent

```text
🟡 MONITOR

Reason:
Strong problem match but no active solution-seeking behavior.

Recommended action:
Monitor future posts/comments.
```

### Low intent

```text
⚪ IGNORE

Reason:
Topic is related but there is insufficient
evidence of pain or intent.
```

---

# 15. Intent Radar

A potential killer feature.

Instead of manually searching Reddit every day:

```text
AI Intent Radar

🔥 12 people need your product NOW
🟠 34 potential leads
🟡 81 conversations to monitor
```

The system continuously identifies newly relevant conversations.

Example alert:

> **New high-intent lead**

> Posted 2 hours ago.

> "Does anyone know an app that automatically blocks Reddit while I'm coding? I keep losing 30 minutes every time my AI agent is generating code."

AI explanation:

```text
ICP fit:             95%
Problem match:       96%
Pain:                94%
Solution intent:     94%
Freshness:           99%

Recommended:
Comment now.
```

---

# 16. Lead CRM

The CRM should track:

```text
New
 ↓
Qualified
 ↓
Contacted
 ↓
Replied
 ↓
Interested
 ↓
Trial
 ↓
Customer
```

The CRM should also track intent independently:

```text
Intent:

🔥 NOW
🟠 HIGH
🟡 MEDIUM
⚪ LOW
```

A lead can therefore be:

```text
Stage: Contacted
Intent: High
Next action: Follow up today
```

---

# 17. Lead Timeline

Every lead should have a chronological timeline.

Example:

```text
Sep 2
🟣 Reddit
User complained about the problem.

Sep 3
🤖 AI detected high intent.

Sep 3
👤 Founder replied.

Sep 4
🟢 Lead replied positively.

Sep 5
🤖 AI recommends mentioning beta.

Sep 5
👤 Founder sent beta link.

Sep 6
🔵 Lead visited website.

Sep 6
🟢 Started trial.
```

This becomes the foundation for lead nurturing.

---

# 18. Conversation Intelligence

AI should understand the entire conversation, not just the latest message.

Example:

```text
Founder:
Hey, saw your comment about Cursor...

Lead:
Yeah, I've tried several productivity apps...
```

AI output:

```text
Intent: HIGH

Objection:
Doesn't like manually starting focus sessions.

Current solution:
Forest.

Opportunity:
Emphasize automatic focus mode.

Recommended next action:
Ask what did not work with Forest.
```

---

# 19. AI Outreach

The AI should generate contextual messages using:

```text
Reddit context
      +
Lead history
      +
Founder/product information
      +
Product knowledge
      +
Brand voice
      ↓
Personalized response
```

Potential modes:

- Helpful / non-promotional
- Casual
- Product mention
- Beta invitation

Default should be helpful and non-pushy.

The founder should review/approve the message before sending.

---

# 20. Lead Memory

Each lead should have persistent context:

```text
Lead
 ├── Reddit posts
 ├── Reddit comments
 ├── Founder replies
 ├── Lead responses
 ├── Website activity
 ├── Trial activity
 └── AI-generated summary
```

Example:

> Sarah is a frontend developer who uses Cursor daily. Her main frustration is losing focus while waiting for AI-generated code. She has tried Forest and Freedom but dislikes manually starting focus sessions.

This prevents the founder from having to reread everything.

---

# 21. RAG / Product Knowledge

Each workspace can contain:

```text
Startup
 ├── Product description
 ├── ICP
 ├── Pricing
 ├── FAQ
 ├── Competitors
 ├── Product docs
 ├── Previous conversations
 └── Brand voice
```

AI uses this information to generate relevant replies and recommendations.

---

# 22. Sources

Initial source:

```text
Reddit
```

Future sources:

```text
Reddit
Hacker News
X
GitHub Discussions
Product Hunt
Online forums
Other communities
```

Use a source abstraction so the core intelligence engine is not tightly coupled to Reddit.

Conceptually:

```python
class LeadSource:
    def search(self, query):
        pass

    def get_conversation(self, id):
        pass

    def get_author(self, id):
        pass
```

All integrations must follow the current terms, API rules, and policies of each platform.

---

# 23. Human-in-the-Loop Outreach

The product should avoid becoming a mass-spam system.

Preferred workflow:

```text
AI detects lead
    ↓
AI explains why
    ↓
AI recommends action
    ↓
AI drafts response
    ↓
Founder reviews
    ↓
Founder sends
    ↓
AI monitors response
    ↓
AI recommends next action
```

This preserves relevance and reduces spam risk.

---

# 24. Validation Strategy

Do not build the complete SaaS before validating demand.

## Phase 1 — Problem validation

Checklist:

- [ ] Define one ICP
- [ ] Find 20–30 founder conversations
- [ ] Collect evidence of customer-acquisition pain
- [ ] Interview 10–15 founders
- [ ] Understand current workflows
- [ ] Identify existing alternatives
- [ ] Identify willingness to pay

Questions:

1. How do you currently find potential customers?
2. How much time do you spend doing this?
3. Where do you look?
4. Have you searched Reddit for potential customers?
5. How do you decide whether someone is a good lead?
6. What happens after finding a lead?
7. How do you follow up?
8. What is the hardest part?
9. Have you paid for tools to solve this?
10. What would make this significantly easier?

Do not lead the interview by pitching the product.

---

# 25. Landing Page Validation

Core headline:

> **Find people who already need what you're building.**

Subheadline:

> AI finds high-intent potential customers on Reddit and online communities, explains why they're a good fit, and helps you start the conversation.

CTA:

> **Find My First Customers**

Secondary message:

> Free during beta · No credit card required

Landing page sections:

1. Hero
2. Product visual
3. Problem
4. How it works
5. Lead intelligence
6. CRM / lead timeline
7. AI follow-up
8. Final CTA

---

# 26. Landing Page Funnel

Track:

```text
Visitors
    ↓
CTA clicks
    ↓
Signup
    ↓
Startup idea submitted
    ↓
ICP submitted
    ↓
Beta interest
```

Do not optimize only for email signups.

A user who submits their startup idea and ICP demonstrates stronger intent than someone who only enters an email address.

---

# 27. Concierge MVP

Before building the full SaaS:

```text
Founder submits startup
        ↓
Manually search Reddit
        ↓
Collect 50–100 candidates
        ↓
AI analyzes candidates
        ↓
Select top 10 leads
        ↓
Create report
        ↓
Send to founder
```

Test with 5–10 founders.

Ask:

- Which leads would you actually contact?
- Which leads are irrelevant?
- Did you contact any?
- Did anyone respond?
- Would you want new leads every week?
- Would you pay for this?

---

# 28. Core Validation Metrics

Important metrics:

### 1. Signup rate

Do people want the product?

### 2. Qualified-lead acceptance rate

Of the leads generated, how many does the founder consider worth contacting?

### 3. Action rate

How many leads does the founder actually contact?

### 4. Reply rate

How many prospects respond?

### 5. Meaningful conversation rate

How many conversations progress beyond a generic response?

### 6. Conversion

How many become:

- beta users
- trials
- customers

The strongest signal is not the number of leads found.

It is:

> **Qualified lead → meaningful conversation → customer**

---

# 29. Pricing Validation

Initial pricing hypotheses can be tested after users experience the value.

Possible plans:

### Free

- Limited leads
- Basic AI scoring

### Pro — ~$29/month

- More leads
- AI scoring
- CRM
- AI outreach
- Follow-up

### Founder — ~$79/month

- More sources
- Higher limits
- Advanced intelligence
- Automation

These prices are hypotheses, not final pricing.

Test willingness to pay before investing heavily in infrastructure.

---

# 30. MVP Scope

## Must have

- [ ] Startup / ICP setup
- [ ] Reddit discovery
- [ ] Hybrid retrieval
- [ ] AI lead scoring
- [ ] Lead explanation
- [ ] Lead list
- [ ] Save lead
- [ ] Lead pipeline
- [ ] AI-generated reply

## Later

- [ ] Intent Radar
- [ ] Continuous monitoring
- [ ] Conversation intelligence
- [ ] AI follow-up
- [ ] Website activity
- [ ] Email
- [ ] Hacker News
- [ ] X
- [ ] GitHub
- [ ] Advanced automation
- [ ] Team collaboration
- [ ] Billing

## Do not build initially

- [ ] Mass automated DM
- [ ] Complex sales automation
- [ ] Multi-source platform
- [ ] Custom ML training
- [ ] Enterprise features
- [ ] Complicated analytics

---

# 31. Technical Development Roadmap

## Stage 0 — Validation

```text
Landing page
    ↓
Waitlist / signup
    ↓
Concierge MVP
    ↓
5–10 users
    ↓
Measure lead quality
```

## Stage 1 — Search MVP

```text
Reddit data
    ↓
Post/comment storage
    ↓
Embeddings
    ↓
pgvector
    ↓
Hybrid retrieval
    ↓
AI ranking
```

## Stage 2 — Lead Intelligence

```text
ICP extraction
    +
Problem extraction
    +
Pain detection
    +
Intent detection
    ↓
Lead scoring
```

## Stage 3 — CRM

```text
Leads
    ↓
Pipeline
    ↓
Timeline
    ↓
Conversation
    ↓
Tasks / follow-ups
```

## Stage 4 — AI Assistant

```text
Conversation
    ↓
Context analysis
    ↓
Next-action recommendation
    ↓
Personalized response
```

## Stage 5 — Intent Radar

```text
Continuous monitoring
    ↓
New conversation
    ↓
AI classification
    ↓
High-intent alert
    ↓
Founder action
```

---

# 32. Long-Term Product Vision

The long-term product is not:

> Reddit scraper.

It is:

> **AI customer acquisition platform for early-stage startups.**

Long-term loop:

```text
        Startup
           ↓
      AI understands
           ↓
      Target customers
           ↓
    Online conversations
           ↓
      Lead discovery
           ↓
    Intent detection
           ↓
       Lead CRM
           ↓
       Outreach
           ↓
       Follow-up
           ↓
       Customer
           ↓
    Conversion data
           ↓
     Better ranking
```

The potential moat is the feedback loop:

```text
Lead characteristics
        ↓
Founder actions
        ↓
Conversation outcomes
        ↓
Trial / purchase
        ↓
Learning
        ↓
Better lead ranking
```

The product should become better at answering:

> **"Who is most likely to become my next customer?"**

rather than simply:

> **"Which Reddit posts are related to my topic?"**

---

# 33. Key Product Principle

### Do not optimize for more leads.

Optimize for:

> **More qualified conversations and customers per lead.**

A system that finds:

```text
10 leads
→ 4 contacted
→ 2 meaningful conversations
→ 1 customer
```

is more valuable than a system that finds:

```text
10,000 leads
→ 0 meaningful conversations
```

---

# 34. Initial Product Thesis

The initial thesis to validate:

> **Founders want an easier way to discover people who are actively experiencing the problem their startup solves. If AI can identify those high-intent people from Reddit conversations with significantly less manual effort, founders will use and potentially pay for the product.**

Secondary thesis:

> **Once those leads are found, founders need help managing conversations, follow-ups, and lead context.**

The first thesis must be validated before investing heavily in the second.

---

# 35. Decision Framework

### BUILD

If:

- Founders repeatedly report customer-discovery pain
- Users submit startup ideas
- AI leads are considered relevant
- Users actually contact leads
- Prospects respond
- Users ask for more leads
- Users want continuous monitoring
- Some users demonstrate willingness to pay

### PIVOT

If:

- Leads are relevant but founders do not contact them
- Reddit is not the preferred source
- Users want customer research rather than lead generation
- Users want a CRM but not discovery

### STOP

If:

- Founders do not have the problem
- Existing workflows are sufficient
- AI lead quality is poor
- Users do not take action on leads
- Nobody demonstrates willingness to pay

---

# 36. First Execution Checklist

## Week 1

- [ ] Define ICP
- [ ] Write problem statement
- [ ] Write 5 validation hypotheses
- [ ] Research 30 founder conversations
- [ ] Interview 10 founders
- [ ] Build landing page
- [ ] Add analytics
- [ ] Launch

## Week 2

- [ ] Get first users
- [ ] Run concierge MVP
- [ ] Manually find leads
- [ ] Deliver lead reports
- [ ] Measure lead quality
- [ ] Measure contact rate
- [ ] Collect feedback

## Week 3

- [ ] Test CRM prototype
- [ ] Test AI follow-up
- [ ] Test pricing
- [ ] Identify strongest use case

## Week 4

- [ ] Decide BUILD / PIVOT / STOP
- [ ] If BUILD: start technical MVP
- [ ] Prioritize search + intent + ranking first
- [ ] Build CRM after proving lead quality

---

# 37. North Star Metric

Primary North Star Metric:

> **Meaningful customer conversations generated per active founder per month.**

Supporting metrics:

- Qualified leads per founder
- Lead acceptance rate
- Contact rate
- Reply rate
- Meaningful conversation rate
- Trial conversion
- Customer conversion
- Retention
