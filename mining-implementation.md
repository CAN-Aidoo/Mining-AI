# Mining — Full Implementation Guide

> From idea to working platform. This document covers every step needed to design, build, test, and scale Mining as an AI engineer.

---

## Overview

Mining is built in six sequential phases. Each phase has a clear goal, a set of tasks, decisions to make, and a definition of done so you know when to move to the next phase. No phase should be skipped — each one feeds the next.

| Phase | Focus | Goal |
|---|---|---|
| 1 | Research Library | Build the knowledge foundation |
| 2 | Documentation Engine | Generate academic documents |
| 3 | AI Prototype Builder | Turn docs into working software |
| 4 | Student Testing | Validate with real users |
| 5 | CAD & Automation Outputs | Expand prototype types |
| 6 | Institutional Licensing | Scale through universities |

---

## Phase 1 — Define the Research Library Structure

### Goal
Build the knowledge backbone that Mining pulls from when a student types their project idea. Without good sources, everything downstream is weak.

---

### 1.1 Decide What the Library Needs to Contain

The research library needs four types of content:

**Academic Papers** — peer-reviewed research from open-access journals. These provide the citations students need for their literature review.

**Past Student Projects** — summaries of final year projects from previous years, organized by topic and field. These show Mining what successful project structures look like.

**Datasets** — publicly available datasets that students can reference or use in their prototypes (e.g., Kaggle, UCI, government open data).

**Field Templates** — structured outlines for what a final year project document looks like in each academic discipline. These are the formatting rules Mining writes inside.

---

### 1.2 Identify Open-Access Academic Sources to Index

These are the sources Mining will connect to and pull papers from. All of them are free and legally accessible:

**General Academic Sources**
- **Semantic Scholar** — AI-powered academic search engine with a public API. Best starting point.
- **OpenAlex** — open catalog of scholarly works, authors, and institutions. Has a clean REST API.
- **arXiv** — preprint server for CS, engineering, mathematics, and related fields. Essential for AI topics.
- **CORE** — aggregates open-access research from universities worldwide. Good for breadth.
- **PubMed Central** — open-access biomedical and health sciences literature. Needed for health field.
- **DOAJ (Directory of Open Access Journals)** — indexes thousands of peer-reviewed open journals across all fields.

**Engineering & Technical Sources**
- **IEEE Xplore Open Access** — select IEEE papers available without a paywall.
- **SpringerOpen** — open-access journals from Springer, covering engineering and applied science.

**Business & Social Sciences**
- **SSRN** — preprints in economics, business, and social sciences.
- **RePEC** — research in economics and related disciplines.

**Past Project Sources**
- **EThOS (British Library)** — UK theses and dissertations, open access.
- **DART-Europe** — European theses.
- **ProQuest Open Access** — selected dissertations available free.
- University institutional repositories (many are publicly accessible via their websites).

---

### 1.3 Design the Library Data Structure

Every item stored in the research library should have a consistent structure so Mining can retrieve, rank, and display it correctly.

**For Academic Papers, store:**
- Title
- Authors
- Abstract
- Field / Subfield tags
- Keywords
- Publication year
- Source (journal or conference name)
- DOI or URL
- Full text or summary (where available)

**For Past Student Projects, store:**
- Project title
- Field / Subfield
- Problem statement summary
- Methodology used
- Tools or technologies involved
- Outcome summary
- Institution (if available)
- Year

**For Datasets, store:**
- Dataset name
- Description
- Field relevance tags
- Source URL
- Format (CSV, JSON, image, etc.)
- Size and update frequency

---

### 1.4 Design the Retrieval Logic

When a student types their project idea, Mining needs to find the most relevant content from the library. The retrieval process works in three steps:

**Step 1 — Keyword and Topic Extraction**
Mining reads the student's input and extracts the core topic, field, and key concepts. For example: *"I want to build a machine learning model to detect malaria from blood slide images"* extracts: field = health/CS, topic = disease detection, method = machine learning, domain = medical imaging.

**Step 2 — Semantic Search**
Mining runs a semantic search over the library using embeddings — not just keyword matching. This means a student who types "detect fake news using AI" still finds papers about "misinformation classification with NLP" even if they used different words.

The tool to use for this is a vector database. Good options at this stage: **ChromaDB** (simple, local-first) or **Pinecone** (managed cloud). Papers and project summaries are converted into vector embeddings when they are indexed, and the student's query is converted the same way at search time.

**Step 3 — Ranking and Filtering**
Results are ranked by relevance score and filtered by field. The top 10–15 sources are passed to the documentation engine in Phase 2.

---

### 1.5 Build the Indexing Pipeline

The indexing pipeline is the background process that keeps the library up to date. It runs on a schedule and does three things:

1. Fetches new papers from the connected APIs (Semantic Scholar, OpenAlex, arXiv, etc.) based on predefined field topics
2. Processes each paper — extracts title, abstract, keywords, and generates an embedding
3. Stores the result in the vector database and a structured metadata database

This does not need to run in real time. A weekly or daily refresh is sufficient at the start.

---

### Phase 1 — Definition of Done

- [ ] Research library structure defined for papers, projects, and datasets
- [ ] At least 5 open-access sources identified and API access confirmed
- [ ] Vector database selected and set up
- [ ] Indexing pipeline built and running for at least 2 fields (CS and engineering)
- [ ] Semantic search returning relevant results for 10 test queries
- [ ] Library contains at least 500 indexed papers across all target fields before Phase 2 begins

---

---

## Phase 2 — Build the Documentation Engine

### Goal
Take a student's project idea and the research retrieved in Phase 1 and produce a complete, properly structured final year project document — ready to submit or refine.

---

### 2.1 Define the Document Structure

A standard final year project document has consistent sections regardless of field. Mining needs to know what these sections are and what belongs in each one.

**Standard Final Year Project Document Structure:**

1. **Title Page** — project title, student name, institution, department, year
2. **Abstract** — 250–350 word summary of the entire project
3. **Table of Contents** — auto-generated
4. **Introduction** — background, motivation, problem statement, project objectives, scope
5. **Literature Review** — review of existing work, with citations, grouped by theme
6. **Methodology** — how the project will be carried out, tools, approach, design decisions
7. **System Design / Project Design** — architecture, diagrams, workflows (for technical projects)
8. **Expected Results / Outcomes** — what success looks like
9. **Timeline / Project Plan** — milestones and schedule (Gantt chart description)
10. **References** — formatted bibliography using APA or IEEE style (field-dependent)

---

### 2.2 Build Field-Specific Templates

Each academic field has slightly different conventions. Mining needs at least four templates at launch.

**Computer Science Template**
Methodology section focuses on software development lifecycle, tools (languages, frameworks, APIs), system architecture, and testing strategy. System Design section includes data flow diagrams and component diagrams. References default to IEEE format.

**Engineering Template**
Methodology section focuses on design process, materials, simulations, and standards compliance. System Design section includes CAD references, schematics, and test conditions. References default to IEEE or APA depending on the institution.

**Business / Management Template**
Methodology section focuses on research approach (qualitative vs quantitative), data collection methods (surveys, interviews), and analysis framework. No system design section — replaced by a Business Analysis section. References default to APA format.

**Health Sciences Template**
Methodology section focuses on study design, ethical considerations, data collection, participant criteria, and analysis methods. Includes an Ethics section. References default to APA or Vancouver format.

Each template is stored as a structured prompt that the language model fills in based on the student's input and the retrieved research.

---

### 2.3 Define the Generation Workflow

The documentation engine runs in this sequence when a student submits their idea:

**Step 1 — Input Collection**
Mining collects from the student:
- Project idea (free text)
- Academic field (CS, Engineering, Business, Health — selected from a dropdown)
- Institution name (optional, for formatting)
- Supervisor name (optional)
- Submission deadline (optional, used for the timeline section)

**Step 2 — Research Retrieval**
Phase 1's retrieval system fetches the top 10–15 relevant sources based on the project idea.

**Step 3 — Document Generation**
Mining passes the following to the language model:
- The student's project idea
- The retrieved research (titles, abstracts, key points)
- The field-specific template as a structural guide
- Instructions to write in formal academic English, use the retrieved sources as citations, and stay within the template structure

The model generates each section sequentially. Longer sections like the literature review are generated with the retrieved paper abstracts as direct context so citations are grounded in real sources.

**Step 4 — Citation Formatting**
After generation, Mining formats all in-text citations and the reference list using the correct style for the field. This is done programmatically using the metadata stored for each source (author, year, title, journal, DOI).

**Step 5 — Review and Edit**
The generated document is displayed to the student section by section. The student can:
- Accept a section as written
- Ask Mining to rewrite a section with different emphasis
- Manually edit the text

**Step 6 — Export**
Once the student approves all sections, Mining exports the document as a formatted PDF or Word file, following the institution's standard layout.

---

### 2.4 Handle the "No References Found" Case

Some very niche or local topics may not return enough relevant papers from the research library. Mining handles this in two ways:

First, it broadens the search — if "soil erosion detection in Northern Ghana" returns few results, Mining expands to "soil erosion detection using remote sensing" and "environmental monitoring AI" and uses those as the literature base.

Second, it flags this to the student — Mining tells the student which sources it used and notes that the literature review is based on related work rather than direct topic matches, so the student can make an informed decision about whether to broaden their topic or seek additional sources.

---

### 2.5 Quality Rules for Generated Documents

The documentation engine should follow these rules to ensure output quality:

- Every claim in the literature review must be tied to a retrieved source. No hallucinated references.
- The abstract must accurately summarize the sections below it — generate it last, not first.
- The methodology section must match the field template — a health project should not describe software architecture.
- References must be real DOIs or URLs confirmed in the metadata database. If a paper has no confirmed DOI, it is cited with available metadata only and flagged for the student to verify.
- Word counts per section should follow academic norms — literature review 800–1500 words, methodology 600–1000 words, etc.

---

### Phase 2 — Definition of Done

- [ ] Four field templates built and tested (CS, Engineering, Business, Health)
- [ ] Document generation workflow running end to end for all four fields
- [ ] Citation formatting working correctly for APA and IEEE
- [ ] Export to PDF and Word working with proper formatting
- [ ] 20 test documents generated across all four fields and reviewed for quality
- [ ] "No references" fallback logic working
- [ ] A student with no technical knowledge can go from idea to full draft in under 10 minutes

---

---

## Phase 3 — Develop the AI Software Prototype Builder

### Goal
After documentation is complete, Mining builds a working AI software prototype that demonstrates the student's idea — something they can open, interact with, and present. This is the most technically demanding phase and the biggest differentiator of the platform.

---

### 3.1 Define What "Working Prototype" Means for a Student

A student prototype does not need to be production-ready. It needs to be:

- **Functional** — it runs and does what it claims to do
- **Demonstrable** — the student can show it working in a presentation
- **Honest** — it clearly represents the scope of a student project, not a commercial product
- **Self-contained** — no complex setup required, ideally runs in a browser or with one click

The bar is: *"Does this prove the idea works?"* — not *"Is this ready to ship?"*

---

### 3.2 Define the Prototype Types Within AI Software

Not every AI project is the same. Mining needs to recognize what kind of AI software the student's project calls for and generate the right type of prototype. The main categories:

**Classifier / Prediction Tool**
Student's idea involves predicting or classifying something. Examples: disease detection from images, spam email detection, student grade prediction, loan default prediction. Output: a simple interface where a user inputs data and receives a prediction with a confidence score.

**Recommendation System**
Student's idea involves suggesting items to users. Examples: book recommendation, crop recommendation based on soil data, course recommendation. Output: interface where a user enters preferences or inputs, and receives a ranked list of recommendations.

**Chatbot / Conversational AI**
Student's idea involves a question-answering system or assistant. Examples: university FAQ bot, mental health support assistant, customer service bot for a local business. Output: a simple chat interface connected to a language model or knowledge base.

**Data Dashboard / Analytics Tool**
Student's idea involves analyzing and visualizing a dataset to surface insights. Examples: COVID-19 trend analysis, crime pattern visualization, agricultural yield dashboard. Output: an interactive dashboard with charts, filters, and summary statistics built from the student's chosen dataset.

**Text Processing Tool**
Student's idea involves working with text — summarization, sentiment analysis, translation, plagiarism detection. Output: an interface where a user pastes or uploads text and receives a processed result.

---

### 3.3 Design the Prototype Generation Workflow

**Step 1 — Prototype Type Detection**
After documentation is complete, Mining reads the project's problem statement, methodology, and system design sections and determines which prototype type applies. This is done by the language model with a structured classification prompt. Mining presents its determination to the student and asks them to confirm or correct it.

**Step 2 — Input Specification**
Mining asks the student a small set of clarifying questions depending on the prototype type:

For a classifier: *"What data will your model use as input? Do you have a dataset, or should Mining use a sample dataset for demonstration?"*

For a chatbot: *"What is the main topic your chatbot should answer questions about? Do you want to upload reference documents for it to use?"*

For a dashboard: *"What dataset should the dashboard visualize? Please upload it or select from our sample datasets."*

Mining keeps these questions simple and gives sample answers so students understand what is being asked.

**Step 3 — Prototype Assembly**
Mining selects the appropriate prototype template for the detected type and fills it in with the student's project-specific details. Each template is a pre-built application structure with configurable components:

- The model type (if classifier: what algorithm to use, what features to accept)
- The interface layout (what the user sees and interacts with)
- The dataset (the student's uploaded data or a relevant sample dataset from the library)
- The branding (project name, student name, field colors)

**Step 4 — Deployment**
Mining deploys the prototype to a shareable link that the student can open in any browser. No installation required. The link is valid for the duration of the student's subscription. The student can also download the prototype as a package.

**Step 5 — Prototype Report**
Mining generates a one-page Prototype Validation Report that the student can include as an appendix in their project document. It describes what the prototype does, how it was built, what data it used, and what results it produced. This bridges the documentation and the working software.

---

### 3.4 Handle Dataset Requirements

Prototypes need data to work. Mining handles data in three ways:

**Student uploads their own dataset** — the student collected or found data relevant to their project. Mining validates the format, previews it, and uses it.

**Student selects from the sample dataset library** — Mining maintains a curated set of freely available datasets organized by topic (health, agriculture, education, finance, transport, etc.). The student picks the most relevant one as a stand-in for real data.

**Mining generates synthetic data** — for projects where no suitable dataset exists, Mining generates a synthetic dataset that follows the statistical properties the project describes. This is clearly labeled as synthetic and the student is told to replace it with real data before final submission.

---

### 3.5 What the Prototype Builder Does Not Do

Be clear about scope to avoid over-promising:

- It does not train custom deep learning models from scratch (too slow and compute-heavy for this stage)
- It does not produce mobile apps or native desktop software
- It does not handle real-time data streams or live integrations
- It does not write custom algorithms — it uses existing libraries and models

The prototype demonstrates the concept using pre-trained models, available APIs, and sample data. That is sufficient for a final year project demonstration.

---

### 3.6 Technology Approach for the Prototype Builder (No Code Details)

At the architectural level, the prototype builder works by:

1. Using pre-built application templates for each prototype type (classifier, chatbot, dashboard, etc.)
2. Filling in the configurable parts of each template using the student's project details
3. Connecting the appropriate AI service or library (a pre-trained model, an LLM API, a charting library)
4. Wrapping it in a simple web interface
5. Deploying it to a hosting environment Mining controls

The key principle: Mining is assembling and configuring, not generating code from scratch. This makes it faster, more reliable, and easier to maintain.

---

### Phase 3 — Definition of Done

- [ ] Five prototype types built as configurable templates: classifier, recommendation, chatbot, dashboard, text processing
- [ ] Prototype type detection working correctly for 15 test project descriptions
- [ ] Input collection workflow complete for all five types
- [ ] All five templates deployable to a shareable link in under 5 minutes
- [ ] Sample dataset library contains at least 20 datasets across the four academic fields
- [ ] Synthetic data generation working for structured tabular data
- [ ] Prototype Validation Report generating correctly
- [ ] A student with no coding knowledge can get a working demo from a completed document in under 15 minutes

---

---

## Phase 4 — Test with a Small Cohort of Real Students

### Goal
Validate that Mining works for actual students doing actual projects. Find what breaks, what confuses people, and what genuinely helps — then fix it before scaling.

---

### 4.1 Recruit the Test Cohort

Target 20–30 final year students for the first test round. Aim for representation across all four fields (CS, Engineering, Business, Health) and a mix of project types and confidence levels.

Where to find them:
- Direct outreach to final year students at one or two local universities
- Posts in student groups on WhatsApp, Telegram, or LinkedIn
- Contact with lecturers or project supervisors who can recommend students
- Offer free access to Mining for the duration of their project in exchange for structured feedback

Ideal cohort breakdown: 8 CS students, 7 engineering students, 8 business students, 7 health sciences students.

---

### 4.2 Define What You Are Testing

Do not test everything at once. In Phase 4, test these specific things:

**Research Library Quality**
Are the retrieved papers actually relevant to each student's topic? Do students feel the references are appropriate for their field?

**Documentation Accuracy**
Is the generated document structured correctly? Does it match what their institution expects? Are the citations real and correctly formatted?

**Prototype Usefulness**
Does the generated prototype actually demonstrate the student's idea? Can the student present it to a supervisor without embarrassment?

**Workflow Ease**
Can a student complete the full flow — from typing their idea to having a document and a prototype — without needing help or getting confused?

**Time Savings**
Ask students to estimate how long the same work would have taken without Mining. Compare to actual time spent using Mining.

---

### 4.3 Structure the Testing Process

**Week 1 — Onboarding**
Bring students onto the platform. Walk them through the flow in a 30-minute group session. Answer questions. Let them start their projects.

**Weeks 2–4 — Active Use**
Students use Mining for their actual final year projects. No hand-holding. They use it as if it were a real tool they found on their own. Collect usage logs (with consent) — which features they use, where they drop off, how long each step takes.

**Week 5 — Structured Feedback**
Run structured interviews or send a detailed feedback form covering:
- What worked well
- What confused them or slowed them down
- What they wish Mining did differently
- Whether they would pay for it (and how much)
- Whether they would recommend it to other students

**Week 6 — Analysis and Iteration**
Analyze feedback. Rank issues by frequency and severity. Fix the top 10 issues before Phase 5 begins.

---

### 4.4 Key Metrics to Track

| Metric | Target |
|---|---|
| Time from idea to full document draft | Under 15 minutes |
| Time from document to working prototype | Under 15 minutes |
| Student satisfaction score (1–10) | 7 or above |
| % who say references were relevant | 80% or above |
| % who successfully got a working prototype | 90% or above |
| % who say they would pay for it | 60% or above |
| % who would recommend it to peers | 70% or above |

---

### 4.5 Common Issues to Anticipate

**Niche topics with few references** — some students will have very specific local topics. The fallback logic from Phase 2 will be tested hard here. Expect to refine it.

**Wrong prototype type detected** — the classifier might misread a chatbot project as a text processing tool. Improve the detection prompt based on real examples of where it fails.

**Document does not match their institution's format** — different universities have slightly different requirements. Plan to add a custom template option after Phase 4.

**Students trying to game the system** — some students will ask Mining to write their entire dissertation for them without any real input. Decide how Mining should handle minimal or low-quality inputs (ask clarifying questions, require more detail before proceeding).

---

### Phase 4 — Definition of Done

- [ ] 20–30 students recruited and onboarded
- [ ] All students completed the full flow at least once
- [ ] Structured feedback collected from at least 80% of cohort
- [ ] Top 10 issues identified and fixed
- [ ] All key metrics at or above target
- [ ] At least 5 detailed case studies documented (one per field + one cross-field)
- [ ] Pricing willingness data collected

---

---

## Phase 5 — Add CAD and Automation Diagram Outputs

### Goal
Expand the prototype builder beyond AI software to serve engineering students (who need CAD/simulation outputs) and business/systems students (who need process diagrams and automation flows). This doubles the student base Mining can serve.

---

### 5.1 CAD and Engineering Simulation Output

Engineering students need to demonstrate designs — bridges, mechanical components, circuit boards, HVAC systems, structural frames. A full CAD file is complex to generate, but Mining can provide meaningful engineering prototype outputs without building a full CAD engine.

**What Mining will produce for engineering projects:**

**Parametric Design Summaries** — structured technical specifications in the format that engineering CAD tools (like FreeCAD, Fusion 360, or AutoCAD) would use as inputs. The student gets a document they can use to build or commission the actual CAD model.

**Simulation Reports** — for projects involving structural analysis, fluid dynamics, heat transfer, or circuit behavior, Mining uses existing simulation engines (Calculix for FEA, OpenFOAM for CFD, or online simulation APIs) to run basic simulations based on the project parameters and return a report with graphs and outcome data.

**Engineering Diagrams** — for projects that need diagrams rather than 3D models (piping and instrumentation diagrams, electrical schematics, network diagrams), Mining generates these using standard diagram libraries and exports them in formats engineers use (SVG, PDF, DXF).

**Step-by-Step Build Guide** — for hardware projects (IoT devices, embedded systems, lab equipment), Mining generates a detailed assembly and testing guide with component lists, circuit descriptions, and test procedures.

The approach: Mining does not replace CAD software. It produces the design inputs, specifications, and reports that go with a CAD model and fills the documentation gap that most engineering students struggle with.

---

### 5.2 Automation and Diagram Output for Business and Systems Projects

Business, management information systems, and software architecture students need process diagrams, system flowcharts, and automation workflows to validate their project designs.

**What Mining will produce for these projects:**

**Business Process Diagrams** — BPMN-style diagrams showing the workflow or process the student's project addresses. If a student's project is about optimizing hospital patient intake, Mining generates a diagram of the current process and the proposed improved process.

**System Architecture Diagrams** — for IS and software projects that are not AI-focused, Mining generates system context diagrams, data flow diagrams, and entity-relationship diagrams based on the project description.

**Automation Flow Prototypes** — for projects proposing process automation (automating invoice processing, automating student enrollment, automating inventory management), Mining builds a working automation prototype using a workflow automation tool and demonstrates the logic with sample data.

**Decision Trees and Logic Maps** — for projects involving decision-making systems, policy frameworks, or rule-based logic, Mining generates visual decision trees and exports them as diagrams.

---

### 5.3 Integration Approach

CAD and diagram outputs are added as new options in the same prototype selection step from Phase 3. After documentation is complete, Mining now asks:

> *"What type of prototype would you like to build?"*
> - AI Software (classifier, chatbot, dashboard, etc.)
> - Engineering Simulation or CAD Design
> - Process Diagram or Automation Flow

Each option leads to its own input collection flow and generation process.

---

### Phase 5 — Definition of Done

- [ ] Engineering simulation report generation working for at least 3 project types (structural, electrical, thermal)
- [ ] Engineering diagram generation working (P&ID, circuit, network)
- [ ] Business process diagram generation working in BPMN format
- [ ] System architecture diagram generation working
- [ ] Automation flow prototype working for at least 2 business process types
- [ ] All new output types tested with at least 5 student projects each
- [ ] Phase 4 cohort expanded with 10–15 additional engineering and business students to test new outputs

---

---

## Phase 6 — Approach Universities and Departments for Institutional Licensing

### Goal
Move from individual student subscriptions to institutional contracts. A single university deal can be worth 10x a year of individual signups. This is how Mining scales sustainably.

---

### 6.1 Understand How University Procurement Works

Universities do not buy software the way individuals do. They go through formal procurement processes involving:

- A department head or faculty dean who identifies the need
- A procurement or IT office that evaluates the vendor
- A legal or compliance review (data privacy is critical — student data must be handled correctly)
- Budget approval, often tied to the academic year cycle
- A pilot period before full commitment

Mining needs to be ready for all of these before approaching institutions.

---

### 6.2 Build the Institutional Readiness Package

Before approaching a single university, Mining needs the following ready:

**Data Privacy Documentation**
A clear statement of what student data Mining collects, how it is stored, who has access, and how it is deleted. This should reference FERPA (US), GDPR (Europe), POPIA (South Africa), or whichever regulations apply in the target market. This is non-negotiable for any university conversation.

**Security and Compliance Statement**
Universities need to know that student project ideas and documentation are not being shared, used to train external models, or exposed to third parties.

**Usage and Outcome Data**
The Phase 4 cohort results become the sales evidence. Universities want to see: time saved per student, quality of outputs, student satisfaction, and comparison to the status quo. Prepare a one-page summary of Phase 4 results.

**Institutional Pricing Sheet**
Pricing for institutions is different from individual students. Suggested structure:
- Department License: covers all students in one department for one academic year
- Faculty License: covers all students across a faculty (e.g., all engineering students)
- University-Wide License: unlimited student access across all departments

Pricing should be per-student-per-year at a lower unit rate than the individual plan, but negotiated as a lump sum so Mining gets stable revenue.

**Support and Onboarding Plan**
Universities want to know what happens after they sign. Define: how students get access, whether Mining provides training sessions, what the support process is, and how issues are escalated.

---

### 6.3 Identify the Right Entry Points at Each University

Do not approach the university administration first. That is the slowest path. Instead, approach in this order:

**1. Project Supervisors and Lecturers**
Faculty members who supervise final year projects feel the pain most directly. They spend hours helping students structure projects and fix documentation. Mining solves their problem too. A lecturer who champions Mining internally is the fastest path to a departmental conversation.

**2. Department Heads**
Once a few lecturers are bought in, a department head conversation becomes natural. Frame it as: *"Your final year students will submit better-quality projects, and your lecturers will spend less time on remedial documentation feedback."*

**3. Teaching and Learning Centers**
Many universities have centers focused on student academic support and graduate outcomes. Mining fits directly into their mandate.

**4. Student Unions and Associations**
Student bodies often have budgets for tools that help students succeed. They can sponsor access for all final year students or advocate internally for the university to adopt Mining.

---

### 6.4 The Pilot Model for University Conversations

Never ask a university to commit to a full license before they have seen Mining work. Instead, propose a structured pilot:

- **Duration:** One semester or one academic year cohort
- **Scope:** One department, all final year students
- **Cost:** Free or heavily discounted pilot in exchange for formal evaluation and a case study
- **Evaluation criteria:** Agreed upfront — student completion rates, documentation quality, supervisor satisfaction
- **Exit path:** Clear definition of what Mining needs to deliver for the pilot to convert to a paid contract

After the pilot, the case study becomes the sales asset for the next university conversation.

---

### 6.5 Build the Long-Term Institutional Product Features

Institutional customers will need features individual students do not:

**Admin Dashboard** — the department coordinator can see which students have started, which have completed their documentation, and which have built prototypes. This gives supervisors visibility without accessing student content.

**Custom Templates** — each institution has its own documentation format. Mining should allow departments to upload their official project template and have Mining write inside it rather than a generic template.

**Bulk Access Management** — students are enrolled by their student ID or institutional email. The department uploads a list, Mining grants access. No individual sign-up friction.

**Integration with Learning Management Systems** — many universities use Moodle, Blackboard, or Canvas. Mining should eventually offer an LTI integration so it appears inside the LMS students already use.

These features do not all need to exist before the first university conversation, but they should be on the roadmap and communicated as planned.

---

### Phase 6 — Definition of Done

- [ ] Data privacy documentation complete and reviewed by a legal professional
- [ ] Institutional pricing sheet finalized
- [ ] Support and onboarding plan documented
- [ ] Outreach to at least 10 department heads or project supervisors at 5 different universities
- [ ] At least 2 pilot agreements signed
- [ ] Both pilots running with active student usage
- [ ] At least 1 pilot converted to a paid institutional contract
- [ ] Admin dashboard, custom template upload, and bulk access management built

---

---

## Cross-Phase Considerations

These are things that matter across all phases and need attention from the very beginning.

### Avoid Hallucinated References

The worst thing Mining can do is generate a document with fake citations — papers that do not exist or DOIs that lead nowhere. This is an academic integrity disaster. From Phase 1 onward, every citation in a generated document must be traceable to a real source in the research library with a confirmed URL or DOI. Build this check into the generation pipeline, not as an afterthought.

### Student Data Privacy

Student project ideas are intellectual property. Mining must never use student-submitted project ideas, documents, or prototypes to train its own models without explicit opt-in consent. Store student data with encryption. Allow students to delete their data. These are not optional — they are trust requirements.

### Honesty About AI Involvement

Mining should be transparent that documents and prototypes are AI-generated starting points, not finished products. Every generated document should carry a note that it was drafted with Mining's assistance and should be reviewed, edited, and owned by the student. This protects students academically and builds trust in the platform.

### Pricing Should Reflect Student Reality

Students in different regions have very different spending power. A $15/month subscription is affordable in Europe or North America but may be prohibitive in parts of Africa or Southeast Asia — exactly where the final year project pain is often highest. Consider regional pricing or a pay-once-per-project model as the primary offering. Keep the free tier functional enough that students can evaluate Mining before committing.

### Build for Low-Bandwidth Environments

Many of the students who will benefit most from Mining are in universities with slow or intermittent internet connections. The platform should load fast on slow connections, not rely on large file uploads where avoidable, and where possible allow document drafts to be downloaded and continued offline.

---

## Summary Timeline

| Phase | Recommended Duration | Key Milestone |
|---|---|---|
| Phase 1 — Research Library | 4–6 weeks | 500+ papers indexed, semantic search working |
| Phase 2 — Documentation Engine | 6–8 weeks | Full document generated across 4 fields |
| Phase 3 — AI Prototype Builder | 8–10 weeks | 5 prototype types deployable in under 15 min |
| Phase 4 — Student Testing | 6–8 weeks | 20+ students tested, top issues fixed |
| Phase 5 — CAD & Automation | 6–8 weeks | Engineering and business outputs live |
| Phase 6 — Institutional Licensing | Ongoing from Month 9 | First paid institutional contract signed |

**Total to first full platform:** approximately 9–12 months of focused development.

---

*Mining — Build it right, build it once, make it matter.*
