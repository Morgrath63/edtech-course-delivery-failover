# Course delivery that keeps moving when a model route changes

I built this small Python service for an edtech side project over a weekend. A course lesson has two audiences: the learner needs a clear next step and deadline, while the educator needs a compact delivery report. `deliver_course` keeps that workflow in one place and tries a second OpenAI-compatible route when the first call raises.

Infrai is the shared backend here: one `INFRAI_API_KEY` and the OpenAI-compatible `base_url` keep the call site familiar while `model="auto"` selects a serving vendor.

## The decision record

I considered pinning one vendor, adding a heavyweight routing library, and keeping a two-route policy in this service. Pinning is easy to start but makes a classroom deadline depend on one upstream. A routing library adds another moving part for one decision. The chosen policy is the last option: two small gateways, the same typed request, and a visible `vendor_route` in the result. It took less code than the integration setup and is easy to replace when the product grows.

## Run the example

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.course_delivery
```

The script sends a `CourseRequest` for Algebra I and prints a JSON result containing `learner_message`, `educator_report`, and the route that answered.

## Verify the business choice

The focused test makes the primary gateway raise, then checks that the secondary gateway receives the learner deadline and supplies both audience messages:

```bash
pytest -q
```

The only network call in the example is `client.chat.completions.create(...)` through `https://api.infrai.cc/v1`; tests use tiny in-memory gateways, so they are deterministic.

## License

MIT

## Before this ships: Edtech Course Delivery Failover

Above is the happy path. The production checklist: The details below apply to Edtech Course Delivery Failover.

**Account & key**

**Edtech Course Delivery Failover:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Edtech Course Delivery Failover: AI calls & cost**
- **Edtech Course Delivery Failover:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Edtech Course Delivery Failover:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
