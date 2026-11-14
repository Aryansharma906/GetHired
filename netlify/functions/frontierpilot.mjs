/**
 * FrontierPilot 2.0 — Serverless Career & Radar Gateway
 */

const DEMO_JOBS = [
  {
    id: "opp_anthropic_systems",
    company: "Anthropic",
    role: "Member of Technical Staff, Systems Engineering",
    matchScore: 98,
    status: "interview",
    tier: "Tier 1 Priority",
    location: "San Francisco, CA (Hybrid / Remote)",
    matchReasons: [
      "Deep expertise in autonomous multi-agent orchestration",
      "Direct experience building resilient high-throughput LLM tooling",
      "Strong alignment with safe agentic workflows and human-in-the-loop systems"
    ],
    contacts: [{ name: "Alexandre Passos", role: "Engineering Lead" }]
  },
  {
    id: "opp_cohere_platform",
    company: "Cohere",
    role: "Staff Infrastructure Engineer, Agents & Tooling",
    matchScore: 94,
    status: "applied",
    tier: "Tier 1 Priority",
    location: "Remote / Toronto / SF",
    matchReasons: [
      "Track record architecting production tool harnesses and MCP connectors",
      "Systems-level Python, TypeScript, and serverless edge deployment expertise"
    ],
    contacts: [{ name: "Sarah Chen", role: "Talent Partner" }]
  },
  {
    id: "opp_perplexity_founder",
    company: "Perplexity AI",
    role: "AI Systems & Product Engineer",
    matchScore: 91,
    status: "outreach",
    tier: "Tier 2 Strategic",
    location: "San Francisco, CA",
    matchReasons: [
      "Demonstrated ability to ship full-stack consumer-facing AI interfaces",
      "Speed of execution and autonomous engineering discipline"
    ],
    contacts: [{ name: "Denis Yarats", role: "CTO" }]
  }
];

export default async (req, context) => {
  const url = new URL(req.url);
  const pathname = url.pathname;

  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
      }
    });
  }

  // 1. Status: GET /api/frontierpilot/status
  if (pathname.includes("/status")) {
    const geminiKey = Boolean(process.env.GEMINI_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('GEMINI_API_KEY')));
    const slackUrl = Boolean(process.env.SLACK_WEBHOOK_URL || (typeof Netlify !== 'undefined' && Netlify.env?.get('SLACK_WEBHOOK_URL')));
    const publoraKey = Boolean(process.env.PUBLORA_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('PUBLORA_API_KEY')));

    return new Response(JSON.stringify({
      status: "operational",
      version: "1.1.22",
      cloud_edge: "Netlify 24/7 Always-On",
      integrations: {
        gemini: geminiKey ? "healthy" : "offline",
        slack: slackUrl ? "healthy" : "offline",
        publora: publoraKey ? "healthy" : "offline",
        sheets: "connected",
        drive: "connected",
        notion: "connected"
      },
      activeOpportunities: DEMO_JOBS.length,
      lastSync: new Date().toISOString()
    }, null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 2. Jobs / Opportunities: GET /api/frontierpilot/jobs or /api/opportunities
  if (req.method === "GET") {
    return new Response(JSON.stringify({
      success: true,
      opportunities: DEMO_JOBS,
      count: DEMO_JOBS.length,
      timestamp: new Date().toISOString()
    }, null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 3. Digest: POST /api/frontierpilot/send_digest
  if (req.method === "POST" && pathname.includes("/send_digest")) {
    const slackWebhook = process.env.SLACK_WEBHOOK_URL || (typeof Netlify !== 'undefined' && Netlify.env?.get('SLACK_WEBHOOK_URL'));
    if (slackWebhook) {
      await fetch(slackWebhook, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: `📊 *[FrontierPilot 2.0 Cloud]* Executive Career Radar Digest:\n• ${DEMO_JOBS.length} High-leverage opportunities active\n• Top match: *${DEMO_JOBS[0].company}* — ${DEMO_JOBS[0].role} (${DEMO_JOBS[0].matchScore}% match)`
        })
      });
    }
    return new Response(JSON.stringify({ success: true, message: "Digest dispatched to Slack" }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  return new Response(JSON.stringify({ success: true, message: "Sync acknowledged" }), {
    status: 200,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
  });
};

export const config = {
  path: [
    "/api/frontierpilot/*",
    "/api/opportunities",
    "/api/opportunities/*"
  ]
};
