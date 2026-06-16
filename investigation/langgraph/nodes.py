from investigation.agents.llm_agent import LLMAgent
from investigation.models.context import Context
from investigation.models.tool_call import ToolCall
from investigation.tools.tool_registry import ToolRegistry


agent = None
registry = None


def initialize_nodes(llm_agent: LLMAgent, tool_registry: ToolRegistry):

    global agent
    global registry

    agent = llm_agent
    registry = tool_registry


def llm_node(state: Context) -> Context:

    action = agent.decide(state)
    state.current_action = action
    return state


def tool_node(state: Context) -> Context:

    action = state.current_action

    tool = registry.get(action.tool_name)

    tool_output = tool.run(**action.tool_input)

    state.tool_calls.append(
        ToolCall(
            tool_name=action.tool_name,
            tool_input=action.tool_input,
            tool_output=tool_output
        )
    )

    state.working_memory[action.tool_name] = tool_output

    state.observations.append(action.observations)

    state.hypotheses.append(action.hypotheses)

    return state