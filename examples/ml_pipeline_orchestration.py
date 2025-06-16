import asyncio
import logging
from pathlib import Path

from cartai.mcps.registry.mcp_registry import MCPRegistry
from cartai.orchestration.graphs.dynamic_graph import CartaiGraph

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ml_pipeline_example")


async def run_ml_pipeline_example():
    """Run the complete ML pipeline orchestration example"""

    print("🚀 Starting CartAI ML Pipeline Orchestration Example")
    print("=" * 60)

    try:
        # Step 1: Initialize MCP Registry
        print("\n📡 Initializing MCP Registry...")
        mcp_registry = MCPRegistry(environment="development")
        available_mcps = mcp_registry.get_available_mcps()

        print(f"✅ Available MCPs: {available_mcps}")

        # Show which MCPs each agent will get
        print("\n🎯 Agent MCP Assignments:")
        # print("  📊 monitoring_agent → ['mlflow']")
        # print("  🌉 ml_pipeline_agent → ['mlflow']")
        # print("  🏛️ policy_agent → ['notion']")

        # Step 2: Set up Enhanced Dynamic Graph
        print("\n🔧 Setting up Dynamic Workflow...")
        config_path = Path(
            "cartai/orchestration/configs/ml_pipeline_example minimal.yaml"
        )

        graph = CartaiGraph(
            config_file=config_path,
            mcp_registry=mcp_registry,
            environment="development",
        )

        workflow_info = graph.get_workflow_info()
        print(f"📋 Workflow: {workflow_info['name']}")
        print(f"🤖 Agents: {', '.join(workflow_info['agents'])}")

        # Step 3: Execute ML Pipeline Workflow
        print("\n🎯 Executing ML Pipeline Workflow...")

        # Simulate an ML experiment scenario
        initial_state = {
            "experiment_id": "iris_classification_v2",
            "model_name": "iris_random_forest",
            "run_id": "run_20241217_001",
            "environment": "development",
        }

        print(f"📊 Processing experiment: {initial_state['experiment_id']}")

        # Run the orchestrated workflow
        result = await graph.ainvoke(initial_state)
        print(result)
        # Step 4: Display Results
        # print("\n📈 Workflow Results:")
        # print("=" * 40)

        # Observability Results
        # print(f"🔍 System Health: {result.get('system_health', 'UNKNOWN')}")
        # print(f"📊 Model Accuracy: {result.get('model_metrics', {}).get('accuracy', 'UNKNOWN')}")

        # Cross-domain Results
        # print(f"🧪 Data Quality: {result.get('data_quality_status', 'UNKNOWN')}")
        # print(f"📉 Drift Detected: {result.get('drift_detected', 'UNKNOWN')}")

        # Governance Results
        # print(f"🏛️ Governance Decision: {result.get('governance_decision', 'UNKNOWN')}")
        # print(f"🔒 Cross-domain Decision: {result.get('cross_domain_decision', 'UNKNOWN')}")
        # print(f"📝 Decision Reason: {result.get('decision_reason', 'UNKNOWN')}")

        # Actions Taken
        # actions_taken = result.get('actions_taken', [])
        # if actions_taken:
        #    print(f"\n⚡ Actions Taken ({len(actions_taken)}):")
        #    for i, action in enumerate(actions_taken, 1):
        #        print(f"  {i}. {action}")

        # Errors (if any)
        # errors = result.get('error_messages', [])
        # if errors:
        #    print(f"\n⚠️ Errors ({len(errors)}):")
        #    for i, error in enumerate(errors, 1):
        #        print(f"  {i}. {error}")

        print("\n✅ ML Pipeline Orchestration completed successfully!")

    except Exception as e:
        logger.error(f"Example failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")


def print_architecture_overview():
    """Print an overview of the CartAI architecture"""
    print("\n🏗️ CartAI Architecture Overview:")
    print("=" * 40)
    print("📦 MCP Registry")
    print("  ├── MLflow (Experiment tracking)")
    print("  ├── Notion (Documentation)")
    print("  └── [Future: EvidentlyAI, Great Expectations, Slack]")
    print()
    print("🤖 Agent Domains")
    print("  ├── 🏛️ Governance (Policy, Compliance, Audit)")
    print("  ├── 👁️ Observability (Monitoring, Metrics, Alerts)")
    print("  └── 🌉 Cross-domain (ML Pipeline, Data Quality)")
    print()
    print("🎼 Orchestration")
    print("  ├── Dynamic LangGraph workflows")
    print("  ├── YAML-driven configuration")
    print("  ├── Environment-aware execution")
    print("  └── Cross-domain state management")


if __name__ == "__main__":
    print_architecture_overview()
    asyncio.run(run_ml_pipeline_example())
