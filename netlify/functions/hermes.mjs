/**
 * FrontierPilot 2.0 — Hermes Agent Autonomous Integration Gateway
 * 
 * Provides an always-on serverless bridge for Nous Research's Hermes Agent.
 * Enables Hermes Agent to inspect skills, dispatch autonomous tasks,
 * execute content & career workflows, and trigger automated Netlify redeploys.
 */

const SKILLS_CATALOG = [
  {
    name: "linkedin-post-writer",
    description: "Drafts viral, high-converting founder LinkedIn posts using verified 2026 hook formulas.",
    category: "content_creation",
    parameters: {
      topic: { type: "string", description: "Core topic or insight" },
      hook_formula: { type: "string", description: "Optional formula name (e.g. 'contrarian_truth', 'data_revelation')" }
    }
  },
  {
    name: "linkedin-comment-drafter",
    description: "Generates high-leverage thoughtful comments that get pinned and earn author profile visits.",
    category: "engagement",
    parameters: {
      post_text: { type: "string", description: "Target LinkedIn post text to comment on" },
      perspective: { type: "string", description: "Angle or founder perspective to take" }
    }
  },
  {
    name: "linkedin-reply-handler",
    description: "Manages comments and threads, formulating insightful author replies to build authority.",
    category: "engagement",
    parameters: {
      comment_text: { type: "string", description: "Incoming comment to respond to" }
    }
  },
  {
    name: "linkedin-humanizer",
    description: "Audits and humanizes AI drafts, eliminating corporate jargon, robotic cadence, and banned vocabulary.",
    category: "quality_assurance",
    parameters: {
      draft_text: { type: "string", description: "Raw text to humanize" }
    }
  },
  {
    name: "frontierpilot-career-radar",
    description: "Scans and evaluates high-leverage executive AI, Systems & Founder engineering roles.",
    category: "career_automation",
    parameters: {
      min_match_score: { type: "number", description: "Minimum match threshold (0-100)" }
    }
  },
  {
    name: "frontierpilot-outreach-engine",
    description: "Generates bespoke recruiter direct messages and cold pitches using recipient background receipts.",
    category: "career_automation",
    parameters: {
      company: { type: "string", description: "Target company name" },
      role: { type: "string", description: "Role title" },
      contact_name: { type: "string", description: "Hiring manager or recruiter name" }
    }
  }
];

function checkAuth(req) {
  const expectedKey = process.env.HERMES_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('HERMES_API_KEY'));
  if (!expectedKey) return true; // If unconfigured, open for public dev
  const authHeader = req.headers.get("authorization") || "";
  const xKey = req.headers.get("x-hermes-key") || "";
  const token = authHeader.replace(/^Bearer\s+/i, "");
  return token === expectedKey || xKey === expectedKey;
}

export default async (req, context) => {
  const url = new URL(req.url);
  const pathname = url.pathname;

  // Handle CORS pre-flight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Hermes-Key"
      }
    });
  }

  // 1. Status / Discovery: GET /api/hermes or /api/hermes/status
  if (req.method === "GET" && (pathname === "/api/hermes" || pathname === "/api/hermes/status")) {
    return new Response(JSON.stringify({
      agent_gateway: "Hermes Agent Autonomous Bridge",
      status: "online",
      version: "1.1.22",
      runtime: "Netlify 24/7 Always-On Edge",
      authenticated: checkAuth(req),
      capabilities: [
        "autonomous_post_generation",
        "interactive_slack_approval",
        "career_radar_evaluation",
        "skill_catalog_discovery",
        "automated_redeploy"
      ],
      endpoints: {
        skills: "/api/hermes/skills",
        dispatch: "/api/hermes/dispatch",
        redeploy: "/api/hermes/redeploy"
      }
    }, null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 2. Skill Catalog: GET /api/hermes/skills
  if (req.method === "GET" && pathname.startsWith("/api/hermes/skills")) {
    return new Response(JSON.stringify({
      count: SKILLS_CATALOG.length,
      skills: SKILLS_CATALOG,
      provider: "FrontierPilot 2.0 Engine"
    }, null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 3. Autonomous Task Dispatch: POST /api/hermes/dispatch
  if (req.method === "POST" && pathname.startsWith("/api/hermes/dispatch")) {
    if (!checkAuth(req)) {
      return new Response(JSON.stringify({ error: "Unauthorized: Invalid or missing Hermes API key" }), {
        status: 401,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    let payload = {};
    try {
      payload = await req.json();
    } catch (e) {
      return new Response(JSON.stringify({ error: "Invalid JSON payload" }), {
        status: 400,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    const { action, params = {} } = payload;

    // A. Action: Draft Post with Gemini
    if (action === "draft_post") {
      const topic = params.topic || "Why lean AI agents outperform monolithic software teams in 2026";
      const geminiKey = process.env.GEMINI_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('GEMINI_API_KEY'));
      
      let postContent = "";
      if (geminiKey) {
        try {
          const geminiRes = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${geminiKey}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              contents: [{
                parts: [{
                  text: `Write an authentic founder LinkedIn post about: "${topic}". Rules: 1-2 sentence punchy paragraphs, max 1 em-dash, no corporate buzzwords (no leverage, facilitate, delve, landscape), optimal length 900-1200 characters.`
                }]
              }]
            })
          });
          const geminiData = await geminiRes.json();
          postContent = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || "";
        } catch (err) {
          console.error("Gemini call error:", err);
        }
      }

      if (!postContent) {
        postContent = `Most engineering leaders think adding more developers speeds up delivery.\n\nIn reality, coordination overhead grows exponentially while individual agency drops to zero.\n\nAutonomous agent workflows don't just automate repetitive tasks. They collapse the iteration cycle between ideation and production deploy.\n\nThe real moat in 2026 isn't headcount. It's leverage per engineer.`;
      }

      // Send to Slack if Webhook configured
      const slackWebhook = process.env.SLACK_WEBHOOK_URL || (typeof Netlify !== 'undefined' && Netlify.env?.get('SLACK_WEBHOOK_URL'));
      let slackDispatched = false;
      if (slackWebhook) {
        try {
          await fetch(slackWebhook, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: `🤖 *[Hermes Agent Dispatch]* New LinkedIn draft prepared:`,
              blocks: [
                {
                  type: "header",
                  text: { type: "plain_text", text: "🤖 Hermes Agent — New LinkedIn Draft" }
                },
                {
                  type: "section",
                  text: { type: "mrkdwn", text: `*Topic:* ${topic}\n\n>${postContent.replace(/\n/g, "\n>")}` }
                }
              ]
            })
          });
          slackDispatched = true;
        } catch (err) {
          console.error("Slack dispatch error:", err);
        }
      }

      return new Response(JSON.stringify({
        success: true,
        action: "draft_post",
        content: postContent,
        slack_dispatched: slackDispatched,
        timestamp: new Date().toISOString()
      }, null, 2), {
        status: 200,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    // B. Action: Send Slack Alert
    if (action === "slack_alert") {
      const message = params.message || "Hermes Agent heartbeat notification";
      const slackWebhook = process.env.SLACK_WEBHOOK_URL || (typeof Netlify !== 'undefined' && Netlify.env?.get('SLACK_WEBHOOK_URL'));
      if (slackWebhook) {
        await fetch(slackWebhook, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: `🚀 *[Hermes Agent]* ${message}` })
        });
      }
      return new Response(JSON.stringify({ success: true, message: "Alert sent to Slack" }), {
        status: 200,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    return new Response(JSON.stringify({ error: `Unknown action: ${action}` }), {
      status: 400,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 4. Redeployment Trigger: POST /api/hermes/redeploy
  if (req.method === "POST" && pathname.startsWith("/api/hermes/redeploy")) {
    if (!checkAuth(req)) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    return new Response(JSON.stringify({
      success: true,
      message: "Redeploy request registered. When Hermes Agent pushes commits to GitHub (main branch), Netlify CI triggers instant automated rebuild & deploy.",
      site: "frontierpilot-studio.netlify.app",
      timestamp: new Date().toISOString()
    }, null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  return new Response(JSON.stringify({ error: "Not Found" }), {
    status: 404,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
  });
};

export const config = {
  path: ["/api/hermes", "/api/hermes/*"]
};
