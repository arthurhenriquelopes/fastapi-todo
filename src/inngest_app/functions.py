import os
import inngest
from src.inngest_app.client import inngest_client

@inngest_client.create_function(
    fn_id="ai-decision-flow",
    trigger=inngest.TriggerEvent(event="ai/flow.run"),
)
async def ai_flow_execution(ctx: inngest.Context, step: inngest.Step):
    event_data = ctx.event.data
    graph_nodes = event_data.get("nodes", {})
    start_node_id = event_data.get("start_node_id")
    
    current_node_id = start_node_id
    history = []
    
    # Loop over nodes dynamically
    while current_node_id and current_node_id in graph_nodes:
        node = graph_nodes[current_node_id]
        prompt = node.get("prompt", "")
        
        step_id = f"execute-node-{current_node_id}-{len(history)}"
        
        def run_llm():
            from src.llm.client import llm_client
            res = llm_client.chat.completions.create(
                model=os.environ.get("LLM_MODEL", "openrouter/free"),
                messages=[
                    {"role": "system", "content": "You are a decision AI. You must respond with EXACTLY 'YES' or 'NO' and nothing else."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return res.choices[0].message.content.strip().upper()
            
        # Inngest step executes the LLM call safely
        result = await step.run(step_id, run_llm)
        
        history.append({
            "node_id": current_node_id,
            "prompt": prompt,
            "result": result
        })
        
        # Branching logic
        if result == "YES":
            current_node_id = node.get("yes_path")
        elif result == "NO":
            current_node_id = node.get("no_path")
        else:
            # Fallback for unexpected model output
            current_node_id = None
            
    return {"status": "completed", "history": history}
