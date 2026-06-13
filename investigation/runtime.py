from investigation.models.tool_call import ToolCall
from investigation.models.results import InvestigationResult


class InvestigationRuntime:

    def __init__(self, agent, registry, max_iterations=10):
        self.agent = agent
        self.registry = registry
        self.max_iterations = max_iterations

    def run(self, context):

        for _ in range(self.max_iterations):

            action = self.agent.decide(context)

            context.observations.extend(action.observations)

            context.hypotheses.extend(action.hypotheses)

            if action.action_type == "finish":

                context.final_conclusion = action.final_conclusion

                return InvestigationResult(
                    request=context.request,
                    tool_calls=context.tool_calls,
                    observations=context.observations,
                    hypotheses=context.hypotheses,
                    final_conclusion=context.final_conclusion
                )

            if action.action_type == "call_tool":

                tool = self.registry.get(action.tool_name)

                tool_output = tool.run(**action.tool_input)

                context.tool_calls.append(
                    ToolCall(
                        tool_name=action.tool_name,
                        tool_input=action.tool_input,
                        tool_output=tool_output
                    )
                )

                context.working_memory[action.tool_name] = tool_output

                continue

            raise ValueError(f"Unknown action type: {action.action_type}")

        raise RuntimeError(f"Maximum number of iterations ({self.max_iterations}) reached.")