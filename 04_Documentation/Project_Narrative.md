# Call Center Quality Analytics — Project Narrative

## Why I Built This

Coming from a 16-year background in QA, call center operations, and coaching at Justdial, I wanted my first data analytics project to sit close to home — something where I already understood the business logic and could focus my energy on learning the technical execution around it. Call center quality was the natural choice. I knew what "good performance" looks like from the operations side; this project was about learning to prove it with data.

Since real call center data is almost never publicly available (privacy and confidentiality make sure of that), I built my own synthetic dataset from scratch using a Python script — 25 agents across 6 months, simulating agent tenure, QA audit scores, average handle time (AHT), resolution outcomes, and customer satisfaction (CSAT). I also deliberately built in the kind of messiness real data always has: missing values, duplicate rows, inconsistent casing, stray whitespace, and a batch of bad AHT entries. The idea was to give myself a proper cleaning problem to solve, not a dataset that was already analysis-ready.

---

## The Data Cleaning Journey

### The AHT sign error — a true debugging moment, not just a simulation

The README describes the negative AHT values as an "intentional data entry error simulation," and while that's technically true in the sense that I planned to inject some bad AHT values, the actual mechanism was more honest than that: while writing `generate_data.py`, I typed a minus sign into the AHT generation logic, which produced negative minutes and seconds across a chunk of rows. I caught it during the cleaning phase, not while writing the script — so what started as a genuine typo became a useful stand-in for the kind of "someone fat-fingered a negative sign in a data entry system" error that shows up in real operational data all the time. I fixed it with `.abs()`, which converts all AHT values to their positive equivalent — a one-line fix, but only after tracing the negative values back to where they actually came from.

### Missing values: choosing median over mean, deliberately

Before deciding how to fill the ~3% missing values, I checked the data for outliers first rather than defaulting to a rule of thumb. AHT and CSAT values had enough spread and a few extreme points that using the mean would have let those outliers pull the fill value away from what a "typical" record actually looked like. Median doesn't get dragged by outliers the same way, so I used it for the missing value fill — a decision made after looking at the actual distribution, not a reflex.

### Text casing cleanup — including a clue in `call_type`

The synthetic data generation also produced inconsistent casing in text fields — things like "excellent" vs "Excellent" vs "EXCELLENT" in performance-related columns, and "Inbound" vs "INBOUND" in the `call_type` column specifically. I standardized this using `.str.title()` and stripped stray leading/trailing whitespace with `.str.strip()`. This cleanup on `call_type` turned out to matter for a finding later in the EDA phase (below).

### Duplicate rows

15 duplicate rows were removed using `.drop_duplicates()`, bringing the dataset from 3,915 rows down to 3,902 clean rows.

---

## Key Findings

### Tenure matters more than QA scores for predicting satisfaction

Tenure correlated with CSAT at 0.59 — a moderate-to-strong relationship — while QA audit scores correlated at 0.47. Both matter, but tenure edges out QA scoring as the stronger single predictor, which lines up with what any call center coach would expect: experience builds the judgment and rapport that a scripted QA checklist can't fully capture.

### The AHT insight that needed a second look

At first glance, "top performers have lower AHT" could easily be misread as "faster is better" — a dangerous conclusion for a call center to act on, since it's exactly the kind of thing that leads to agents rushing calls to hit a number. Cross-referencing AHT against resolution status showed the real story: high performers aren't ending calls early, they're resolving issues efficiently. That distinction is the whole point — AHT should never be tracked as a standalone KPI, only alongside resolution rate and CSAT.

### `call_type`: knowing when *not* to analyze something

Every single call in the dataset had the same `call_type` value — "Inbound" — once the casing had been standardized during cleaning. I suspected this might be the case going in, since I'd generated the dataset myself and knew there was only one call type built into the simulation, but I checked it deliberately during EDA rather than assuming. Confirming it meant the column had zero variance: no differences to measure, no relationships to explore, nothing to segment by. So I excluded it from further analysis entirely.

This ended up being one of the more useful lessons of the project — not every column earns a place in the analysis just because it exists. Recognizing a dead-end column and setting it aside, rather than forcing a chart or a correlation out of something with no signal in it, is its own kind of analytical judgment. It's easy to assume more columns automatically means more insight; this was a small, concrete reminder that it doesn't.

---

## Business Recommendations

1. **Invest in tenure-linked coaching.** Since tenure predicts CSAT more strongly than QA scores alone, pairing newer agents with experienced mentors could move the needle on satisfaction faster than QA-score-driven coaching by itself.
2. **Never use AHT as a standalone KPI.** Pair it with resolution rate so the metric can't be gamed by agents cutting calls short.
3. **Investigate the Escalated-vs-Unresolved CSAT gap.** Since escalating doesn't hurt satisfaction much, it may be worth encouraging agents to escalate sooner rather than attempting a resolution they're not equipped to close out.

---

## Reflections

This project taught me two things that go beyond the specific charts and numbers. First, that a "data entry error simulation" isn't always as clean as it sounds on paper — my own typo turned into the negative AHT problem, and tracing it back to its source was a more realistic debugging exercise than if I'd deliberately scripted the error in from the start. Second, that a good analyst has to be willing to *not* analyze something — the `call_type` column was a reminder that spotting a dead end and moving on is just as much a skill as finding a strong correlation.

I used AI (Claude) as a learning aid throughout — for guidance on code structure, debugging, and understanding why each step mattered — but the domain judgment behind what counts as a real finding versus noise came from my own operations background, and I can walk through and explain every step of this project's logic.
