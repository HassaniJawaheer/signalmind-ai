from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.graph import END
from investigation.models.context import Context
from investigation.langgraph.nodes import llm_node, tool_node
from investigation.langgraph.edges import should_continue


workflow = StateGraph(Context)

workflow.add_node("llm", llm_node)

workflow.add_node("tool", tool_node)

workflow.add_edge(START, "llm")

workflow.add_conditional_edges(
"llm",
    should_continue,
    {
        "tool": "tool",
        "end": END
    }
)

workflow.add_edge("tool", "llm")

graph = workflow.compile()