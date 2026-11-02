from investigation.models.context import Context
from investigation.runtime import InvestigationRuntime


def llm_node(state: Context, investigation_runtime: InvestigationRuntime) -> Context:
    return investigation_runtime.decide(state)


def tool_node(state: Context, investigation_runtime: InvestigationRuntime) -> Context:
    return investigation_runtime.execute_tool(state)


def finalize_node(state: Context, investigation_runtime: InvestigationRuntime) -> Context:
    return investigation_runtime.finalize(state)
