/**
 * Deterministic mock data generator for offline / no-backend mode.
 * Activated when VITE_USE_MOCK=true OR an API call fails (api.js falls back).
 *
 * Keeps the UI demo-able for academic review even when the backend is down.
 */

const rng = (seed) => {
  let s = seed >>> 0
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0
    return s / 0xffffffff
  }
}

const r = rng(20260415)
const pick = (arr) => arr[Math.floor(r() * arr.length)]
const intBetween = (a, b) => Math.floor(r() * (b - a + 1)) + a

const AGENT_DEFS = [
  { id: 'analyzer-claude', name: 'Analyzer · Claude Opus', agent_type: 'analyzer', llm_provider: 'anthropic', model: 'claude-opus-4-6' },
  { id: 'analyzer-gpt',    name: 'Analyzer · GPT-4o',     agent_type: 'analyzer', llm_provider: 'openai',    model: 'gpt-4o' },
  { id: 'analyzer-llama',  name: 'Analyzer · Llama-3.1',  agent_type: 'analyzer', llm_provider: 'ollama',    model: 'llama3.1:70b' },
  { id: 'healer-claude',   name: 'Healer · Claude Sonnet',agent_type: 'healer',   llm_provider: 'anthropic', model: 'claude-sonnet-4-6' },
  { id: 'healer-gpt',      name: 'Healer · GPT-4o',       agent_type: 'healer',   llm_provider: 'openai',    model: 'gpt-4o' },
  { id: 'healer-deepseek', name: 'Healer · DeepSeek-Coder',agent_type:'healer',   llm_provider: 'ollama',    model: 'deepseek-coder:33b' },
  { id: 'validator-claude',name: 'Validator · Claude Haiku',agent_type:'validator',llm_provider: 'anthropic', model: 'claude-haiku-4-5' },
  { id: 'validator-gpt',   name: 'Validator · GPT-4o-mini',agent_type:'validator',llm_provider: 'openai',    model: 'gpt-4o-mini' },
  { id: 'validator-qwen',  name: 'Validator · Qwen-2.5',   agent_type:'validator',llm_provider: 'ollama',    model: 'qwen2.5-coder:32b' },
]

export const mockAgents = AGENT_DEFS.map((a, i) => ({
  ...a,
  status: i === 4 ? 'busy' : (i === 8 ? 'offline' : 'online'),
  reputation_score: 0.72 + r() * 0.27,
  total_proposals: intBetween(120, 980),
  accepted_proposals: intBetween(80, 700),
  avg_latency_ms: intBetween(180, 720),
  uptime_pct: 92 + r() * 7.5,
}))

const BUG_TYPES = [
  'payment_calculation','cart_state','inventory_race','currency_conversion',
  'session_management','input_validation','null_pointer','off_by_one',
  'type_coercion','memory_leak','race_condition','deadlock'
]
const SEVERITIES = ['critical','high','medium','low']
const STATUSES = ['detected','analyzing','fix_proposed','consensus_pending','resolved','failed']
const PROJECTS = ['ecommerce-simulator','pandas','numpy','flask','requests','black','spacy','tornado']

const ORIGINAL_SNIPPETS = {
  payment_calculation: 'total = price * quantity\ntax = total * 0.15',
  cart_state: 'cart.items.append(item)\nreturn cart',
  inventory_race: 'if product.stock > 0:\n    product.stock -= 1',
  currency_conversion: 'converted = amount * rate',
  session_management: "session['user_id'] = user.id",
  input_validation: "qty = int(request.form['quantity'])",
  null_pointer: 'email = user.email.lower()',
  off_by_one: 'for i in range(len(items) + 1):',
  type_coercion: 'price = float(payload["price"])',
  memory_leak: 'cache[key] = heavy_object()',
  race_condition: 'counter += 1',
  deadlock: 'lock_a.acquire(); lock_b.acquire()',
}
const FIXED_SNIPPETS = {
  payment_calculation: "total = Decimal(str(price)) * Decimal(str(quantity))\ntax  = total * Decimal('0.15')",
  cart_state: 'cart.items.append(item.copy())\nreturn cart',
  inventory_race: 'with product.lock:\n    if product.stock > 0:\n        product.stock -= 1',
  currency_conversion: "converted = (Decimal(str(amount)) * Decimal(str(rate))).quantize(Decimal('0.01'))",
  session_management: "session.regenerate()\nsession['user_id'] = user.id",
  input_validation: "qty = max(1, min(int(request.form['quantity']), MAX_QTY))",
  null_pointer: 'email = user.email.lower() if user and user.email else None',
  off_by_one: 'for i in range(len(items)):',
  type_coercion: 'price = Decimal(str(payload["price"]))\nif price < 0: raise ValueError',
  memory_leak: 'with weakref_cache(cache) as c:\n    c[key] = heavy_object()',
  race_condition: 'with counter_lock:\n    counter += 1',
  deadlock: 'with ordered_locks(lock_a, lock_b):\n    ...',
}

const now = Date.now()

export const mockBugs = Array.from({ length: 47 }, (_, i) => {
  const bug_type = pick(BUG_TYPES)
  const severity = pick(SEVERITIES)
  const status = i < 8 ? pick(['detected','analyzing','fix_proposed','consensus_pending'])
                       : (r() > 0.18 ? 'resolved' : 'failed')
  return {
    id: `bug-${(i+1).toString().padStart(4,'0')}`,
    bug_type,
    severity,
    status,
    project: pick(PROJECTS),
    file_path: `src/${pick(PROJECTS)}/${bug_type}/handler_${i}.py`,
    line_number: intBetween(8, 412),
    detected_at: new Date(now - intBetween(60, 60*60*48) * 1000).toISOString(),
    original_code: ORIGINAL_SNIPPETS[bug_type],
    proposed_fix: FIXED_SNIPPETS[bug_type],
    confidence: 0.62 + r() * 0.36,
    consensus_votes: { prepare: intBetween(5, 9), commit: intBetween(4, 9) },
  }
})

export const mockMetrics = {
  total_bugs: mockBugs.length,
  resolved_bugs: mockBugs.filter(b => b.status === 'resolved').length,
  failed_bugs: mockBugs.filter(b => b.status === 'failed').length,
  active_bugs: mockBugs.filter(b => !['resolved','failed'].includes(b.status)).length,
  agents_online: mockAgents.filter(a => a.status === 'online').length,
  agents_total: mockAgents.length,
  success_rate: 0.847,
  average_consensus_time_ms: 312,
  throughput_per_min: 6.4,
  total_consensus_rounds: 1284,
  uptime_seconds: 60 * 60 * 73,
}

export const mockRecentActivity = Array.from({ length: 14 }, (_, i) => {
  const types = ['bug_detected','fix_proposed','fix_applied','consensus_reached','agent_status']
  const t = pick(types)
  const messages = {
    bug_detected: `${pick(['Critical','High','Medium'])} severity bug detected in ${pick(PROJECTS)}`,
    fix_proposed: `${pick(AGENT_DEFS).name} proposed fix for ${pick(BUG_TYPES).replace('_',' ')}`,
    fix_applied: `Fix validated and applied to ${pick(PROJECTS)}`,
    consensus_reached: `PBFT consensus reached in ${intBetween(180, 480)}ms (${intBetween(6,9)}/9 votes)`,
    agent_status: `${pick(AGENT_DEFS).name} reputation increased`,
  }
  return {
    type: t,
    message: messages[t],
    timestamp: new Date(now - i * intBetween(60, 480) * 1000).toISOString(),
  }
})

export const mockConsensusStatus = {
  consensus_ready: true,
  active_round_id: 'round-7842',
  total_agents: mockAgents.length,
  online_agents: mockAgents.filter(a => a.status === 'online').length,
  byzantine_threshold: Math.floor((mockAgents.length - 1) / 3),
  required_quorum: 2 * Math.floor((mockAgents.length - 1) / 3) + 1,
  current_view: 18,
  primary_agent_id: 'analyzer-claude',
}

export const mockConsensusRounds = Array.from({ length: 32 }, (_, i) => {
  const success = r() > 0.12
  const startMs = now - i * intBetween(45, 180) * 1000
  const durationMs = intBetween(180, 540)
  return {
    id: `round-${7842 - i}`,
    sequence: 7842 - i,
    bug_id: `bug-${intBetween(1, mockBugs.length).toString().padStart(4,'0')}`,
    primary: pick(AGENT_DEFS).id,
    phase: i === 0 ? pick(['pre_prepare','prepare','commit']) : 'decided',
    prepares: Array.from({ length: intBetween(5, 9) }, () => ({
      agent_id: pick(AGENT_DEFS).id,
      timestamp: startMs + intBetween(20, 80),
      digest: Math.random().toString(36).slice(2, 10),
    })),
    commits: Array.from({ length: intBetween(4, 9) }, () => ({
      agent_id: pick(AGENT_DEFS).id,
      timestamp: startMs + intBetween(120, 220),
      digest: Math.random().toString(36).slice(2, 10),
    })),
    success,
    reason: success ? 'quorum_reached' : pick(['view_change','timeout','byzantine_detected']),
    durationMs,
    startedAt: new Date(startMs).toISOString(),
    completedAt: new Date(startMs + durationMs).toISOString(),
  }
})

export const mockEvaluation = {
  datasets: [
    { name: 'BugsInPy',  total: 493,  attempted: 412, fixed: 287, pass_at_1: 0.697, pass_at_5: 0.812 },
    { name: 'Defects4J', total: 835,  attempted: 612, fixed: 401, pass_at_1: 0.655, pass_at_5: 0.781 },
    { name: 'Synthetic E-Commerce', total: 2000, attempted: 2000, fixed: 1764, pass_at_1: 0.882, pass_at_5: 0.941 },
  ],
  by_bug_type: BUG_TYPES.map(t => ({
    bug_type: t,
    success_rate: 0.55 + r() * 0.42,
    avg_latency_ms: intBetween(220, 720),
    sample_size: intBetween(40, 240),
  })),
  by_severity: SEVERITIES.map(s => ({
    severity: s,
    success_rate: s === 'critical' ? 0.78 : s === 'high' ? 0.84 : s === 'medium' ? 0.90 : 0.93,
    count: intBetween(80, 420),
  })),
  latency_buckets: [
    { bucket: '<200ms',  count: 412 },
    { bucket: '200-400', count: 681 },
    { bucket: '400-600', count: 384 },
    { bucket: '600-1s',  count: 142 },
    { bucket: '>1s',     count: 31  },
  ],
  reputation_history: AGENT_DEFS.map(a => ({
    agent_id: a.id,
    series: Array.from({ length: 24 }, (_, h) => ({
      t: h,
      rep: Math.max(0.3, Math.min(0.99, 0.7 + Math.sin(h / 3 + (a.id.length % 5)) * 0.12 + r() * 0.05)),
    })),
  })),
  throughput_history: Array.from({ length: 60 }, (_, m) => ({
    minute: m,
    bugs_per_min: 4 + Math.sin(m / 6) * 2 + r() * 1.5,
  })),
}

/* ────────────────────────── Repair Timeline ────────────────────────── */

const TIMELINE_PHASES = ['detection','analysis','healing','validation','consensus','applied']

export function mockTimelineEvents(bugId) {
  const bug = mockBugs.find(b => b.id === bugId) || mockBugs[0]
  const base = new Date(bug.detected_at).getTime()
  const events = []
  let t = base

  const pushEvt = (phase, agentId, agentType, action, detail, vote, pbftRound) => {
    const dur = intBetween(40, 280)
    t += intBetween(200, 1200)
    events.push({
      id: `evt-${events.length.toString().padStart(3,'0')}`,
      timestamp: new Date(t).toISOString(),
      phase, agent_id: agentId, agent_type: agentType,
      action, detail: detail || '', vote: vote || null,
      pbft_round: pbftRound ?? null, duration_ms: dur,
    })
  }

  // Detection
  pushEvt('detection','analyzer-claude','analyzer','Anomaly detected','Static analysis flagged suspicious float arithmetic in payment path')
  pushEvt('detection','analyzer-gpt','analyzer','Confirmed anomaly','Cross-check found same pattern — payment_calculation fault confirmed')

  // Analysis
  pushEvt('analysis','analyzer-claude','analyzer','Root-cause identified','Float precision loss in multiplication: price * qty truncates to IEEE 754 double')
  pushEvt('analysis','analyzer-llama','analyzer','Pattern matched','Bug matches pattern P-FP-001 (Float Precision) with 94% confidence')
  pushEvt('analysis','analyzer-gpt','analyzer','Impact assessed','Affects 12% of checkout paths; max monetary loss $0.03 per transaction')

  // Healing
  pushEvt('healing','healer-claude','healer','Fix proposed','Replace float arithmetic with Decimal; apply quantize for 2-digit cents')
  pushEvt('healing','healer-gpt','healer','Fix proposed','Wrap multiplication in round(…, 2) — simpler but less precise')
  pushEvt('healing','healer-deepseek','healer','Fix proposed','Use integer cents internally; convert at display boundary')

  // Validation
  pushEvt('validation','validator-claude','validator','Test suite passed','All 47 existing tests pass; 3 new edge-case tests added and pass')
  pushEvt('validation','validator-gpt','validator','Regression check clear','No performance regression; memory footprint unchanged')
  pushEvt('validation','validator-qwen','validator','Veto — edge case','round() proposal fails for JPY (0-decimal currency); recommending Decimal approach', 'veto')

  // Consensus
  const rndSeq = intBetween(7800, 7842)
  pushEvt('consensus','analyzer-claude','system','Pre-Prepare broadcast','Primary multicasts PRE-PREPARE with Decimal fix proposal', 'prepare', rndSeq)
  AGENT_DEFS.slice(0, 7).forEach(a => {
    pushEvt('consensus', a.id, a.agent_type, `${a.agent_type} voted PREPARE`, `Digest a3f2…91c4 validated`, 'prepare', rndSeq)
  })
  AGENT_DEFS.slice(0, 6).forEach(a => {
    pushEvt('consensus', a.id, a.agent_type, `${a.agent_type} voted COMMIT`, `Quorum met — committing fix`, 'commit', rndSeq)
  })

  // Applied
  pushEvt('applied','validator-claude','system','Fix applied to sandbox','Sandboxed deployment succeeded; canary traffic 5% routed')
  pushEvt('applied','validator-gpt','system','Production promotion','Fix promoted to production after 60s canary with 0 errors')

  return events
}

/* ────────────────────────── Agent Heatmap ────────────────────────── */

export const mockHeatmapData = (() => {
  const ids = AGENT_DEFS.map(a => a.id)
  const n = ids.length
  const matrix = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => {
      if (i === j) return 1.0
      const sameType = AGENT_DEFS[i].agent_type === AGENT_DEFS[j].agent_type
      const base = sameType ? 0.72 : 0.42
      const val = Math.min(1, Math.max(0, base + (r() - 0.5) * 0.2))
      return +val.toFixed(3)
    })
  )
  // Make symmetric
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) matrix[j][i] = matrix[i][j]

  const correlations = []
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
    correlations.push({
      agent_a: ids[i], agent_b: ids[j],
      pearson_r: +(matrix[i][j] * 0.95 + (r() - 0.5) * 0.1).toFixed(3),
      agreement_pct: +(matrix[i][j] * 100).toFixed(1),
      rounds_together: intBetween(800, 1284),
    })
  }
  correlations.sort((a, b) => b.agreement_pct - a.agreement_pct)

  return { agents: ids, matrix, rounds_analyzed: 1284, correlations }
})()

/* ────────────────────────── Byzantine Lab ────────────────────────── */

export const mockByzantineScenarios = (() => {
  const agents = AGENT_DEFS.map(a => ({
    ...a, fault_injected: false, fault_type: null,
  }))

  const FAULT_TYPES = ['bad_proposal','drop_message','equivocate']
  const scenarios = Array.from({ length: 16 }, (_, i) => {
    const numFaults = intBetween(1, 3)
    const faults = Array.from({ length: numFaults }, () => ({
      agent_id: pick(AGENT_DEFS).id,
      fault_type: pick(FAULT_TYPES),
    }))
    const survived = numFaults <= 2 ? r() > 0.1 : r() > 0.7
    return {
      id: `scenario-${(i + 1).toString().padStart(3,'0')}`,
      faults,
      survived,
      rounds_to_recover: survived ? intBetween(1, 4) : 0,
      consensus_achieved: survived,
      duration_ms: intBetween(220, 680),
      log: [
        `Injected ${numFaults} fault(s): ${faults.map(f => f.fault_type.replace('_',' ')).join(', ')}`,
        survived ? 'View change triggered — new primary elected' : 'Consensus timeout — system halted',
        survived ? `Recovery in ${intBetween(1,4)} round(s)` : 'Manual intervention required',
      ],
    }
  })

  const survived = scenarios.filter(s => s.survived).length
  return {
    agents,
    scenarios,
    summary: {
      total_runs: scenarios.length,
      survived,
      failed: scenarios.length - survived,
      survival_rate: +(survived / scenarios.length).toFixed(3),
    },
  }
})()

/* ────────────────────────── Knowledge Graph ────────────────────────── */

export const mockKnowledgeGraph = (() => {
  const nodes = []
  const edges = []

  // Bug patterns
  const patterns = [
    { id: 'pat-fp', label: 'Float Precision', x: 400, y: 300 },
    { id: 'pat-race', label: 'Race Condition', x: 200, y: 200 },
    { id: 'pat-null', label: 'Null Deref', x: 600, y: 200 },
    { id: 'pat-obo', label: 'Off-By-One', x: 300, y: 450 },
    { id: 'pat-inj', label: 'Injection', x: 550, y: 420 },
    { id: 'pat-type', label: 'Type Coercion', x: 150, y: 400 },
  ]
  patterns.forEach(p => nodes.push({ ...p, type: 'pattern' }))

  // Fixes
  const fixes = [
    { id: 'fix-decimal', label: 'Decimal Coercion', x: 440, y: 180, success_rate: 0.94 },
    { id: 'fix-lock', label: 'Lock Guard', x: 120, y: 120, success_rate: 0.88 },
    { id: 'fix-nullchk', label: 'Null Guard', x: 680, y: 120, success_rate: 0.91 },
    { id: 'fix-bound', label: 'Bounds Check', x: 350, y: 540, success_rate: 0.86 },
    { id: 'fix-sanitize', label: 'Input Sanitize', x: 620, y: 520, success_rate: 0.93 },
    { id: 'fix-cast', label: 'Safe Cast', x: 80, y: 480, success_rate: 0.82 },
  ]
  fixes.forEach(f => nodes.push({ ...f, type: 'fix' }))

  // Bugs scattered around patterns
  const bugPatternMap = {
    payment_calculation: 'pat-fp', inventory_race: 'pat-race', null_pointer: 'pat-null',
    off_by_one: 'pat-obo', input_validation: 'pat-inj', type_coercion: 'pat-type',
    race_condition: 'pat-race', currency_conversion: 'pat-fp', cart_state: 'pat-null',
    session_management: 'pat-inj', memory_leak: 'pat-type', deadlock: 'pat-race',
  }
  const patFixMap = {
    'pat-fp': 'fix-decimal', 'pat-race': 'fix-lock', 'pat-null': 'fix-nullchk',
    'pat-obo': 'fix-bound', 'pat-inj': 'fix-sanitize', 'pat-type': 'fix-cast',
  }

  mockBugs.slice(0, 18).forEach((b, i) => {
    const patId = bugPatternMap[b.bug_type] || 'pat-fp'
    const pat = patterns.find(p => p.id === patId)
    nodes.push({
      id: b.id, type: 'bug', label: `${b.bug_type.replace(/_/g,' ')} #${i+1}`,
      x: pat.x + (r() - 0.5) * 160, y: pat.y + (r() - 0.5) * 120,
      severity: b.severity,
    })
    edges.push({ source: b.id, target: patId, relation: 'exhibits' })
  })

  // Pattern→Fix edges
  Object.entries(patFixMap).forEach(([p, f]) => {
    edges.push({ source: p, target: f, relation: 'resolved_by' })
  })

  // A few similar-bug edges
  for (let i = 0; i < 6; i++) {
    const a = nodes.filter(n => n.type === 'bug')[intBetween(0, 12)]
    const b = nodes.filter(n => n.type === 'bug')[intBetween(0, 12)]
    if (a && b && a.id !== b.id) edges.push({ source: a.id, target: b.id, relation: 'similar_to' })
  }

  return { nodes, edges }
})()

/* ────────────────────────── Diff Theater ────────────────────────── */

const CODE_CONTEXT = {
  payment_calculation: {
    file: 'src/ecommerce/checkout/payment.py',
    lines: [
      'class PaymentProcessor:',
      '    def calculate_total(self, price, quantity, tax_rate=0.15):',
      '        """Calculate order total with tax."""',
      '        total = price * quantity',
      '        tax = total * tax_rate',
      '        return total + tax',
      '',
      '    def process_payment(self, order):',
      '        amount = self.calculate_total(',
      '            order.price, order.quantity',
      '        )',
      '        return self.gateway.charge(amount)',
    ],
    fault_lines: [3, 4],
  },
  cart_state: {
    file: 'src/ecommerce/cart/manager.py',
    lines: [
      'class CartManager:',
      '    def add_item(self, cart, item):',
      '        """Add item to shopping cart."""',
      '        cart.items.append(item)',
      '        return cart',
      '',
      '    def get_cart(self, user_id):',
      '        cart = self.store.get(user_id)',
      '        return cart or Cart()',
    ],
    fault_lines: [3],
  },
}

export function mockDiffTheater(bugId) {
  const bug = mockBugs.find(b => b.id === bugId) || mockBugs[0]
  const ctx = CODE_CONTEXT[bug.bug_type] || CODE_CONTEXT.payment_calculation

  const healers = AGENT_DEFS.filter(a => a.agent_type === 'healer')
  const validators = AGENT_DEFS.filter(a => a.agent_type === 'validator')

  const proposals = healers.map((h, i) => {
    const accepted = i === 0 // first healer's fix wins
    const modLines = [...ctx.lines]
    if (bug.bug_type === 'payment_calculation') {
      if (i === 0) {
        modLines[3] = "        total = Decimal(str(price)) * Decimal(str(quantity))"
        modLines[4] = "        tax = total * Decimal(str(tax_rate))"
      } else if (i === 1) {
        modLines[3] = '        total = round(price * quantity, 2)'
        modLines[4] = '        tax = round(total * tax_rate, 2)'
      } else {
        modLines[3] = '        total = int(price * 100) * quantity'
        modLines[4] = '        tax = total * tax_rate // 100'
      }
    } else {
      modLines[ctx.fault_lines[0]] = '        cart.items.append(item.copy())  # defensive copy'
    }

    return {
      agent: h,
      label: `${h.llm_provider} — ${h.model}`,
      original_lines: ctx.lines,
      modified_lines: modLines,
      fault_lines: ctx.fault_lines,
      verdict: accepted ? 'accepted' : 'rejected',
      confidence: accepted ? 0.94 : 0.62 + r() * 0.2,
      validator_votes: validators.map(v => ({
        agent_id: v.id,
        vote: (accepted || r() > 0.5) ? 'approve' : 'reject',
        reason: accepted
          ? 'Fix passes all tests; handles edge cases correctly'
          : (r() > 0.5 ? 'Insufficient precision for multi-currency' : 'Regression in edge case: zero-quantity orders'),
      })),
    }
  })

  return {
    bug,
    file_path: ctx.file,
    original_lines: ctx.lines,
    fault_lines: ctx.fault_lines,
    proposals,
  }
}

/* ────────────────────────── Mock Router ────────────────────────── */

export function mockReply(url) {
  if (url.includes('/dashboard/metrics'))         return mockMetrics
  if (url.includes('/dashboard/recent-activity')) return mockRecentActivity
  if (url.includes('/agents/consensus/status'))   return mockConsensusStatus
  if (url.includes('/agents'))                    return mockAgents
  if (url.includes('/bugs/stats/summary'))        return { total: mockBugs.length, by_status: {}, by_severity: {} }
  if (url.match(/\/bugs\/[^/]+$/))                return mockBugs[0]
  if (url.includes('/bugs'))                      return { bugs: mockBugs, total: mockBugs.length }
  if (url.includes('/consensus/rounds'))          return mockConsensusRounds
  if (url.includes('/evaluation'))                return mockEvaluation
  if (url.match(/\/timeline\/[^/]+$/))            return mockTimelineEvents(url.split('/').pop())
  if (url.includes('/heatmap'))                   return mockHeatmapData
  if (url.includes('/byzantine'))                 return mockByzantineScenarios
  if (url.includes('/knowledge-graph'))           return mockKnowledgeGraph
  if (url.match(/\/diff-theater\/[^/]+$/))        return mockDiffTheater(url.split('/').pop())
  return null
}
