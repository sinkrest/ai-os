# Roman's Lab

A browser-based lab — a collection of AI-built tools, interactive apps, and experiments, all running inside a single tabbed interface.

**Live:** [sinkrest.github.io/romans-lab](https://sinkrest.github.io/romans-lab) &nbsp;·&nbsp; Built with [Claude Code](https://claude.ai/code)

---

## What It Is

Roman's Lab is a browser-based launcher where each "app" is a standalone interactive tool. Navigation works like a browser: click an app to open it in a tab, click Home to return to the launcher.

No frameworks. No build step. Pure HTML, CSS, and JavaScript — deliberately keeping it lightweight and instantly deployable.

---

## Apps

### ⚡ Industrial Command Center — Flagship
Live supply chain operations dashboard built for industrial product managers.
- Animated supply chain network with real-time particle flow
- KPI gauges: OEE, Yield Rate, Cycle Time, Defect Rate, MTBF, Cost/Unit
- What-If Simulator: adjust demand surge, supplier risk, automation level, lead time — see projected impact instantly
- Risk Heat Map (5×5 FMEA-style matrix)
- Global Production Lines: 6 facilities with live throughput timelines
- Activity log with streaming events

### 🛠️ PD Toolkit
Decision tools for Product Development Managers:
- Stage-Gate Checker
- FMEA Calculator
- Make vs Buy Matrix
- Cycle Time Estimator

### 📊 AI Usage Dashboard
Track AI token consumption, model usage, and execution history across Claude and other LLM APIs.

### 🏭 Product Pipeline
A strategy game where you navigate a product through development stages — collect milestones, dodge scope creep, ship before budget runs out.

### ⬡ AI Scoping Tool — Live AI Tool
Describe a business problem. Answer 3 discovery questions. Get a structured AI implementation plan — recommended AI approach, process automation breakdown, effort vs. impact, phased rollout, risks, and success metrics. Powered by Claude API.

**[Live demo →](https://sinkrest.github.io/ai-scoping-tool)**

### 📬 The Industrial Edge
Newsletter landing page for Industrial Product Development Managers — AI, smart manufacturing, and product strategy.

### 🐍 Snake
Classic Snake with a twist: the food runs away when you get close.

---

## Technical Decisions

**No framework** — each app is a self-contained HTML file loaded into an iframe. This keeps load time instant, isolates app state, and makes it easy to add or remove apps without touching shared code.

**Tab navigation** — mimics browser UX. A single nav bar shows the current app as a tab alongside Home. Clicking Home clears the iframe and returns to the launcher grid.

**Canvas for data viz** — the Command Center's supply chain network is rendered on `<canvas>` with `requestAnimationFrame` for smooth particle animation. No charting library needed.

---

## Structure

```
roman-os/
├── index.html              # OS shell + launcher + Snake game
├── nav.js                  # Shared navigation logic
└── apps/
    ├── command-center.html # Industrial Command Center
    ├── dashboard.html      # AI Usage Dashboard
    ├── toolkit.html        # PD Toolkit
    ├── snake.html          # Product Pipeline game
    ├── dog.html            # Royal Dog Portrait Generator
    ├── shop.html           # Gallop & Co. Shop
    └── newsletter.html     # The Industrial Edge
```

---

## Run Locally

No install required. Open `index.html` in a browser.

```bash
git clone https://github.com/sinkrest/roman-os.git
cd roman-os
open index.html
```

---

Built by [Roman Martins](https://romanmartins.com) using Claude Code · [github.com/sinkrest/romans-lab](https://github.com/sinkrest/romans-lab)
