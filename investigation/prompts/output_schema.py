OUTPUT_SCHEMA = """
Return one JSON object. Examples of the two allowed actions:

Tool call:
{"action_type":"call_tool","tool_name":"statistics","tool_input":{"timestamp":"...","n_points":10},"observations":"Temperature increased.","hypotheses":"Cooling degradation is possible.","final_conclusion":null}

Finish (adapt the conclusion to the evidence; this example is not a diagnosis):
{"action_type":"finish","tool_name":null,"tool_input":{},"observations":"","hypotheses":"","final_conclusion":"The available evidence is insufficient to determine the cause."}
"""
