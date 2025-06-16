# 🌟 Cartai 🌟

## 📝 Description
Cartai is a command-line interface (CLI) tool designed to assist in various tasks such as project summary generation and code parsing. It leverages advanced LLM (Language Model) capabilities to enhance your development workflow by automating repetitive tasks, improving documentation, and providing insights into code changes.

## 📂 Codebase Structure
```
cartai/
├── adapters/
├── cli/
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── pr_diff.py
│   │   └── readme.py
│   └── main.py
├── core/
│   ├── __init__.py
│   └── code_parser.py
├── lineage/
├── llm_agents/
│   ├── __init__.py
│   ├── documenter.py
│   ├── graph.py
│   ├── graph_states.py
│   ├── templates/
│   │   ├── pr_diff.jinja
│   │   ├── project_uml.jinja
│   │   └── readme.jinja
│   └── utils/
│       ├── __init__.py
│       ├── model_client_utils.py
│       └── yaml_utils.py
```

## ⚙️ Installation

To install the necessary dependencies for the project, you can use the provided Makefile. Simply run the following command in your terminal:

```bash
make install
```

This command will set up all required packages and dependencies.

💻 Usage

Once the installation is complete, you can start using Cartai. The main CLI entry point is `main.py`, and you can execute various commands such as generating pull request diffs or creating project readme files.

To run the application, you can use the following command:

```bash
make run
```

This will execute the main application, and you can start using the available commands.

🚀 Deployment

For deployment purposes, ensure that all environment variables and configurations are set as needed. You can refer to the documentation or the Makefile for any specific deployment instructions.

We welcome contributions!

Fork the repository 🍴

Create your feature branch:
```bash
git checkout -b feature/YourFeature
```

Commit your changes:
```bash
git commit -m 'Add YourFeature'
```

Push to the branch:
```bash
git push origin feature/YourFeature
```

Open a pull request 📬

Please follow the coding guidelines and check the Makefile or contributing docs if available.

# CartAI Examples - Incremental Implementation

This directory contains examples demonstrating CartAI's agile, incremental approach to building an AI governance and observability platform.

## 🎯 What We've Built (Incrementally)

### Phase 1: Foundation Layer ✅
- **MCP Registry**: Central management for all MCP integrations
- **Environment-aware configuration**: Different setups for dev/staging/prod
- **Error handling and health checking**

### Phase 2: Agent Architecture ✅
- **Base MCP-Aware Agent**: Foundation for all agents
- **Governance Agent**: Policy enforcement and compliance
- **Observability Agent**: Monitoring and metrics collection
- **Cross-Domain Agent**: Bridges governance and observability

### Phase 3: Dynamic Orchestration ✅
- **Enhanced LangGraph Integration**: Dynamic workflow building
- **YAML-driven configuration**: Easy workflow customization
- **Cross-domain state management**: Unified state across agent types

## 🚀 Running the Example

```bash
# Set environment variables (optional)
export MLFLOW_TRACKING_URI=http://localhost:5000
export NOTION_TOKEN=your_notion_token

# Run the ML pipeline orchestration example
python examples/ml_pipeline_orchestration.py
```

## 🏗️ Architecture Overview

```
CartAI Platform
├── 📦 MCP Registry (Foundation)
│   ├── MLflow integration
│   ├── Notion integration
│   └── Health monitoring
├── 🤖 Specialized Agents
│   ├── 🏛️ Governance (PolicyAgent)
│   ├── 👁️ Observability (MonitoringAgent)
│   └── 🌉 Cross-domain (MLPipelineAgent)
└── 🎼 Dynamic Orchestration
    ├── LangGraph workflows
    ├── YAML configuration
    └── Environment awareness
```

## 💡 Key Features Demonstrated

### 🔄 Cross-Domain Intelligence
The MLPipelineAgent shows how to bridge governance and observability:
- Simulates Great Expectations data quality checks
- Monitors MLflow experiments
- Detects drift using EvidentlyAI patterns
- Makes decisions considering both domains

### 🎛️ Configuration-Driven Workflows
The YAML configuration allows easy customization:
```yaml
agents:
  - name: monitoring_agent
    logic: "cartai.agents.observability.monitoring_agent.MonitoringAgent"
    params:
      monitoring_config:
        thresholds:
          accuracy_degradation_threshold: 0.05
```

### 🌍 Environment Awareness
Different configurations for different environments:
- Development: Relaxed thresholds, local MLflow
- Production: Strict governance, enterprise integrations
- Testing: Mock services for CI/CD

## 🎪 Example Workflow

1. **MonitoringAgent** collects MLflow experiment metrics
2. **MLPipelineAgent** performs cross-domain analysis:
   - Checks data quality (Great Expectations simulation)
   - Detects model drift (EvidentlyAI simulation)
   - Makes deployment decision
3. **PolicyAgent** enforces governance policies and creates audit trail

## 🛠️ Next Steps for Development

### Immediate (Next Sprint)
- [ ] Add real Great Expectations MCP integration
- [ ] Implement EvidentlyAI MCP wrapper
- [ ] Add Slack notifications
- [ ] Create web dashboard

### Short-term (Next Month)
- [ ] Add more governance policies
- [ ] Implement approval workflows
- [ ] Add prometheus metrics export
- [ ] Create deployment pipeline

### Long-term (Next Quarter)
- [ ] Multi-tenant support
- [ ] Advanced conditional routing
- [ ] ML model lifecycle management
- [ ] Compliance reporting dashboard

## 🧪 Testing the System

The current implementation uses simulated data, making it perfect for:
- **Development**: No external dependencies
- **Testing**: Predictable results for CI/CD
- **Demos**: Consistent behavior for presentations

## 📚 Learning from This Implementation

This incremental approach demonstrates:
1. **Separation of Concerns**: MCPs, Agents, and Orchestration are independent
2. **Extensibility**: Easy to add new agents, MCPs, or workflows
3. **Configuration-Driven**: Changes without code deployment
4. **Cross-Domain Intelligence**: Bridging different operational domains
5. **Enterprise-Ready**: Audit trails, error handling, environment awareness

The foundation is now solid for scaling to a full enterprise AI governance platform!
```
