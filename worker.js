/**
 * DeepL translation proxy for the 英単語しりとり (English Word Chain) game.
 *
 * This Worker hides your DeepL API key from the browser. The game's HTML/JS
 * calls THIS worker's URL instead of calling DeepL directly, so the key is
 * never exposed in client-side code that anyone could view.
 *
 * ---- Setup ----
 * 1. Create a free DeepL API account: https://www.deepl.com/pro-api
 *    (the "DeepL API Free" plan has a monthly character quota at no cost)
 * 2. Install Wrangler (Cloudflare's CLI):  npm install -g wrangler
 * 3. Log in:                                wrangler login
 * 4. From this folder, store your key as a secret (never goes in source code):
 *      wrangler secret put DEEPL_KEY
 *    (paste your DeepL API key when prompted)
 * 5. Deploy:                                wrangler deploy
 * 6. Wrangler will print a URL like:
 *      https://word-chain-translate.<your-subdomain>.workers.dev
 *    Put that URL into the game's DEEPL_PROXY_URL constant (see the game file).
 *
 * ---- Usage from the browser ----
 *   GET  https://<your-worker>.workers.dev/?word=apple
 *   →    { "word": "apple", "translated": "りんご" }
 *
 * ---- Notes ----
 * - CORS is enabled for all origins (*) by default below. If you want to
 *   restrict it to only your GitHub Pages site, change ALLOWED_ORIGIN.
 * - DeepL's free plan uses the api-free.deepl.com host and keys ending in ":fx".
 *   If you upgrade to a paid plan, change DEEPL_API_URL to api.deepl.com.
 */

const ALLOWED_ORIGIN = "*"; // e.g. "https://yourname.github.io" to restrict
const DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"; // change to api.deepl.com for paid plans

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }

    const url = new URL(request.url);
    const word = url.searchParams.get("word");

    if (!word) {
      return new Response(JSON.stringify({ error: "missing 'word' query parameter" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }

    if (!env.DEEPL_KEY) {
      return new Response(JSON.stringify({ error: "DEEPL_KEY secret is not configured on this Worker" }), {
        status: 500,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }

    try {
      const deeplRes = await fetch(DEEPL_API_URL, {
        method: "POST",
        headers: {
          "Authorization": `DeepL-Auth-Key ${env.DEEPL_KEY}`,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          text: word,
          source_lang: "EN",
          target_lang: "JA",
        }),
      });

      if (!deeplRes.ok) {
        const errText = await deeplRes.text();
        return new Response(JSON.stringify({ error: "DeepL API error", detail: errText }), {
          status: deeplRes.status,
          headers: { "Content-Type": "application/json", ...corsHeaders() },
        });
      }

      const data = await deeplRes.json();
      const translated = data.translations && data.translations[0] && data.translations[0].text;

      return new Response(JSON.stringify({ word, translated: translated || null }), {
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: "proxy request failed", detail: String(err) }), {
        status: 502,
        headers: { "Content-Type": "application/json", ...corsHeaders() },
      });
    }
  },
};
