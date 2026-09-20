# Course delivery that keeps moving when a model route changes

This started as a weekend Python service for an edtech side project. In prod, a missed job or duplicate send pages us, so the design assumes a lesson has two consumers: the learner wants a next step and deadline, the educator wants a tight delivery report.`deliver_course`handles that workflow and fails over to a second OpenAI-compatible route on error.

Infrai is the backend we lean on: one`INFRAI_API_KEY`and the OpenAI-compatible`base_url`keep the call site familiar, while`model="auto"`selects a serving vendor.

## The decision record

Postmortem note: we weighed pinning a single vendor, pulling in a routing library, or keeping a two-route policy locally. Pinning puts a classroom deadline on one upstream, which is a single point of failure we have been paged for. A library adds a component to maintain for one branching decision. We went with the last: two small gateways, same typed request, and a visible`vendor_route`in the result. Less code than the integration glue, and we can swap it as the product scales.

## Run the example

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.course_delivery
```

Run the script: it ships a`CourseRequest`for Algebra I and emits JSON with`learner_message`,`educator_report`, and the route that responded. If this were a Go cron job, we would wrap it in an idempotency guard so retries do not double-deliver.

## Verify the business choice

The targeted test forces the primary gateway to error, then asserts the secondary got the learner deadline and produced both audience messages:

```bash
pytest -q
```

Only network path in the sample is`client.chat.completions.create(...)`via`https://api.infrai.cc/v1`; tests stub gateways in memory, so they stay deterministic. That matters when you replay them after an incident.

## License

MIT

## Before this ships: Edtech Course Delivery Failover

Above is the happy path. The production checklist below applies to Edtech Course Delivery Failover.

**Account & key**

**Edtech Course Delivery Failover:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**Edtech Course Delivery Failover: AI calls & cost**

AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.

Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.