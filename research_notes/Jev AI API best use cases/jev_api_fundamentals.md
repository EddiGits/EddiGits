# Jev AI API (TypeSafe AI "System One" model) — Product Fundamentals

Research date: 2026-09-29. All claims dated where the source gives a date. "Official" = TypeSafe AI (typesafe.ai, docs.typesafe.ai, console.typesafe.ai). "Third-party" = everything else. Note: several look-alike domains (jevai.org, jevtypesafe.org, jevtypesafeai.com, thejevai.com, jevaiguide.com) are community/unofficial sites, not TypeSafe; jevai.org itself states "TypeSafe AI ships the model, core infrastructure, and native API execution" and describes itself as a separate hub — [jevai.org](https://jevai.org).

## Key Question 1: What is Jev, and what exactly does a request/response look like for Choice, Score, and Noul?

### Takeaway
Jev is TypeSafe AI's first "System One" model: a non-chat model that takes a State plus a set of typed Questions and returns typed answers (a Choice with a probability distribution, a Score on an ordered rubric, or a Noul yes/no probability) from a single `POST https://api.typesafe.ai/v1/systemone` call; all questions in a request are evaluated in parallel against the same state, and output tokens are always zero.

### Cited Findings

**What it is / positioning (official)**
- Jev is "TypeSafe's flagship model and the first System One model," which "evaluates typed questions against a state and returns structured results directly" for code consumption without text parsing — [docs.typesafe.ai Introduction](https://docs.typesafe.ai/introduction)
- System One models are "a new class of frontier models designed to make fast, structured decisions that software can use directly," optimized for automation rather than human conversation; Jev "achieves similar levels of intelligence on System One tasks compared to existing LLMs, while being two orders of magnitude faster and more efficient" — [TypeSafe blog: Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- Jev is described as "a frontier-intelligence function call: unstructured state in, typed probabilistic decisions out"; TypeSafe says it "took the opposite research direction" from chat LLMs and that "RLHF creates inherent issues such as mode dropping, overconfidence, and lack of reliability" — [typesafe.ai home](https://typesafe.ai)
- TypeSafe built "a new model architecture, parallel sampler for maximum efficiency, and training method they call Reinforcement Learning for Calibrated Decisions (RLCD)"; RLCD optimizes for "epistemically honest probabilities on System One tasks," contrasted with RLHF (human preference) and RLVR (verifiable rewards) — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- "While Jev gives up string generation, it's optimized for structured outputs and can't hallucinate"; TypeSafe claims a "0% type error rate (mathematically guaranteed by design)" — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- Name origin: Jev is "named after Jevons Paradox" (third-party press coverage of the launch release) — [Business Wire via Morningstar, 2026-09-15](https://www.morningstar.com/news/business-wire/20260915525333/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai)

**The three inputs: State, Model, Questions (official)**
- Request schema: `state` (string | object | array, required), `model` (string, required; docs say use `jev-latest`), `questions` (object keyed by user-chosen question IDs; each has `type` = `noul | choice | score`, `instructions` (string | object | array), and `criteria` whose shape varies by type) — [docs.typesafe.ai API Reference](https://docs.typesafe.ai/api.md)
- Common question fields: an ID (user-defined key identifying the answer), `type`, `instructions` (the judgment question/statement), `criteria` (options for Choice, ordered levels for Score, optional yes/no clarification for Noul) — [docs.typesafe.ai Primitives](https://docs.typesafe.ai/primitives.md)
- "All three question types can be mixed in a single API call"; each question evaluates independently in parallel against identical state, and adding questions "barely changes response time" and costs only the tokens of the extra questions — [docs.typesafe.ai Introduction](https://docs.typesafe.ai/introduction); [Primitives](https://docs.typesafe.ai/primitives.md)
- Input is text only (no images, audio, video); English-optimized, other languages "supported but less accurate"; no per-account fine-tuning, domain adaptation is via `state`, `instructions`, `criteria`; not trained on customer requests; zero data retention available for enterprise — [docs.typesafe.ai Models](https://docs.typesafe.ai/models.md)

**Endpoint, auth, response shape (official)**
- `POST https://api.typesafe.ai/v1/systemone`, header `Authorization: Bearer <API_KEY>` — [docs.typesafe.ai API Reference](https://docs.typesafe.ai/api.md)
- Response schema: `model` (string, the versioned model actually used), `answers` keyed by question ID, each with `type`, and then `noul` (0–1) or `choice` (string) or `score` (number), plus `probabilities` (object), `confidence` (0–1), `legend` (object, Score only); `usage: { input_tokens, output_tokens }` — [docs.typesafe.ai API Reference](https://docs.typesafe.ai/api.md)
- Error codes: 401 invalid/missing key; 422 request validation failed; 429 rate limit exceeded; 529 service overloaded; guidance is to "retry the request with exponential backoff" on 429/529 — [docs.typesafe.ai API Reference](https://docs.typesafe.ai/api.md)
- Streaming is not supported by the TypeSafe API (third-party integration doc) — [LiteLLM TypeSafe pass-through docs](https://docs.litellm.ai/docs/pass_through/typesafe)

**Choice (official)**
- Request example: `{"type":"choice","instructions":"Which team should handle this?","criteria":{"billing":"Payment issues","technical":"Integration problems"}}`; response fields: `choice` (selected option key), `probabilities` (distribution across all options), `confidence` (how peaked the distribution is); use when "the answer is one of a known set of options with no order" (routing, classification) — [docs.typesafe.ai Primitives](https://docs.typesafe.ai/primitives.md)
- Max 255 options per Choice question — [docs.typesafe.ai API Reference](https://docs.typesafe.ai/api.md); also "Supports up to 255 options per choice" — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

**Score (official)**
- Request example: `{"type":"score","instructions":"How frustrated does the customer appear?","criteria":["Calm","Concerned","Very angry"]}`; response fields: `score` (position along levels, "may fall between two"), `legend` (numbered levels), `probabilities`, `confidence`; use when answers fall on a spectrum with defined meaning per level (severity, skill level) — [docs.typesafe.ai Primitives](https://docs.typesafe.ai/primitives.md)
- Score rubrics have 2–10 levels; max 10 levels per question — [docs.typesafe.ai API Reference](https://docs.typesafe.ai/api.md); Pydantic AI docs add that 11+ levels "become pick-one questions" — [Pydantic AI TypeSafe docs](https://pydantic.dev/docs/ai/models/typesafe/)

**Noul (official)**
- Request example: `{"type":"noul","instructions":"Does the message request a refund?"}`; response field `noul`: probability (near 1 = yes, near 0 = no, near 0.5 = uncertain); use when "a clean yes/no judgment exists where probability itself provides actionable signal" — [docs.typesafe.ai Primitives](https://docs.typesafe.ai/primitives.md)
- Noul answers do not carry a `confidence` property (only Choice and Score do) — [docs.typesafe.ai Confidence](https://docs.typesafe.ai/confidence.md)

**Official quickstart example (Python SDK, all three primitives in one call)**
- `pip install typesafe-sdk`; env var `TYPESAFE_API_KEY`; `from typesafe_sdk import Choice, Noul, Score, TypeSafeClient`; `client.system_one(state="Hi, I've been trying to connect my Stripe account for 3 days...", questions={"department": Choice(instructions="Which team should handle this", criteria={"billing":"Payment or subscription issues","technical":"Bugs or integration problems","sales":"Pricing or account questions"}), "frustration": Score(instructions="How frustrated the customer appears", criteria=["Calm, just stating facts","Frustrated but civil","Very angry, strong language"]), "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity")})`; printed output `department.choice: "technical"`, `frustration.score: 1.0`, `is_urgent.noul: 1.0`; default model `jev-latest`, response reports `jev-1.13.0` — [docs.typesafe.ai Quick Start](https://docs.typesafe.ai/introduction/quickstart.md)

**Third-party illustrations of full JSON round-trips**
- Cloudflare's listing describes the shape as: input = State object (string or structured data) plus questions object with type, instructions, criteria; output = Answers object containing model version, individual question responses, and token usage; Noul example "Does this convey urgency?", Choice example "Which department should handle this?", Score example "How frustrated is the customer?" (0=Calm, 1=Frustrated, 2=Very angry) — [Cloudflare AI docs: Jev (typesafe)](https://developers.cloudflare.com/ai/models/typesafe/jev/)
- Hugging Face community tutorial (author "sora-2", 2026-09-21) shows a Noul request `{"model":"typesafe/jev-1.13","state":"A customer has tried to connect Stripe for three days.","questions":{"urgent":{"type":"noul","instructions":"Does this message express urgency?"}}}` and response `{"answers":{"urgent":{"noul":0.87}},"usage":{"input_tokens":42,"output_tokens":0},"elapsedMs":214}`. CAUTION: this post points at `POST https://thejevai.com/v1/systemone`, which is not TypeSafe's domain, and its `elapsedMs` field does not appear in the official response schema — [Hugging Face blog (third-party)](https://huggingface.co/blog/sora-2/jev-ai-api-tutorial-build-your-first-structured-de)
- The jevai.org community site shows a pseudocode `client.decide(model="jev-1", state=..., questions={"intent":["refund","bug","billing","other"],"needs_human":bool,"urgency":("score",1,5)})` returning `{"intent":("refund",p=0.94),...}` — this shorthand does not match the official SDK/API shape and should be treated as illustrative only — [jevai.org (community, unofficial)](https://jevai.org)
- Vercel AI SDK form (third-party integration, official Vercel changelog 2026-09-16): `import { experimental_evaluate as evaluate } from 'ai'; await evaluate({ model: 'typesafe-ai/jev', state: '...', questions: { refunded: { type: 'boolean', instructions: 'Was a refund issued?' } } })` — note Vercel calls the Noul type `'boolean'` — [Vercel changelog](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway); [Vercel model page](https://vercel.com/ai-gateway/models/jev)

**SDKs / integrations**
- Official Python SDK: `pip install typesafe-sdk` (Python 3.10+); official JavaScript SDK: `@typesafe-ai/sdk` — [OpenRouter search summary citing TypeSafe docs](https://openrouter.ai/typesafe); [docs.typesafe.ai SDK index](https://docs.typesafe.ai/llms.txt) (lists Python SDK with sync/async clients, retries, exceptions; JavaScript SDK with changelog and API reference)
- Third-party guide: `npm install @typesafe-ai/sdk` (Node 20+); both SDKs read `TYPESAFE_API_KEY` and implement exponential backoff honoring `retry-after` on 429 — [dev.to (Valyu AI, third-party)](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e)
- Pydantic AI integration: `pip install "pydantic-ai-slim[typesafe]"`, model names `typesafe:jev-latest`, `typesafe:jev-preview`, `typesafe:jev-1.13.0`; per-field confidence exposed via `provider_details['confidence']` — [Pydantic AI docs](https://pydantic.dev/docs/ai/models/typesafe/)
- LiteLLM pass-through: base URL `https://api.typesafe.ai`, proxied at `/typesafe/v1/systemone`; models `jev-1.13.0`, `jev-latest`, `jev-preview`; cost tracking uses `usage.input_tokens`/`usage.output_tokens`; logged under the versioned model TypeSafe reports — [LiteLLM docs](https://docs.litellm.ai/docs/pass_through/typesafe)
- TypeSafe docs also list an "Agent Skill" page and a "Coding Agents" page, plus cookbooks (re-ranking, function calling, LLM guardrails, citation checking, hierarchical classification, etc.) — [docs.typesafe.ai index](https://docs.typesafe.ai/llms.txt)

### Inferences
- The "three inputs" framing (State, Model, Questions) maps exactly to the three required top-level request fields `state`, `model`, `questions`.
- Because `output_tokens` is always 0 and output is free, cost is purely a function of state size plus question text, so batching many questions against one state is the intended cost/latency pattern.
- Third-party tutorials on Hugging Face and community sites frequently use unofficial hostnames (thejevai.com, jevai.org) and non-standard shapes; a report should steer readers to `api.typesafe.ai/v1/systemone` and the official SDKs.

### Gaps
- I could not retrieve a verbatim full official response JSON (with actual `probabilities` and `legend` values) from docs.typesafe.ai; the API reference gave the schema and the quickstart gave only the printed scalar values.
- The official docs' `advanced` primitives page (structured `instructions` as object/array) was not fetched, so nested/structured instruction forms are undocumented here.

## Key Question 2: What are the official latency, accuracy, and calibration claims, and what evidence backs them?

### Takeaway
TypeSafe claims 70–500 ms end-to-end latency, "193.6x faster and 444.6x cheaper" than frontier LLMs on its own proprietary workflow evals, and calibrated probabilities from RLCD; the evidence is TypeSafe's internal workflow evaluations against GPT-6 Astra and Fable 5.1, with no public standard benchmark results and no published calibration metric (e.g., ECE) found.

### Cited Findings
- Latency: "End-to-end response time: 70ms-500ms (40x-200x faster than frontier models for equivalent intelligence on System One tasks)"; compared LLMs at 3–329 seconds — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- Workflow evals: "193.6x faster than LLMs (0.114s vs 8.566s on workflow tasks)" and "444.6x cheaper" — [typesafe.ai home](https://typesafe.ai); the blog describes these as "proprietary evaluations using complex production workflows, comparing against GPT-6 Astra and Fable 5.1 as reference models" — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- The blog "does not report results on standard public benchmarks (e.g., MMLU, GSM8K)" — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- Calibration claim: Jev provides "calibrated decisions" where higher confidence correlates with higher accuracy; RLCD optimizes for "epistemically honest probabilities" — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- "Zero hallucinations; every decision includes confidence estimates" — [typesafe.ai home](https://typesafe.ai)
- How confidence is computed: "a statistic computed from the probability distribution the answer already gives you," measuring how concentrated the distribution is; a demo approximation for three options is `(3 × largest probability − 1) / 2`; recommended three-band gating (high = proceed automatically, medium = confirm/human review, low = route to human/fallback), with "different actions within the same system ... gated at different levels depending on the consequences of getting it wrong"; example code uses 0.5 as a floor and >0.9 for high-stakes operations — [docs.typesafe.ai Confidence](https://docs.typesafe.ai/confidence.md)
- Official caveat on calibration consistency: no guarantee that structural invariants hold across formulations; example: for "customer asking for refund," Noul scored 0.22 but the equivalent Choice scored 0.01 (yes) / 0.99 (no); advice is not to transfer thresholds between question types — [docs.typesafe.ai Model Jaggedness (Jev 1.13)](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Third-party latency observations: jevai.org community site claims "~120ms end to end" for a classification request — [jevai.org (unofficial)](https://jevai.org); Hugging Face tutorial example shows `elapsedMs: 214` — [Hugging Face blog (third-party)](https://huggingface.co/blog/sora-2/jev-ai-api-tutorial-build-your-first-structured-de)
- Third-party press summary of architecture: "non-autoregressive" System-1 model (MindStudio headline) — [MindStudio blog (third-party)](https://www.mindstudio.ai/blog/jev-system-one-model-launch); DataCamp headline "Never Hallucinates" repeats TypeSafe's claim — [DataCamp (third-party)](https://www.datacamp.com/blog/system-one-models-jev)
- Adoption (third-party, Vercel-reported per search summary): three days after launch Vercel said Jev was "the fastest-adopted model in AI Gateway history: nearly 13 percent of paid teams in its first 24 hours" — reported via [CellCog blog (third-party)](https://cellcog.ai/blog/jev-typesafe-decision-model/) and [Vercel Developers on X](https://x.com/vercel_dev/status/2100378959653507175) (X post not directly fetched; treat as unverified)

### Inferences
- "Can't hallucinate" is a type-safety claim (the output is always one of the declared options/levels/0–1), not an accuracy claim; wrong-but-well-typed answers are still possible, which is why TypeSafe publishes a "jaggedness" page.
- Latency is likely dominated by input size (32k context cap); the 70 ms floor corresponds to small states.

### Gaps
- No published calibration metric (ECE, reliability diagram) or accuracy numbers per task were found in official sources.
- The exact composition of the "workflow evals" (number of tasks, datasets) is not disclosed; only the aggregate 193.6x / 444.6x figures.
- The MarkTechPost article (2026-09-19) returned empty content on fetch, so any additional benchmark detail it may contain is unverified.

## Key Question 3: What does it cost through each access route, and what are the limits?

### Takeaway
Direct TypeSafe pricing is $0.042 per 1M input tokens with free output; limits are 32k tokens for state + longest question, 64k tokens total per request, 255 Choice options, 10 Score levels, and rate limits of 250,000 tokens/sec and 1,200 requests/min (dynamically adjusted); Vercel AI Gateway listed it at the same $0.042/M with a promotional free period ending 2026-09-25, and OpenRouter and Cloudflare also list it, though OpenRouter per-token pricing could not be retrieved.

### Cited Findings

**Direct TypeSafe API (official)**
- Pricing: "$42 / $0.042" per billion / per million input tokens; output is free — [docs.typesafe.ai Models](https://docs.typesafe.ai/models.md); "$42 per billion input tokens (238x cheaper than Claude Fable 5.1)" — [typesafe.ai home](https://typesafe.ai); blog contrasts LLM inputs at "$0.20-$10/MTok" with outputs ~5x more — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- Rate limits: 250,000 tokens/second; 1,200 requests/minute; "Rate limits are adjusting dynamically" due to high demand and may change without notice — [docs.typesafe.ai Models](https://docs.typesafe.ai/models.md)
- Context: 64k total per request; 32k for state + longest question — [docs.typesafe.ai Models](https://docs.typesafe.ai/models.md); corroborated by [Pydantic AI docs](https://pydantic.dev/docs/ai/models/typesafe/)
- Structural limits: max 255 Choice options; Score rubrics 2–10 levels — [docs.typesafe.ai API Reference](https://docs.typesafe.ai/api.md)
- Access: early access "now available," developers "being brought off the waitlist"; console at https://console.typesafe.ai/ — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev); API keys at console.typesafe.ai/settings/keys (third-party) — [dev.to](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e)
- Launch press release: Jev "is available through early access waitlisted at typesafe.ai" and "demand was so hot at launch the company briefly lost the ability to serve its API" — [Business Wire via Morningstar, 2026-09-15](https://www.morningstar.com/news/business-wire/20260915525333/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai)
- Third-party per-case estimate: "~$0.0004 on benchmark workflows"; cascade example reduced cost "from ~$30,400 to ~$6,480 on a million-ticket workload" — [dev.to (third-party)](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e)

**Vercel AI Gateway (third-party route; Vercel is the primary source for its own terms)**
- Announced 2026-09-16; model ID `typesafe-ai/jev`; requires AI SDK 7.0.105+ and the `experimental_evaluate` API — [Vercel changelog](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway)
- Model page: $0.042/1M input tokens; 32,000-token context; max output tokens 0; provider "TypeSafe AI (available via DigitalOcean)"; features listed: classification, routing decisions, rubric-based assessment, automated verification, parallel multi-question evaluation — [Vercel model page](https://vercel.com/ai-gateway/models/jev)
- Free tier: "Jev (typesafe-ai/jev) System One evaluation model — free pricing, 32K context" with "promotional pricing ends on September 25, 2026" (issue opened 2026-09-21) — [freetokens GitHub issue #445 (third-party tracker)](https://github.com/luongnv89/freetokens/issues/445); search summary of Vercel's X post: "free on Vercel AI Gateway until Sept 25" and "your Vercel team must have a card on file or requests fail with customer_verification_required" — [Vercel Developers on X](https://x.com/vercel_dev/status/2101116818463281579) (not directly fetched). As of 2026-09-29 this free period has ended.
- Vercel also lists it as available via DigitalOcean, implying at least one hosting partner beyond TypeSafe's own infrastructure — [Vercel model page](https://vercel.com/ai-gateway/models/jev)

**OpenRouter (third-party route)**
- OpenRouter's TypeSafe author page lists three models, "Jev Router, Jev Latest, and Jev 1.13," with IDs `typesafe/jev-1.13`, `typesafe/jev-router`, `typesafe/jev-latest`, "served through the same OpenRouter API and API key" — [OpenRouter /typesafe](https://openrouter.ai/typesafe)
- Search summary of OpenRouter's description: "Jev returns typed decisions (a choice, a score, or a yes/no probability) instead of text, so it is called through its own evaluate endpoint rather than /chat/completions" — [OpenRouter /typesafe](https://openrouter.ai/typesafe)

**Cloudflare Workers AI (third-party route)**
- Cloudflare AI docs list `typesafe/jev`: input $0.042 per 1M tokens, output $0.00, cached input $0.00; 32,000-token context; zero data retention: yes; provider: third-party (TypeSafe); schemas downloadable as JSON; use cases: support routing/triage, refund eligibility, account risk, policy compliance — [Cloudflare AI docs](https://developers.cloudflare.com/ai/models/typesafe/jev/)

**Community "free" routes (unofficial)**
- jevai.org advertised a "free-play blitz" playground through Sept 25 (no credits required) and API key generation at `/agent/keys`; this is a community site, not TypeSafe — [jevai.org](https://jevai.org)

### Inferences
- All three listed gateways (Vercel, Cloudflare, and by press reports OpenRouter) mirror TypeSafe's $0.042/M input, $0 output pricing and 32k context, so as of late September 2026 there is no price arbitrage between routes; the choice is about billing consolidation, SDK ergonomics, and the (now-expired) Vercel promo.
- The "jev-router" model on OpenRouter and "jev-preview" alias in TypeSafe docs suggest TypeSafe is preparing multiple model tiers, but no official description of jev-router was found.

### Gaps
- OpenRouter per-token pricing, context length, and date-added for `typesafe/jev-1.13` could not be retrieved (model page returned 404; the public `/api/v1/models` JSON returned to me did not include typesafe entries, possibly due to truncation or because the evaluate-style model is excluded from the chat models list).
- No official statement of what happened to Vercel free-tier users after 2026-09-25 beyond reverting to $0.042/M.
- No official per-plan/enterprise pricing tiers or volume discounts were found.
- The Vercel card-on-file requirement is from a search snippet of an X post I could not fetch directly.

## Key Question 4: What does TypeSafe say Jev is NOT good for?

### Takeaway
TypeSafe publishes an explicit "Model Jaggedness (Jev 1.13)" page listing 11 weaknesses: literal reading of negations/scoping, arithmetic and counting, numeric representations, score interpolation, date/time comparison, indirection/multi-hop, large irrelevant context, adversarial content, contradictory instructions, lack of structural invariants across question types, and text generation.

### Cited Findings (all official unless noted)
- Literal reading: "Scoping words, negations, and implied conditions are read at face value"; mitigation: state exact conditions, include boundary cases in criteria, split ambiguous questions — [Model Jaggedness (Jev 1.13)](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Math and counting: "Jev is not a calculator"; counting errors grow with list size; mitigation: do math in code, ask one question per item and sum in code — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Numeric representations: poor on hex values, RGB triples, precise numeric comparisons; convert to named buckets first — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Score interpolation: cannot reliably reconstruct exact numbers between levels; use scores for thresholds only — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Dates/times: read as text, not ordered quantities; keep ordering/duration/offset in code — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Indirection: double negatives and multi-hop reasoning reduce accuracy — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Large irrelevant context: "Unrelated detail acts as a distractor"; filter state in code first — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Adversarial content: doesn't treat state as hostile; susceptible to prompt injection and misleading framing — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Contradictory instructions vs criteria cause confusion — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Structural invariants: no guarantee identities like P(noul)+P(not_noul)=1 hold across formulations (0.22 vs 0.01/0.99 example) — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Text generation: "Not trained for text generation; slow and ineffective when forced"; use Choice over bounded options or a generative model for extraction — [same](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md)
- Blog-level framing: Jev sacrifices string generation; "Not optimized for: chat, general text generation, or human-in-the-loop tasks requiring flexibility" — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- Modality/language: text only; English-optimized — [docs.typesafe.ai Models](https://docs.typesafe.ai/models.md)
- Third-party summary consistent with official page: unsuitable for "arithmetic/counting, literal reading of negations, indirect multi-hop questions, generating text, handling adversarial inputs, and enforcing structural invariants across related fields" — [Pydantic AI docs](https://pydantic.dev/docs/ai/models/typesafe/); "Avoid asking the model something code can compute exactly. Avoid hiding several judgments inside one question"; not for decisions "requiring written rationale for audits" — [dev.to (third-party)](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e)
- Recommended architecture (official pattern names): Speculative Fan-out, Confidence-Gated Routing, Composite Scoring, Intent Routing; cookbooks include "SDE Cascade," "LLM Guardrails," "Re-ranking" — [docs.typesafe.ai index](https://docs.typesafe.ai/llms.txt); third-party "cascade" description: route cheaply with Jev, do lookups in code, escalate complex cases to frontier LLMs — [dev.to](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e)

### Inferences
- The jaggedness list amounts to: Jev is a semantic judge, not a computer; anything deterministic (math, dates, counting, comparisons) should be pre-computed in code and only the judgment delegated.
- The "no written rationale" point is a real audit limitation: responses contain probabilities but no explanation, so explainability must come from question design.

### Gaps
- No official quantified accuracy degradation numbers for any of the weaknesses (e.g., how much accuracy drops with N distractor tokens).

## Key Question 5: Release timeline and version history

### Takeaway
TypeSafe AI emerged from stealth on 2026-09-15 with a $40M DCVC-led seed and released Jev in waitlisted early access the same day; the only publicly documented model version is `jev-1.13.0` (aliases `jev-latest` and `jev-preview` both point to it as of late September 2026), with Vercel (09-16), OpenRouter, and Cloudflare listings following within days.

### Cited Findings
- 2026-09-15: "TypeSafe AI Emerges From Stealth With $40M in Funding With New Model for Composable AI" (Business Wire, dated 20260915); seed led by DCVC; founders Diogo Almeida (former OpenAI researcher, co-inventor of RLHF/ChatGPT), Erik Gafni, Sasha Sheng; Jev in early access via waitlist — [Morningstar/Business Wire](https://www.morningstar.com/news/business-wire/20260915525333/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai); [Wilson Sonsini](https://www.wsgr.com/en/insights/wilson-sonsini-advises-typesafe-ai-on-dollar40-million-seed-round-as-company-emerges-from-stealth.html); [AIwire 2026-09-16](https://www.hpcwire.com/aiwire/2026/09/16/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai/)
- Official blog "Introducing System One Models & Jev": the fetched page displayed a timestamp of 2026-09-28 19:32 UTC, which conflicts with the 09-15 launch date reported by press; likely a last-updated stamp — [TypeSafe blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev). The typesafe.ai home page footer showed "Version 0.01 as of September 28, 2026" (site/page version, not model version) — [typesafe.ai](https://typesafe.ai)
- 2026-09-16: Vercel AI Gateway availability — [Vercel changelog](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway)
- 2026-09-19: MarkTechPost coverage "TypeSafe AI Releases Jev" — [MarkTechPost](https://www.marktechpost.com/2026/09/19/typesafe-ai-releases-jev/) (content not retrievable on fetch)
- 2026-09-21: Hugging Face community tutorial published — [Hugging Face blog](https://huggingface.co/blog/sora-2/jev-ai-api-tutorial-build-your-first-structured-de)
- 2026-09-25: Vercel promotional free pricing ended — [freetokens issue #445](https://github.com/luongnv89/freetokens/issues/445)
- Versions: current model `jev-1.13.0`; `jev-latest` → `jev-1.13.0` (stable); `jev-preview` → `jev-1.13.0` (currently same); "an alias moves when a new release ships"; no prior versions documented — [docs.typesafe.ai Models](https://docs.typesafe.ai/models.md)
- OpenRouter additionally lists `typesafe/jev-router` — [OpenRouter](https://openrouter.ai/typesafe)
- Third-party advice: pin versions because "updates change answers" — [dev.to](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e) (note: this article's page metadata shows "September 17, 2024," an apparent typo for 2026 given it discusses the 2026-09-15 launch)

### Inferences
- "1.13" appears to be an internal version counter at first public release rather than the 13th public release; there is no public changelog of earlier Jev versions.
- The term "System One" is a reference to Kahneman's fast/intuitive System 1 (third-party sources say so explicitly; the official blog uses the term without attribution in the content I retrieved).

### Gaps
- No official model changelog or deprecation policy with dates was found.
- No official description of `jev-router` (what it routes between) was found.
- The exact date the official blog post was first published could not be confirmed from the page itself.
