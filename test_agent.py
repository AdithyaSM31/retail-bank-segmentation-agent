import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.orchestrator import create_agent, run_agent_query

def run_test():
    print("Initializing agent...")
    agent = create_agent()
    
    query = "Segment customers into priority, regular and dormant based on balance being maintained and frequency of transactions. Then plot the segment distribution."
    print(f"Running query: {query}")
    
    try:
        result = run_agent_query(agent, query)
        print("\n--- Agent Response ---")
        print(result["response"])
        print("\n--- Charts Generated ---")
        print(f"Count: {len(result.get('charts', []))}")
        print("Test completed successfully.")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    run_test()
