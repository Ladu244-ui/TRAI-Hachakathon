Guardrail Sentinel – “Guard the Gates of Your Language Model.” 
Idea Summary: 
�
�
 Creating a prompt injection vulnerability detector for AI agents. The tool will scan 
public/private API endpoints (chatbots, LLMs, etc.), analyze their guardrails, and report 
weaknesses. It will offer automated audits, security reports, and optional alerts or 
subscription services for clients. 
�
�
 Core Features: 
1. Endpoint Discovery & Classification 
2. Prompt Injection Testing Agent 
3. Weakness Analysis & Guardrail Suggestions 
4. Automated Reporting + Ethical Disclosure System 
5. Subscription-based Access & Monitoring Platform 
�
�
 Tech Stack: 
● Frontend: React.js (with TailwindCSS for speed & beauty) 
● Backend: Python (FastAPI for blazing speed and async magic) 
● Cloud AI: Novita.ai – for prompt intelligence, classification, summarization, etc. 
● Vector DB: Zilliz (Milvus) – store test results, prompt patterns, and previous scan 
reports for semantic search. 
● Auth: Firebase/Auth0 (or simple JWT) 
● Infra: Railway / Render / Vercel for deployment 
�
�
 Team Roles & Responsibilities 
�
�
 Developer 1: Backend Architect / Prompt Tester 
● Responsibilities: 
○ Build FastAPI services for: 
■ Endpoint submission 
■ Prompt injection test suite 
■ Novita.ai integration 
○ Interface with Zilliz to store test vectors 
○ Design automated test flows with Python asyncio 
● Best Practices: 
○ Modular service-oriented design 
○ Use Pydantic for data validation 
○ Test endpoints with unescaped inputs, logic bombs, and nested prompt 
structures 
�
�
 Developer 2: LLM Analyst & Novita Integration Lead 
● Responsibilities: 
○ Use Novita.ai for: 
■ Classifying endpoint model type 
■ Summarizing model responses post-attack 
■ Generating guardrail suggestions from reports 
○ Design prompt templates to trigger common vulnerabilities 
● Best Practices: 
○ Use Novita’s prompt classification to auto-suggest risk levels 
○ Cache frequent model responses locally for efficiency 
�
�
 Developer 3: Vector DB & Zilliz Master 
● Responsibilities: 
○ Integrate Zilliz for: 
■ Storing prompt-injection test results 
■ Storing successful/failed exploit patterns as vector embeddings 
■ Enabling fast retrieval of similar vulnerabilities across endpoints 
○ Handle schema design and similarity search queries 
● Best Practices: 
○ Use embedding models (e.g., sentence-transformers) to vectorize 
input/output pairs 
○ Normalize and chunk data for consistent vector quality 
�
�
 Developer 4: Frontend Engineer 
● Responsibilities: 
○ Build a clean, responsive UI: 
■ Submit endpoint → View test results → Generate PDF report 
■ Dashboard for subscriptions and automation 
○ Integrate with backend and auth system 
● Best Practices: 
○ Use Tailwind + React Hooks 
○ Optimize API calls with SWR or React Query 
○ Follow component-based design for reusability 
�
�
 Developer 5: Security & Subscriptions Specialist 
● Responsibilities: 
○ Ethical disclosure workflow: 
■ Email integration for notifications 
■ Templates to inform companies/individuals 
○ Subscription logic: 
■ Automated endpoint re-checks 
■ Notifications and role-based access 
● Best Practices: 
○ Secure API keys with environment variables 
○ Use webhook/event system for automated checks 
○ Log audit history for compliance tracking 
�
�
 24-Hour Execution Plan 
Time Block 
0–2 hrs 
2–6 hrs 
6–10 hrs 
10–14 hrs 
Focus Area 
Design API schema, data flow, and UI wireframes 
Core backend setup + vector DB + frontend 
skeleton 
Novita.ai integration + prompt test suites 
Zilliz vector storage + semantic similarity search 
Dev 
Roles 
All 
1, 3, 4 
1, 2 
2, 3 
14–18 hrs 
Auth, subscription logic + frontend polish 
4, 5 
18–22 hrs 
22–24 hrs 
Final integrations, bug fixes, polish UI/UX 
Deployment + demo prep + presentation 
All 
All 
�
�
 Recommendations & Best Practices 
�
�
 Security First 
● Obfuscate endpoint testing (don’t run tests without consent) 
● Use signed user actions to document permission 
● Encrypt sensitive data at rest (Zilliz supports secure deployment) 
�
�
 Async All the Way 
● Use async def in Python with FastAPI for speed and efficiency 
● Batch test prompts using async calls and asyncio.gather 
�
�
 Vector Intelligence 
● Log failed prompts with embeddings → recommend proactive guardrails 
● Build a “pattern bank” to auto-match and flag similar endpoints 
�
�
 Lean into Monetization 
● Free basic scan 
● Premium: Scheduled audits, detailed reports, direct email disclosures 
● Partner program: Let security firms subscribe and monitor clients 
�
�
 Potential Novita.ai Use Cases 
● Classify model type: Is it ChatGPT? Claude? Open-source? 
● Summarize model replies for clarity in reports 
● Generate human-readable explanations for technical issues 
�
�
 Stretch Goals (if ahead of time) 
● Real-time model monitoring 
● Browser extension to test LLMs on websites 
● Slack/email bot for alerts