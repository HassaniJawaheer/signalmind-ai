from inspect import signature
from math import isfinite
from time import monotonic

from investigation.errors import InvestigationError
from investigation.models.agent_action import AgentAction
from investigation.models.tool_call import ToolCall
from investigation.models.results import InvestigationResult
from investigation.models.context import Context


class InvestigationRuntime:

    def __init__(self, agent, registry, max_iterations=10, max_duration_seconds=120.0):
        if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or max_iterations <= 0:
            raise ValueError("max_iterations must be a positive integer.")
        if not isfinite(max_duration_seconds) or max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be finite and positive.")
        self.agent = agent
        self.registry = registry
        self.max_iterations = max_iterations
        self.max_duration_seconds = max_duration_seconds
        self.started_at = None

    def prepare(self, context: Context) -> None:
        if context.status != "running" or context.current_action is not None:
            raise ValueError("An investigation requires a fresh running context.")
        self.started_at = monotonic()

    def check_duration(self, context: Context) -> bool:
        # Cooperative budget: running calls are not interrupted here.
        # Network waits are bounded separately by GroqClient HTTP timeouts.
        if monotonic() - self.started_at >= self.max_duration_seconds:
            context.status = "incomplete"
            context.stop_reason = "duration_limit"
            context.error_message = "The investigation duration limit was reached."
            return False
        return True

    def fail(self, context: Context, reason: str, message: str) -> Context:
        context.status = "failed"
        context.stop_reason = reason
        context.error_message = message
        return context

    def decide(self, context: Context) -> Context:
        if not self.check_duration(context):
            return context
        if context.iterations >= self.max_iterations:
            context.status = "incomplete"
            context.stop_reason = "iteration_limit"
            context.error_message = "The maximum number of agent decisions was reached."
            return context

        context.iterations += 1
        try:
            action = self.agent.decide(context)
            if not isinstance(action, AgentAction):
                raise InvestigationError("invalid_action", "The agent did not return an AgentAction.")
            action.validate()
        except InvestigationError as error:
            return self.fail(context, error.reason, error.message)
        except Exception:
            return self.fail(context, "agent_error", "An unexpected error occurred while obtaining the agent decision.")

        context.current_action = action
        if action.observations:
            context.observations.append(action.observations)
            context.observation_turns.append(context.iterations)
        if action.hypotheses:
            context.hypotheses.append(action.hypotheses)
            context.hypothesis_turns.append(context.iterations)
        self.check_duration(context)
        return context

    def execute_tool(self, context: Context) -> Context:
        if not self.check_duration(context):
            return context
        action = context.current_action
        try:
            tool = self.registry.get(action.tool_name)
            signature(tool.run).bind(**action.tool_input)
        except (TypeError, ValueError):
            return self.fail(context, "invalid_tool_call", "The requested tool or its parameters are invalid.")

        try:
            output = tool.run(**action.tool_input)
        except Exception:
            return self.fail(context, "tool_error", "The requested analysis tool failed.")

        context.tool_calls.append(ToolCall(
            tool_name=action.tool_name,
            tool_input=action.tool_input,
            tool_output=output,
            turn=context.iterations,
        ))
        context.working_memory[action.tool_name] = output
        self.check_duration(context)
        return context

    def finalize(self, context: Context) -> Context:
        if context.status == "running":
            action = context.current_action
            if action is None or action.action_type != "finish":
                self.fail(context, "invalid_action", "The investigation ended without a finish action.")
            else:
                context.final_conclusion = action.final_conclusion
                context.status = "completed"
                context.stop_reason = "agent_finished"
                context.error_message = None
        if context.status != "completed":
            context.final_conclusion = None
        return context

    @staticmethod
    def result(context: Context) -> InvestigationResult:
        return InvestigationResult(
            request=context.request,
            tool_calls=list(context.tool_calls),
            observations=list(context.observations),
            hypotheses=list(context.hypotheses),
            final_conclusion=context.final_conclusion,
            status=context.status,
            stop_reason=context.stop_reason,
            error_message=context.error_message,
        )

    def run(self, context: Context) -> InvestigationResult:
        self.prepare(context)
        while context.status == "running":
            self.decide(context)
            if context.status != "running" or context.current_action.action_type == "finish":
                break
            self.execute_tool(context)
        self.finalize(context)
        return self.result(context)
