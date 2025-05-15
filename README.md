<div align="center">
<h1 align="center">🌟 Cartai 🌟</h1>
<h3>Crafting intelligent E2E trazes & documentation for trustworthy AI</h2>

  <kbd style="background-color: #ffffd7">**👩‍🔬 Agents for tracking your AI project lineage.**</kbd>
<br>

[![PyPI version](https://img.shields.io/pypi/v/cartai.svg)](https://pypi.org/project/cartai/)
[![Build Status](https://github.com/ContrastoAI/cartai/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/ContrastoAI/cartai/actions)
[![GitHub Repo stars](https://img.shields.io/github/stars/contrastoAI/cartai?style=flat)](https://github.com/contrastoAI/cartai)
<a href="https://github.com/huggingface/smolagents/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/huggingface/smolagents.svg?color=blue"></a>
<a href="https://github.com/contrastoai/cartai/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/contrastoai/cartai.svg"></a>


</div>

<br>

`cartai` is a library that enables end-to-end traceability and lineage of your AI projects. PRDs, data lineage, training experiments, deployments, monitoring, and third-party vibe-coding platforms.

## 📂 Codebase Structure

```
📁 /
  📄 .env.example
  📁 .github/
    📁 workflows/
      📄 pr-review.yaml
      📄 pre-commit.yaml
      📄 publish.yaml
  📄 .pre-commit-config.yaml
  📄 .python-version
  📁 cartai/
    📄 __init__.py
    📁 adapters/
    📁 cli/
      📁 commands/
        📄 __init__.py
        📄 pr_diff.py
        📄 readme.py
      📄 main.py
    📁 core/
      📄 __init__.py
      📄 code_parser.py
    📁 lineage/
    📁 llm_agents/
      📄 __init__.py
      📄 documenter.py
      📄 graph.py
      📄 graph_states.py
      📁 templates/
        📄 pr_diff.jinja
        📄 readme.jinja
      📁 utils/
        📄 __init__.py
        📄 model_client_utils.py
        📄 yaml_utils.py
  📁 langgraph_config/
    📄 dummy_config.yaml
    📄 repo_documenter.yaml
  📄 LICENSE
  📁 llm_agents/
    📁 templates/
  📄 Makefile
  📄 pyproject.toml
  📄 README.md
  📄 uv.lock
```

## ⚙️ Installation

To get started with the CartAI project, follow these instructions to set up your environment:

1. Clone the repository:
   ```bash
   git clone https://www.github.com/ContrastoAI/cartai
   cd cartai
   ```

2. Ensure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) and [pre-commit](https://pre-commit.com/) installed. You can check their installation with:
   ```bash
   make .uv
   make .pre-commit
   ```

3. Install all dependencies and set up your environment:
   ```bash
   make install-all
   ```

## 💻 Usage

You can run the project using the provided Makefile commands. For example, to generate the README documentation, you can use:
```bash
make run_readme
```
This command will execute the documentation generation process with the description "Crafting intelligent E2E documentation for trustworthy AI." and output it to `README_new.md`.

### Other Makefile Commands

- **Format code**:
  ```bash
  make format
  ```

- **Lint code**:
  ```bash
  make lint
  ```

- **Run tests**:
  ```bash
  make test
  ```

- **Run pre-commit hooks**:
  ```bash
  make pre-commit
  ```

## 🚀 Deployment

To deploy the project, follow the standard deployment procedures for your environment. Ensure all dependencies are installed, and run the necessary commands as needed.

## 🤝 Contributing

We welcome contributions! Here's how you can contribute:

1. Fork the repository 🍴
2. Create your feature branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add YourFeature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a pull request 📬

Please follow the coding guidelines and check the Makefile or contributing docs if available.
```
