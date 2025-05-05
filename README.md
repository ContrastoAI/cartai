# cartai

Crafting intelligent E2E documentation for trustworthy AI.

## Overview

The `cartai` project is dedicated to creating intelligent end-to-end documentation systems tailored for trustworthy AI applications. This involves leveraging various components to ensure that documentation is not only comprehensive but also easily maintainable and adaptable.

### Project Structure

The codebase is organized into several key directories, each serving a specific purpose:

| Folder         | Purpose                                      |
| ---------------| -------------------------------------------- |
| `adapters/`    | Thin, interchangeable tools                  |
| `cli/`         | Lightweight user entry points                |
| `core/`        | Pure logic, no external dependencies         |
| `lineage/`     | High-level lineage coordination              |
| `llm_agents/`  | LLM-based logic only                         |
| `tests/`       | Developer trust & confidence                 |
| `examples/`    | Fast time-to-first-success                   |

## Installation

To set up the `cartai` project, you need to have Python 3.12 or higher installed on your machine. The project uses [uv](https://docs.astral.sh/uv/getting-started/) as the package manager.

1. Clone the repository:
   ```bash
   git clone https://www.github.com/ContrastoAI/cartai.git
   cd cartai
   ```

2. Install the dependencies using the following command:
   ```bash
   uv install
   ```

3. Alternatively, you can install the package in editable mode for development:
   ```bash
   uv pip install -e .
   ```

4. Ensure that `pre-commit` is installed for maintaining code quality:
   ```bash
   uv run pre-commit
   ```

## Usage

The `cartai` package can be run from the command line. You can generate documentation using the following command:

```bash
uv run cartai readme --description "Crafting intelligent E2E documentation for trustworthy AI." --code "." --output "README.md"
```

This will create a `README.md` file based on the specified input and template.

## Contributing

Contributions are welcome! If you would like to help improve `cartai`, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add my feature"
   ```
4. Push your changes:
   ```bash
   git push origin feature/my-feature
   ```
5. Submit a pull request.

Thank you for considering contributing to `cartai`! Your efforts help improve the project and assist others in the AI community.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more details.