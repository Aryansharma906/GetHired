/**
 * FrontierPilot 2.0 — Serverless LinkedIn Autonomous Creator Studio API
 */

import { DRAFTS } from "./drafts_data.mjs";

let liveDrafts = [...DRAFTS];

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

  // 1. List drafts: GET /api/drafts
  if (req.method === "GET") {
    return new Response(JSON.stringify(liveDrafts, null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 2. Generate new post with Gemini: POST /api/drafts/generate
  if (req.method === "POST" && pathname.includes("/generate")) {
    let body = {};
    try {
      body = await req.json();
    } catch (e) {}

    const topic = body.topic || "Autonomous engineering agents vs traditional dev workflows";
    const geminiKey = process.env.GEMINI_API_KEY || (typeof Netlify !== 'undefined' && Netlify.env?.get('GEMINI_API_KEY'));

    let generatedText = "";
    if (geminiKey) {
      try {
        const geminiRes = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${geminiKey}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{
              parts: [{
                text: `Write an authentic founder LinkedIn post about: "${topic}". Rules: 1-2 sentence punchy paragraphs, max 1 em-dash, no corporate buzzwords, optimal length 900-1200 characters.`
              }]
            }]
          })
        });
        const resData = await geminiRes.json();
        generatedText = resData.candidates?.[0]?.content?.parts?.[0]?.text || "";
      } catch (err) {
        console.error("Gemini generation error:", err);
      }
    }

    if (!generatedText) {
      generatedText = `Most teams treat AI agents as fancy autocomplete.\n\nThe real unlock is delegating entire operational loops: automated tests, cloud edge deployments, and real-time approval gateways.\n\nWhen your system runs 24/7 on edge, you stop being a ticket-pusher and become an architect.\n\nThe future belongs to engineers who multiply leverage.`;
    }

    const newDraft = {
      id: `draft_${Date.now()}`,
      topic,
      hookFormula: "Direct Contrast",
      hook_formula: "Direct Contrast",
      content: generatedText,
      status: "pending_approval",
      createdAt: new Date().toISOString(),
      created_at: new Date().toISOString(),
      characterCount: generatedText.length,
      char_count: generatedText.length
    };

    liveDrafts.unshift(newDraft);

    // Slack Notification
    const slackWebhook = process.env.SLACK_WEBHOOK_URL || (typeof Netlify !== 'undefined' && Netlify.env?.get('SLACK_WEBHOOK_URL'));
    if (slackWebhook) {
      try {
        await fetch(slackWebhook, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: `📝 *[FrontierPilot 2.0 Cloud]* New Post Draft Generated:\n*Topic:* ${topic}\n\n${generatedText.slice(0, 200)}...`
          })
        });
      } catch (e) {}
    }

    return new Response(JSON.stringify({ success: true, draft: newDraft }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 3. Approve draft: POST /api/drafts/:id/approve
  if (req.method === "POST" && pathname.includes("/approve")) {
    const parts = pathname.split("/");
    const draftId = parts[3] || "draft";

    const target = liveDrafts.find(d => d.id === draftId);
    if (target) {
      target.status = "scheduled";
    }

    const slackWebhook = process.env.SLACK_WEBHOOK_URL || (typeof Netlify !== 'undefined' && Netlify.env?.get('SLACK_WEBHOOK_URL'));
    if (slackWebhook) {
      await fetch(slackWebhook, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: `🎉 *[FrontierPilot 2.0 Cloud]* Post Approved & Scheduled: \`${draftId}\` by Aryan Sharma.`
        })
      });
    }

    return new Response(JSON.stringify({ success: true, message: `Draft ${draftId} approved and scheduled` }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 4. Reject draft: POST /api/drafts/:id/reject
  if (req.method === "POST" && pathname.includes("/reject")) {
    const parts = pathname.split("/");
    const draftId = parts[3] || "draft";

    const target = liveDrafts.find(d => d.id === draftId);
    if (target) {
      target.status = "rejected";
    }

    return new Response(JSON.stringify({ success: true, message: `Draft ${draftId} rejected` }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // 5. Delete draft: DELETE /api/drafts/:id
  if (req.method === "DELETE") {
    const parts = pathname.split("/");
    const draftId = parts[3] || "draft";
    liveDrafts = liveDrafts.filter(d => d.id !== draftId);
    return new Response(JSON.stringify({ success: true, message: `Draft ${draftId} removed` }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // Fallback
  return new Response(JSON.stringify(liveDrafts, null, 2), {
    status: 200,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
  });
};

export const config = {
  path: [
    "/api/drafts",
    "/api/drafts/*"
  ]
};
