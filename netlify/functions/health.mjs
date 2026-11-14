export default async (req, context) => {
  const geminiKey = process.env.GEMINI_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('GEMINI_API_KEY'));
  const slackUrl = process.env.SLACK_WEBHOOK_URL || (typeof Netlify !== 'undefined' && Netlify.env?.get('SLACK_WEBHOOK_URL'));
  const publoraKey = process.env.PUBLORA_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('PUBLORA_API_KEY'));
  const hermesKey = process.env.HERMES_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('HERMES_API_KEY'));

  const data = {
    status: "healthy",
    platform: "FrontierPilot 2.0 Autonomous Creator Studio",
    version: "1.1.25",
    cloud: "Netlify Edge & Serverless Functions",
    uptime_mode: "24/7 Always-On (Continuous Cloud Execution)",
    timestamp: new Date().toISOString(),
    services: {
      gemini_generator: geminiKey ? "connected" : "missing_key",
      slack_approval_hub: slackUrl ? "connected" : "missing_key",
      publora_publishing: publoraKey ? "connected" : "missing_key",
      hermes_agent_bridge: hermesKey ? "ready" : "ready (unrestricted)",
      firebase_auth: "integrated"
    },
    endpoints: {
      health: "/api/health",
      drafts: "/api/drafts",
      frontierpilot: "/api/frontierpilot/status",
      hermes_status: "/api/hermes/status",
      hermes_dispatch: "/api/hermes/dispatch",
      hermes_skills: "/api/hermes/skills",
      hermes_redeploy: "/api/hermes/redeploy"
    }
  };

  return new Response(JSON.stringify(data, null, 2), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Cache-Control": "no-cache, no-store, must-revalidate"
    }
  });
};

export const config = {
  path: "/api/health"
};
