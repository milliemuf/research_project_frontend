# CodeFlow AI — Frontend

Vue 3 + Vite single-page application for the **CodeFlow AI** research project: a Byzantine
Fault-Tolerant multi-agent system for autonomous runtime program repair, with a focus on
e-commerce systems.

This frontend connects to the [CodeFlow AI backend](#) and provides operations dashboards,
live consensus visualisation, an isolated sandbox runner, and research-mode views for the
empirical evaluation reported in the accompanying paper.

**Author:** Millicent Mufambi (H240624A)
**Supervisor:** Mr. Makondo
**Institution:** Department of Software Engineering, Harare Institute of Technology

---

## Stack

| Layer | Technology |
| --- | --- |
| Framework | Vue 3 (Composition API, `<script setup>`) |
| Build | Vite 5 |
| State | Pinia |
| Routing | vue-router 4 |
| Styling | Tailwind CSS 3 |
| HTTP | Axios |
| Charts | Chart.js + vue-chartjs |
| Realtime | Native WebSocket |

---

## Views

The application is organised into two groups of views:

### Operations
- **Overview** — summary dashboard of recent activity, agent health, and live metrics
- **Consensus** — animated visualisation of the PBFT three-phase protocol
- **Consensus Lab** — live, WebSocket-streamed playground for proposing fixes to the
  consensus engine and watching each validator vote arrive in real time
- **Bug Stream** — incoming bug reports
- **Fix History** — applied / rolled-back fixes with full diff
- **Agent Mesh** — per-agent reputation, accuracy, and LLM provider
- **Sandbox** — paste any candidate fix and run it inside the isolated sandbox; see
  exit code, stdout/stderr, and run history live
- **Evaluation** — empirical results from the seven-metric evaluation framework

### Research
- **Repair Timeline**, **Agent Heatmap**, **Byzantine Lab**, **Knowledge Graph**, **Diff
  Theater** — research-mode views used to inspect individual repairs and visualise the
  consensus process for the technical paper.

---

## Getting started

### Prerequisites
- Node.js 18 or newer
- The CodeFlow AI backend running locally on `http://127.0.0.1:7222`

### Install and run

```bash
npm install
npm run dev
```

The dev server starts on `http://localhost:5173`. Default credentials for the bundled
mock auth are exposed by the Login view.

### Environment

Copy `.env.example` to `.env.local` and adjust if your backend runs on a non-default
host or port:

```ini
VITE_API_URL=http://127.0.0.1:7222
VITE_WS_URL=ws://127.0.0.1:7222/ws/live
```

### Production build

```bash
npm run build      # outputs to ./dist
npm run preview    # serves the production build locally
```

---

## Project structure

```
src/
├── assets/         Static assets and Tailwind entry CSS
├── components/     Shared UI components (Sidebar, Header, StatCard)
├── layouts/        Page layouts (default, blank for login)
├── router/         Route definitions
├── services/       API client (Axios), WebSocket service, mock fixtures
├── stores/         Pinia stores (agents, bugs, consensus, theme, …)
└── views/          Route components (Dashboard, ConsensusLab, Sandbox, …)
```

---

## Companion repositories

- **Backend:** [CodeFlow AI backend (FastAPI + Python)](#) — implements the analyzer,
  healer, validator agents, the PBFT consensus engine, the sandbox executor, and the
  benchmark harness.
- **Research papers:** the systematic review and the technical paper that report the
  empirical findings produced with this prototype are kept separately.

---

## License

[TBD — pending decision before public release.]
