from functools import partial
from langgraph.graph import StateGraph, START, END

from investigation.models.context import Context
from investigation.models.results import InvestigationResult
from investigation.runtime import InvestigationRuntime
from investigation.langgraph.nodes import llm_node, tool_node, finalize_node
from investigation.langgraph.edges import should_continue, after_tool


def build_graph(runtime: InvestigationRuntime):
    workflow = StateGraph(Context)
    workflow.add_node("llm", partial(llm_node, investigation_runtime=runtime))
    workflow.add_node("tool", partial(tool_node, investigation_runtime=runtime))
    workflow.add_node("finalize", partial(finalize_node, investigation_runtime=runtime))
    workflow.add_edge(START, "llm")
    workflow.add_conditional_edges("llm", should_continue, {
        "tool": "tool",
        "finalize": "finalize",
    })
    workflow.add_conditional_edges("tool", after_tool, {
        "llm": "llm",
        "finalize": "finalize",
    })
    workflow.add_edge("finalize", END)
    return workflow.compile()


def run_investigation(context: Context, agent, registry, max_iterations=10,
                      max_duration_seconds=120.0) -> InvestigationResult:
    runtime = InvestigationRuntime(agent, registry, max_iterations, max_duration_seconds)
    runtime.prepare(context)
    graph = build_graph(runtime)
    # Leave room for the budget check and finalization after the last tool call.
    state = graph.invoke(context, config={"recursion_limit": 2 * max_iterations + 4})
    return runtime.result(Context(**state))
