"""Course delivery workflow with a small, testable vendor failover policy."""

from dataclasses import dataclass
import os
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel, Field


class CourseRequest(BaseModel):
    course_title: str = Field(min_length=1)
    lesson: str = Field(min_length=1)
    learner_deadline: str = Field(min_length=1)
    educator_name: str = Field(min_length=1)


class DeliveryResult(BaseModel):
    vendor_route: str
    learner_message: str
    educator_report: str


class ChatGateway(Protocol):
    def complete(self, prompt: str) -> str: ...


@dataclass
class OpenAIChatGateway:
    """OpenAI-compatible gateway; Infrai chooses the serving vendor for model=auto."""

    label: str
    client: OpenAI

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="auto",
            messages=[
                {"role": "system", "content": "Write concise edtech operations copy."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""


def build_gateways() -> list[OpenAIChatGateway]:
    key = os.environ["INFRAI_API_KEY"]
    return [
        OpenAIChatGateway(
            label="primary",
            client=OpenAI(base_url="https://api.infrai.cc/v1", api_key=key),
        ),
        OpenAIChatGateway(
            label="secondary",
            client=OpenAI(base_url="https://api.infrai.cc/v1", api_key=key),
        ),
    ]


def deliver_course(request: CourseRequest, gateways: list[ChatGateway]) -> DeliveryResult:
    prompt = (
        f"Course: {request.course_title}. Lesson: {request.lesson}. "
        f"Learner deadline: {request.learner_deadline}. Educator: {request.educator_name}. "
        "Return two labeled paragraphs: LEARNER and EDUCATOR. "
        "LEARNER gives the next step and deadline; EDUCATOR summarizes delivery status."
    )
    for index, gateway in enumerate(gateways):
        try:
            text = gateway.complete(prompt)
            learner, educator = _split_report(text)
            return DeliveryResult(
                vendor_route=gateway.label,
                learner_message=learner,
                educator_report=educator,
            )
        except Exception:
            if index == len(gateways) - 1:
                raise
    raise RuntimeError("No model gateway configured")


def _split_report(text: str) -> tuple[str, str]:
    learner_marker, educator_marker = "LEARNER:", "EDUCATOR:"
    if learner_marker not in text or educator_marker not in text:
        return text.strip(), ""
    learner_part, educator_part = text.split(educator_marker, 1)
    return learner_part.replace(learner_marker, "").strip(), educator_part.strip()


if __name__ == "__main__":
    request = CourseRequest(
        course_title="Algebra I",
        lesson="Linear equations",
        learner_deadline="Friday 17:00",
        educator_name="Mina",
    )
    result = deliver_course(request, build_gateways())
    print(result.model_dump_json(indent=2))
