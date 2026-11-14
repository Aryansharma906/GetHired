/**
 * FrontierPilot 2.0 — Serverless LinkedIn Autonomous Creator Studio API
 */

const SAMPLE_DRAFTS = [
  {
    id: "draft_2026_01",
    topic: "Why small AI teams beat 50-person agencies",
    hookFormula: "Contrarian Truth",
    content: "Most engineering leaders think adding more developers speeds up delivery.\n\nIn reality, coordination overhead grows exponentially while individual agency drops to zero.\n\nAutonomous agent workflows don't just automate repetitive tasks. They collapse the iteration cycle between ideation and production deploy.\n\nThe real moat in 2026 isn't headcount. It's leverage per engineer.",
    status: "published",
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    characterCount: 412
  },
  {
    id: "draft_2026_02",
    topic: "Why we killed our 3-tier staging environments",
    hookFormula: "Radical Transparency",
    content: "We spent 3 months maintaining staging environments that never matched production.\n\nEvery time staging passed, production failed anyway on edge configurations.\n\nLast month we deleted staging entirely and moved to ephemeral preview branches with automated canary testing.\n\nTime-to-production dropped by 74%. Zero regressions reported.",
    status: "pending_approval",
    createdAt: new Date().toISOString(),
    characterCount: 398
  },
  {
    id: "draft_2026_03",
    topic: "From 1st-year student to evaluating frontier LLMs at scale",
    hookFormula: "Before vs After",
    content: "Six months ago, I was reading benchmark papers from the outside.\n\nToday, I run automated red-teaming harnesses and prompt vulnerability checks against production foundation models.\n\nThe difference wasn't academic credentials.\n\nIt was building public proof-of-work, evaluating real failure modes, and shipping code every single week.",
    status: "scheduled",
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    characterCount: 425
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

  // 1. List drafts: GET /api/drafts
  if (req.method === "GET") {
    return new Response(JSON.stringify(SAMPLE_DRAFTS, null, 2), {
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
      content: generatedText,
      status: "pending_approval",
      createdAt: new Date().toISOString(),
      characterCount: generatedText.length
    };

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

    return new Response(JSON.stringify({ success: true, message: `Draft ${draftId} rejected` }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }

  // Fallback
  return new Response(JSON.stringify({ success: true, drafts: SAMPLE_DRAFTS }), {
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
