from src.course_delivery import CourseRequest, deliver_course


class BrokenGateway:
    label = "primary"

    def complete(self, prompt: str) -> str:
        raise RuntimeError("transport unavailable")


class WorkingGateway:
    label = "secondary"

    def complete(self, prompt: str) -> str:
        assert "Friday 17:00" in prompt
        return "LEARNER: Complete the practice by Friday 17:00. EDUCATOR: Lesson queued."


def test_deadline_workflow_fails_over_to_next_gateway():
    request = CourseRequest(
        course_title="Algebra I",
        lesson="Linear equations",
        learner_deadline="Friday 17:00",
        educator_name="Mina",
    )
    result = deliver_course(request, [BrokenGateway(), WorkingGateway()])
    assert result.vendor_route == "secondary"
    assert result.learner_message == "Complete the practice by Friday 17:00."
    assert result.educator_report == "Lesson queued."
