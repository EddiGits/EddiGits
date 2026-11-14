# OpenAI Decisions API (gpt-6-luna) — Product Profile for Comparison with TypeSafe AI's Jev

State as of 14 November 2026. "Official" = OpenAI's own docs/changelog/API reference (developers.openai.com) or OpenAI staff quoted on the record. Everything else is marked as third-party. OpenAI's announcement blog post (openai.com/index/decisions-api/) and openai.com/api/pricing/ returned HTTP 403 to the fetcher, so official facts below come from the developer docs, API reference and changelog, which were fetched directly.

## Launch timeline, current availability, model names and versions

### Takeaway
The Decisions API moved from a DevDay limited preview (29 Sep 2026) to public beta (6 Oct 2026) to general availability (22 Oct 2026) in just over three weeks. It runs exclusively on `gpt-6-luna`; no dated snapshot or Decisions-specific model variant is exposed by OpenAI (gateways use the alias `openai/gpt-6-luna-decisions`).

### Cited Findings
- OpenAI's API changelog, 6 Oct 2026 (Feature, gpt-6-luna, v1/decisions): the Decisions API launched in beta with gpt-6-luna, turning text and images into typed answers "10x faster than the Responses API" — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official)
- OpenAI's API changelog, 22 Oct 2026 (Update, gpt-6-luna, v1/decisions): the Decisions API became generally available with gpt-6-luna; GA added prompt caching ("Cache shared input across requests for prompt-cache discounts"), images in individual question instructions, JSON input via `input_json`, and "Each request now supports up to 400 questions, increased from 200 in public beta" — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official)
- OpenAI's API changelog, 15 Oct 2026: native Decisions integration added to GPT-Live (v1/live/sessions); Live can "call Decisions directly through native delegation," or decisions can be triggered as input/output transcript deltas arrive — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official)
- The changelog contains no "preview" entry distinct from the 6 Oct beta; the DevDay limited preview is documented only by press — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official)
- TechCrunch (Tim Fernholz, 30 Sep 2026): OpenAI revealed the Decisions API in an aside by Sam Altman at DevDay (Tuesday 29 Sep); released as a "limited preview"; Altman: "By focusing the model on that choice, we can make it extremely fast" — [TechCrunch](https://techcrunch.com/2026/09/30/openais-jev-clone-could-help-the-frontier-lab-stop-its-swarming-agents) (third-party, on-record OpenAI quote)
- gpt-6-luna itself launched 22 Sep 2026 alongside GPT-6 Sol (changelog, Feature) — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official)
- The Decisions guide: `gpt-6-luna` is "the only currently supported model"; no snapshot names listed — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- API reference: `model` — "Only `gpt-6-luna` is supported" — [OpenAI API reference, decisions.create](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- Mixed-news (7 Oct 2026) observed that the gpt-6-luna model page's 18-row endpoint-support table did not list v1/decisions at beta launch; beta guide said GA expected "in the coming weeks" — [Mixed-news](https://mixed-news.com/en/openai-decisions-api-beta-gpt-6-luna-endpoint-table/) (third-party)
- Parallel's comparison table: OpenAI "Preview Sep 29, beta Oct 6, GA Oct 22, 2026"; Jev launched Sep 15, 2026 (1.14 on Oct 14) — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party, competitor; facts "checked November 6, 2026")
- Unite.AI (22 Oct 2026, AI-generated article reviewed by editors): GA on 22 Oct 2026; also lists Decisions Playground for text/image testing and usage endpoint `GET /v1/organization/usage/decisions` — [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/) (third-party)
- Azure: Classmethod (25 Oct 2026) reports Decisions API GA on Azure OpenAI / Microsoft Foundry on 22 Oct 2026, endpoint `/openai/v1/decisions` on the Azure resource, gpt-6-luna deployment required, rolling out to Luna regions with East US 2 excluded, API-key or Entra ID auth — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)

### Inferences
- OpenAI's "preview" phase was effectively a 7-day gated access period; developers comparing to Jev should treat 6 Oct 2026 as the first date the public contract (schema, pricing) existed.
- There is no model versioning story for Decisions today: customers cannot pin a Luna snapshot for decision behaviour, whereas Jev exposes `jev-1.13.0` / `jev-1.14.0` / `jev-latest` (per Parallel's table).

### Gaps
- OpenAI's announcement blog post (openai.com/index/decisions-api/) could not be fetched (HTTP 403); exact announcement wording unverified.
- No Microsoft Learn page for Azure Decisions API was found in search; Azure GA details rest on one third-party write-up.

## Request and response shape; question types and how they map to Jev's Choice / Score / Noul

### Takeaway
A request is `{model, input, questions[]}`; each question is `predicate` (→ probability 0–1), `choice` (→ chosen value + per-option probabilities + confidence) or `score` (→ probability-weighted average over 2–10 ordered levels + per-level probabilities + confidence). These map one-to-one to Jev's Noul, Choice and Score; OpenAI has no equivalent of Jev 1.14's `box` type.

### Cited Findings
- Endpoint `POST /v1/decisions`; request has `model`, `input` (text string, or ordered array of messages, tool calls and tool outputs) and `questions` (1–400) — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- Question types per the guide: `predicate` returns `probability` (0–1 estimate the condition is true); `choice` takes `choices` each with `value` and optional `description`, returns `choice`, `probabilities`, `confidence`; `score` takes 2–10 `levels` each with `label` and `description`, ordered lowest to highest, returns `score` (probability-weighted average of 0-based level indices, "can fall between levels"), plus `probabilities` and `confidence` — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- `instructions` on a question is a string or a non-empty array of `input_text` / `input_image` parts (no `role` wrapper), enabling question-specific images — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- API reference constraints: `questions` 1–400 items, answers returned in the same order; `choice.choices` 2–255 unique items, `value` string or boolean ("1" and true are distinct); `score.levels` 2–10; `instructions` up to 1,048,576 chars or 1–16,384 parts of text/image/JSON; `name` optional — [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- Response `Decision` object: `answers[]` (one per question, in order; types predicate/choice/score/refusal), `model`, `usage` with `input_tokens`, `input_tokens_details.{cached_tokens, cache_write_tokens}`, `output_tokens`, `output_tokens_details.reasoning_tokens`, `total_tokens` — [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- A `refusal` answer affects only that question; other questions are still answered — [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- OpenAI's own example response (guide): predicate `visible_damage` with `probability` 0.92; API-reference example: input "The package arrived with a broken screen." → predicate `damaged` probability 0.95 — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions); [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- Score example in OpenAI's guide (as reported by Mixed-news): probabilities 0.1/0.7/0.2 over three levels → score 1.1 — [Mixed-news](https://mixed-news.com/en/openai-decisions-api-beta-gpt-6-luna-endpoint-table/) (third-party quoting official docs)
- Dependent decisions require separate requests: "A question that depends on an earlier answer needs a separate request" — [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/) and [Mixed-news](https://mixed-news.com/en/openai-decisions-api-beta-gpt-6-luna-endpoint-table/) (third-party, both paraphrasing OpenAI docs)
- Jev's types: Noul = probability a condition holds; Choice = selected option + per-option probability + confidence; Score = probability-weighted position on an ordered rubric + full distribution; types can be mixed in one call — [Firecrawl](https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev) (third-party)
- Parallel's table: OpenAI question types "predicate, choice, score"; Jev "noul, choice, score, box"; OpenAI names questions via an array with `name` on each, Jev uses an object keyed by name — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party)
- Vercel's gateway docs state the same contract and add: unnamed questions return `name: null`; a request with refused questions is billed for its input like any other — [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) (third-party, launch partner)

### Concrete request/response example (Vercel's OpenAI-SDK example; identical shape to OpenAI's, differing only in base URL and model slug)
```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Vercel version uses base_url="https://ai-gateway.vercel.sh/v1"

decision = client.decisions.create(
    model="gpt-6-luna",   # on Vercel: "openai/gpt-6-luna-decisions"
    input="The package arrived with a broken screen. I want my money back.",
    questions=[
        {"type": "predicate", "name": "damaged",
         "instructions": "Does the customer report a damaged item?"},
        {"type": "choice", "name": "queue",
         "instructions": "Which team should handle this ticket?",
         "choices": [{"value": "billing", "description": "Refunds and payments"},
                     {"value": "shipping", "description": "Delivery and damaged items"}]},
        {"type": "score", "name": "urgency",
         "instructions": "How urgent is this ticket?",
         "levels": [{"label": "low"}, {"label": "medium"}, {"label": "high"}]},
    ],
)
print(decision.answers)
```
Response shape (from the same source):
```json
{
  "answers": [
    { "type": "predicate", "name": "damaged", "probability": 0.95 },
    { "type": "choice", "name": "queue", "choice": "shipping", "confidence": 0.81,
      "probabilities": [ { "value": "billing", "probability": 0.19 },
                         { "value": "shipping", "probability": 0.81 } ] },
    { "type": "score", "name": "urgency", "score": 1.3, "confidence": 0.62,
      "probabilities": [ { "value": 0, "label": "low", "probability": 0.08 },
                         { "value": 1, "label": "medium", "probability": 0.54 },
                         { "value": 2, "label": "high", "probability": 0.38 } ] }
  ],
  "usage": { "input_tokens": 96, "output_tokens": 0, "total_tokens": 96 }
}
```
Source: [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions). Minimal curl against OpenAI directly (shape per OpenAI API reference):
```bash
curl https://api.openai.com/v1/decisions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model":"gpt-6-luna","input":"The package arrived with a broken screen.",
       "questions":[{"type":"predicate","name":"damaged","instructions":"Does the customer report a damaged item?"}]}'
```
JSON input example (from Vercel docs, same as OpenAI's `input_json` part):
```json
{ "model": "gpt-6-luna",
  "input": [{ "role": "user", "content": [
      { "type": "input_text", "text": "Review this order." },
      { "type": "input_json", "data": { "order": { "id": "A-1", "total": 42.5, "status": "refunded" } } } ] }],
  "questions": [{ "type": "predicate", "name": "refunded", "instructions": "Is the order refunded?" }] }
```

### Inferences
- Mapping for the comparison: OpenAI `predicate` ≈ Jev `Noul`; OpenAI `choice` ≈ Jev `Choice`; OpenAI `score` ≈ Jev `Score`. Both return full distributions and a separate `confidence` for choice/score.
- OpenAI's `output_tokens_details.reasoning_tokens` field in the usage object hints the backend is a constrained generative model rather than a pure classifier head (consistent with reports that Luna was "reconfigured," not retrained).

### Gaps
- OpenAI's own Python/TypeScript snippets could not be reproduced verbatim by the fetch tool (quote-length limits); the Python example above is Vercel's OpenAI-SDK code, which Vercel states uses OpenAI's exact request/response shapes.
- No official documentation of a few-shot `examples` field was found; the API reference lists no such parameter.

## Supported inputs; context and option limits

### Takeaway
Inputs are text, multi-role messages, function/custom tool calls and outputs, `input_json`, and images (base64 data URLs or, since GA, public HTTP(S) URLs). Hard limits: 1–400 questions, 2–255 choices, 2–10 score levels, up to 128 images per request (third-party), and Luna's ~1.05M-token window with a >272K long-context price tier; OpenAI publishes no Decisions-specific context cap.

### Cited Findings
- Input types (guide): text strings; user messages with `input_text`, `input_image`, `input_json` (`input_json` user-role only); developer/system messages text only; assistant messages `output_text` or refusals; function and custom tool outputs with text and images matched by `call_id` — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- Images: "inline base64 data URLs or publicly accessible HTTP or HTTPS URLs"; `file_id`, files, audio and item references not supported — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- API reference: `input_image.image_url` up to 1,073,741,824 chars, `detail` low/high/auto(default)/original; `input_json.data` limited to 32 nesting levels, 10,000 values, 256 KiB compact UTF-8; `input` string up to 10,485,760 chars or array up to 131,072 items; user content up to 16,384 parts — [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- Beta-era restriction (7 Oct 2026): images had to be inline base64; hosted URLs and file_id not supported; limit 128 image parts per request — [Mixed-news](https://mixed-news.com/en/openai-decisions-api-beta-gpt-6-luna-endpoint-table/) (third-party quoting beta docs); Vercel's docs (last updated 2026-10-08) still say "Images must be base64-encoded data URLs. External URLs and file IDs aren't supported, and a request can include at most 128 images" — [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) (third-party)
- GA added public HTTP/HTTPS image URLs and images inside question instructions — [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/) (third-party); confirmed by the official guide wording above.
- Classmethod (Azure test): 128 images per request, 32 MB total per request — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)
- Context: OpenRouter lists `openai/gpt-6-luna-decisions` at 1,050,000 tokens context, text + image input — [OpenRouter](https://openrouter.ai/openai/gpt-6-luna-decisions) (third-party); Vercel lists the same 1,050,000 context, max output tokens 0 — [Vercel model page](https://vercel.com/ai-gateway/models/gpt-6-luna-decisions) (third-party)
- Long-context threshold on OpenAI's pricing page: "Short context: ≤272K input tokens. Long context: >272K input tokens" (for gpt-6-luna generally; guide says long-context multipliers apply to Decisions) — [OpenAI pricing docs](https://developers.openai.com/api/docs/pricing); [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- Jev limits for comparison: "64K per request, 32K per question" context; up to 255 options per choice; up to 10 score levels; text, object or images (images experimental, behind a header in 1.13/1.14); no fixed question cap within context — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party); Firecrawl: Jev context 32K on OpenRouter / 64K per TypeSafe docs; Jev text-only at launch — [Firecrawl](https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev) (third-party)
- Vercel: `typesafe-ai/jev` returns a 400 for requests with images; `openai/gpt-6-luna-decisions` accepts images — [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) (third-party)

### Inferences
- OpenAI's effective context advantage over Jev is roughly 16x (≈1.05M vs 64K), but the price doubles above 272K input tokens, and TypeSafe's own "jaggedness" docs warn accuracy drops with irrelevant state, so very long inputs are not necessarily a practical win for either.
- Both products allow up to 255 options per choice question and up to 10 score levels, so option/level limits are not a differentiator.

### Gaps
- OpenAI's guide does not state the max image count or request size; the 128-image and 32 MB figures are third-party (the latter from one source).
- No official statement of a Decisions-specific context window; the 1.05M figure comes from gateway listings.

## Pricing and billing model vs Jev ($0.042/M input, free output)

### Takeaway
OpenAI charges $0.10 per million uncached input tokens and nothing for output; since GA, cache hits are discounted (reported $0.01/M) and cache writes are charged. That is 2.4x Jev's $0.042/M input (both free output); on OpenAI's pricing page Decisions has no Batch/Flex/Fast row, and a 10% uplift applies to regional-processing endpoints, with a 2x long-context tier above 272K tokens.

### Cited Findings
- Official guide (GA): uncached input $0.10 per 1M tokens; "Cache hits get discounted input pricing. Cache writes are charged"; output tokens not charged; "Regional processing premiums and long-context input multipliers apply" (no figures on the page) — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- Beta-era guide wording (7 Oct 2026): input $0.10/1M with "no cache-read, cache-write, or output-token charges" — [Mixed-news](https://mixed-news.com/en/openai-decisions-api-beta-gpt-6-luna-endpoint-table/) (third-party quoting official docs). This changed at GA when prompt caching was introduced.
- OpenAI's pricing page has no Decisions API section; gpt-6-luna Standard short-context rows: input $0.10, cached $0.01, 30m cache write $0.125, 12h write $0.25, output $0.50; long-context (>272K): input $0.20, cached $0.02; Batch/Flex short: $0.05 input; Fast short: $0.20 input — [OpenAI pricing docs](https://developers.openai.com/api/docs/pricing) (official)
- "Regional processing (data residency) endpoints are charged a 10% uplift for models released on or after March 5, 2026"; FedRAMP endpoints also 10% uplift — [OpenAI pricing docs](https://developers.openai.com/api/docs/pricing) (official)
- Changelog gpt-6-luna launch pricing (22 Sep 2026): "$0.10 input, $0.01 cached input, and $0.50 output" — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official)
- Decisions cached-input rate reported as $0.01/M by Unite.AI, WinBuzzer and Classmethod (Azure) — [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/); [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/); [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)
- Prompt caching mechanics (official): implicit breakpoint at end of shared `input`; reusable prefix must be ≥1,024 tokens and question content does not count; `prompt_cache_key` partitions reuse; explicit mode via `prompt_cache_breakpoint`; breakpoints not supported in question instructions; `ttl` only "30m" — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions); [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- Usage reporting: `GET /v1/organization/usage/decisions` with admin key holding `api.usage.read`; `num_model_requests` counts requests, not questions — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- OpenRouter lists `openai/gpt-6-luna-decisions` at $0.10/M input, $0.00/M output — [OpenRouter](https://openrouter.ai/openai/gpt-6-luna-decisions) (third-party); Vercel lists $0.10/M input, billed "at Decisions API rates" as a separate ID from `openai/gpt-6-luna` — [Vercel model page](https://vercel.com/ai-gateway/models/gpt-6-luna-decisions); [Vercel changelog](https://vercel.com/changelog/openai-decisions-api-now-available-on-ai-gateway) (third-party)
- Worked example (Vercel response metadata): 96 input tokens → gateway cost "0.0000096" USD — [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) (third-party)
- Azure test: 477-token text request ≈ $0.000048; 1,207-token request with one 960×640 image ≈ $0.00012 — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)
- WinBuzzer illustration: 1M calls × 2,000 input tokens = $200 via Decisions vs $225 via Responses (assuming 50 output tokens/answer) — [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/) (third-party)
- Parallel's cost example (1,000 records × 5 questions × 1,500-token state): Jev ≈ $0.076 (1.8M tokens), OpenAI ≈ $0.18; with +8,000 tokens web text per record Jev ≈ $0.41, OpenAI ≈ $0.98; caching does not help when each record's state differs — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party, competitor)
- Jev price: $0.042 per 1M input tokens, output free — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md); [Firecrawl](https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev); [eesel.ai](https://www.eesel.ai/blog/typesafe-jev-pricing) (third-party; eesel notes TypeSafe has no dedicated pricing page)
- Microsoft's separate Microsoft-Decision-1 (Azure, 9 Oct 2026, text-only, `/providers/microsoft/v1/systemone`) is priced at $0.042/M input, matching Jev — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)

### Inferences
- Like-for-like on uncached input, OpenAI is 2.38x Jev's price ($0.10 vs $0.042). With a cacheable shared prefix ≥1,024 tokens and the reported $0.01 cache-read rate, OpenAI's blended cost can fall below Jev's for workloads that repeat a large shared context, but cache writes are charged (rate not published for Decisions; Luna's standard 30m write is $0.125/M) and per-record varying state defeats caching.
- Because Decisions has no Batch/Flex row on OpenAI's pricing page and output is already free, the discount levers available on Responses (50% Batch/Flex) do not appear to exist for Decisions; the only published modifiers are the long-context 2x and the 10% regional uplift.

### Gaps
- OpenAI publishes no explicit Decisions cache-read or cache-write dollar rate; the $0.01 cached figure is third-party (consistent across three outlets).
- No official statement on whether Decisions supports the Batch API, Flex processing, or Fast mode; absence from the pricing table suggests not, but this is unconfirmed.
- Enterprise/volume or tier discounts for Decisions: no information found.

## Official latency, accuracy and calibration claims and OpenAI's evidence

### Takeaway
OpenAI's only quantified claim is "about 10x faster than the Responses API" (DevDay slide: ~150 ms vs ~1.6 s for Luna via Responses), with no published benchmark, and it makes no formal accuracy or calibration claim; evidence is limited to customer anecdotes (Box, Datadog, Ramp, Sierra, Speak) reporting "same/comparable accuracy." Third-party measurements show 1.4–5.5 s latencies via Azure and near-random accuracy on web-fact questions without context.

### Cited Findings
- Official: "The Decisions API evaluates text, images, and JSON and returns typed answers about 10x faster than the Responses API" — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official); changelog: "10x faster than the Responses API" — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official)
- DevDay slide (per Firecrawl): 150 ms for Decisions vs 1.6 s for the GPT-6 Luna API; OpenAI product lead Tibo Sottiaux: "less than a few hundreds of milliseconds end to end" — [Firecrawl](https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev) (third-party reporting OpenAI statements; test conditions unstated)
- Customer claims relayed in GA coverage: Box ~5x faster route selection across 30 certificate-of-insurance cases with "same accuracy as the Responses API"; Datadog 40x faster p95 vs frontier models with "comparable accuracy"; Ramp 4x faster and 30% cheaper than gpt-6-luna with "no loss of accuracy"; Sierra <280 ms p95 for next-action selection, ~3x faster and 90% lower cost per call, "no drop in customer outcomes"; Speak time-to-next-action 1.4 s → 0.13 s with GPT-Live — [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/) (third-party, paraphrasing OpenAI's GA materials)
- Speak CTO Andrew Hsu told TechCrunch the trial cut interval between actions from 1.4 s to 0.13 s — [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/) (third-party)
- "OpenAI reconfigured Luna for faster, cheaper inference rather than training a new model" — [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/); Parallel: "TechCrunch reported it reconfigured GPT-6 Luna rather than training a separate calibrated model" — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party)
- No formal calibration metrics published; "Choice questions return confidence values. The article gives no formal calibration metrics" — [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/) (third-party); TechCrunch: "a key open question is how well calibrated each decision model's outputs will be to real-world outcomes" — [TechCrunch](https://techcrunch.com/2026/09/30/openais-jev-clone-could-help-the-frontier-lab-stop-its-swarming-agents) (third-party)
- Independent latency observations (Azure, eastus, 25 Oct 2026): text request 2,045 / 1,607 / 1,400 ms; image request 5,530 / 2,421 / 2,793 ms; answers identical across three runs — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)
- Independent accuracy (Parallel, competitor): "answer in input" 231-question JevBench subset: OpenAI 90.0%, Parallel 89.6%, Jev 88.3%; PWS-Decisions (300 dated web questions, mean of 3 runs, random 42.4%): OpenAI without web context 41.7% ($0.023/1,000 questions), Jev 1.14 without web context 33.4% ($0.019/1,000), Parallel 76.2%, GPT-6 Luna with native web search 97.3% at p50 7.42 s and $16.52/1,000; Artificial Analysis Decision Index (5 Nov 2026, 23 models): Jev 1.14 ranked 10th at 57.1, GPT-6 Luna 21st at 48.5 — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party, competitor; "We build Parallel's Decisions API, so weigh that")
- Calibration critique: Classmethod observed 0.99 probability for a coat colour that could read as black or brown, arguing confidence "seemed excessive" — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)
- Jev's comparison baseline: OpenRouter production telemetry as of 1 Oct 2026, P50 0.21 s, P95 0.34 s, P99 0.75 s; TypeSafe describes training as "Reinforcement Learning for Calibrated Decisions" — [Firecrawl](https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev) (third-party)
- Agent-monitoring cost anecdote (Jev, not OpenAI): $2.94 with Jev vs $372 with a frontier LLM — [TechCrunch](https://techcrunch.com/2026/09/30/openais-jev-clone-could-help-the-frontier-lab-stop-its-swarming-agents) (third-party)

### Inferences
- OpenAI's "10x" is relative to its own Responses API on the same model, not to Jev or any external baseline; the observed Azure latencies (1.4–2 s text) are an order of magnitude above the 150 ms slide figure, suggesting the claim reflects best-case or server-side timing.
- Both vendors return a `confidence` scalar, but only TypeSafe asserts a calibration-oriented training method; neither publishes reliability diagrams or ECE figures in the sources found.

### Gaps
- No OpenAI-published latency distribution (p50/p95), accuracy benchmark, or calibration study was found; the customer figures are paraphrased in press, not primary.
- Could not access OpenAI's blog post to verify the customer quotes verbatim.

## Feature comparison: what OpenAI has that Jev lacks, and vice versa

### Takeaway
OpenAI's distinct advantages are production-grade image input (base64 or URL, per-question images, up to 128/request), native `input_json`, conversation/tool-call history as input, prompt caching, GPT-Live voice integration, ~1.05M context, and enterprise controls (ZDR, HIPAA, data residency, Private Link, Azure). Jev's advantages are 2.4x lower price, model versioning, an additional `box` question type, an explicit calibration training claim, and broader gateway distribution (OpenRouter, Cloudflare Workers AI, Vercel, Eden AI, Venice).

### Cited Findings
- OpenAI inputs: text, messages, tool calls/outputs, JSON, images; Jev: text, object, or images (experimental) — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party)
- OpenAI supports evaluating "conversation history ... alongside function/custom tool calls and outputs" — [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/) (third-party); confirmed by API reference item types `function_call`, `function_call_output`, `custom_tool_call`, `custom_tool_call_output` — [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- GPT-Live integration: Live can call Decisions directly or trigger decisions as transcript deltas arrive (configured via `session.triggers` per Unite.AI) — [OpenAI API changelog](https://developers.openai.com/api/docs/changelog) (official); [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/) (third-party)
- Jev image support: "experimental"; TypeSafe "says it cannot vouch for them in production" — [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/) (third-party); Jev 1.13/1.14 images behind an experimental header; 1.14 adds `box` type — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party)
- Caching: OpenAI prompt caching with cache writes charged; Jev "Not documented" — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party)
- Neither has web search or citations — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party)
- Distribution: OpenAI Decisions on OpenRouter (`openai/gpt-6-luna-decisions`, added 8 Oct 2026, not available via EU in-region routing per the Japanese page) — [OpenRouter](https://openrouter.ai/openai/gpt-6-luna-decisions); [Remio](https://www.remio.ai/post/gpt-6-luna-decisions-hits-openrouter-but-fast-routing-still-needs-guardrails) (third-party); on Vercel AI Gateway since 7 Oct 2026 — [Vercel changelog](https://vercel.com/changelog/openai-decisions-api-now-available-on-ai-gateway) (third-party); on Azure OpenAI/Foundry since 22 Oct 2026 — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party); Langfuse AI Gateway added it 11 Nov 2026 — [Langfuse changelog](https://langfuse.com/changelog/2026-11-11-ai-gateway-openai-decisions.md) (third-party); also LLM Gateway and Portkey expose OpenAI-compatible `/decisions` — [LLM Gateway](https://llmgateway.io/blog/openai-decisions-api); [Portkey](https://portkey.ai/docs/api-reference/inference-api/decisions.md) (third-party)
- Jev distribution: OpenRouter (`POST https://openrouter.ai/api/alpha/decisions`, `typesafe/jev-1.13`), Cloudflare Workers AI (`typesafe/jev`), Vercel (`typesafe-ai/jev`), Eden AI (`typesafe/jev-latest`), Venice beta — [Firecrawl](https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev); [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md); [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) (third-party)
- SDKs: OpenAI's guide provides examples in curl, TypeScript, Python, Go, Java and Ruby — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official); `client.decisions.create` requires OpenAI SDK ≥7.30.0 (JavaScript) or ≥3.26.0 (Python) — [Vercel changelog](https://vercel.com/changelog/openai-decisions-api-now-available-on-ai-gateway) (third-party); TypeSafe publishes full schemas and Python/JS SDKs — [Firecrawl](https://www.firecrawl.dev/blog/openai-decisions-api-vs-jev) (third-party)
- Vercel's AI SDK `decide` function and a TypeSafe-compatible endpoint are both offered, so Jev and OpenAI can be swapped behind one gateway; `providerOptions.gateway.models` enables decision fallbacks between them — [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) (third-party)
- Playground: OpenAI offers a Decisions Playground at platform.openai.com/decisions for text or images — [Mixed-news](https://mixed-news.com/en/openai-decisions-api-beta-gpt-6-luna-endpoint-table/); [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/) (third-party)

### Inferences
- The OpenAI SDK's `decisions.create` method has become a de facto wire standard: Vercel, LLM Gateway, Portkey, Langfuse and Eden AI all expose it, and Jev is routable through it, which lowers switching cost in both directions.
- Jev's "no fixed question cap" vs OpenAI's 400-question cap matters only for extreme batch-labelling workloads; for most routing use cases OpenAI's cap is not binding.

### Gaps
- No official OpenAI statement on few-shot examples; no `examples` parameter exists in the API reference. Whether Jev supports few-shot was likewise not found in these sources.
- Azure region list and quota for Decisions not found in Microsoft documentation.

## Documented limitations, rate limits, data retention and ZDR

### Takeaway
OpenAI's stated limitations: one model only, no files/audio/item references/file_id, dependent decisions need separate requests, no custom JSON/free-text/tool-call outputs (use Responses for those), cache breakpoints unsupported in question instructions, no web search. ZDR and HIPAA are available to eligible customers, with US and EU (EEA+Switzerland) regional processing, data residency in all supported regions and Private Link. No Decisions-specific rate limits are published anywhere found.

### Cited Findings
- Not supported inputs: "Files, audio, and item references aren't supported." "This endpoint doesn't support `file_id` inputs." — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- Only `gpt-6-luna` accepted as `model`; choice values must be unique; `ttl` only "30m" — [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- Cache breakpoints not supported in question instructions; prefix must be ≥1,024 tokens excluding question content — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- Guidance to use Responses API instead for custom JSON objects, written explanations, or model-requested tool calls (Structured Outputs / function calling) — [Unite.AI](https://www.unite.ai/openai-makes-decisions-api-generally-available-with-gpt-6-luna/); [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/) (third-party, paraphrasing OpenAI docs)
- Dependent multi-step logic requires additional requests — [WinBuzzer](https://winbuzzer.com/2026/10/24/openai-ai-decision-service-leaves-beta-with-voice-integration-xcxwbn/); [Mixed-news](https://mixed-news.com/en/openai-decisions-api-beta-gpt-6-luna-endpoint-table/) (third-party)
- Data controls (official guide): "Zero Data Retention (ZDR) and HIPAA use are supported for eligible customers"; data residency in all supported API regions; regional processing in the United States and Europe (EEA + Switzerland); Private Link supported — [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions) (official)
- Regional processing endpoints carry a 10% price uplift — [OpenAI pricing docs](https://developers.openai.com/api/docs/pricing) (official)
- `safety_identifier` (0–128 chars) accepted as an opaque end-user identifier — [OpenAI API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) (official)
- Rate limits: the Decisions guide and API reference do not mention them; OpenAI's general API docs say limits are returned in `x-ratelimit-*` headers — [OpenAI API reference overview](https://developers.openai.com/api/docs/api-reference/decisions) (official, general); a targeted search found no Decisions-specific RPM/TPM figures — [OpenAI rate limits guide (via search)](https://developers.openai.com/docs/guides/rate-limits)
- OpenRouter (Japanese page): the decisions model is not currently available via EU in-region routing — [OpenRouter](https://openrouter.ai/ja/openai/gpt-6-luna-decisions) (third-party)
- Azure: East US 2 excluded during rollout; ZDR/data handling not described — [Classmethod](https://dev.classmethod.jp/en/articles/azure-openai-decisions-api-ga/) (third-party)
- Third-party caveats: scored near random (41.7%) on dated web-fact questions without supplied context; no web search or citations; options and score-level caps not stated in the guide — [Parallel](https://parallel.ai/articles/openai-decisions-api-vs-jev-vs-parallel.md) (third-party, competitor)
- Vercel gateway: `providerOptions.gateway.zeroDataRetention: true` can be required per request — [Vercel AI Gateway docs](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-decisions) (third-party)

### Inferences
- Since Decisions runs on gpt-6-luna, it most likely inherits the account's gpt-6-luna RPM/TPM tier limits, but OpenAI has not said so; a comparison should flag rate limits as "undocumented" rather than quote Luna's limits.
- OpenAI's enterprise data controls (ZDR, HIPAA, residency, Private Link, Azure) are a clear differentiator against Jev, for which no equivalent retention terms surfaced in these sources.

### Gaps
- No Decisions-specific rate limits (RPM/TPM/images per minute) found in any official or third-party source.
- Jev's data-retention / ZDR terms were not researched here (out of scope) and are not in the sources found.
- The named third-party pieces stacktoheap.com ("OpenAI Decisions API: How Does Jev's Big-Lab Competitor Fare?"), valyu.ai ("Jev vs OpenAI Decisions API") and medium.com/@mvpkenlin (GA post) did not appear in any search results and could not be fetched; no The Verge coverage was found.
- OpenAI's announcement post and openai.com pricing page were inaccessible (HTTP 403), so their exact wording is unverified; the developer docs, changelog and API reference were used instead.
