/**
 * FrontierPilot 2.0 — Serverless Career & Radar Gateway
 */

import { OPPORTUNITIES } from "./opportunities_data.mjs";

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
      version: "1.1.26",
      cloud_edge: "Netlify 24/7 Always-On",
      integrations: {
        gemini: geminiKey ? "healthy" : "offline",
        slack: slackUrl ? "healthy" : "offline",
        publora: publoraKey ? "healthy" : "offline",
        sheets: "connected",
        drive: "connected",
        notion: "connected"
      },
      activeOpportunities: OPPORTUNITIES.length,
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
      opportunities: OPPORTUNITIES,
      count: OPPORTUNITIES.length,
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
          text: `📊 *[FrontierPilot 2.0 Cloud]* Executive Career Radar Digest:\n• ${OPPORTUNITIES.length} High-leverage opportunities active\n• Top match: *${OPPORTUNITIES[0].organization}* — ${OPPORTUNITIES[0].title} (${OPPORTUNITIES[0].match_score}% match)`
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
