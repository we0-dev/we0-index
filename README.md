# We0-index

[English](README.md) | [中文](README-zh.md)

A Python-based code indexing engine similar to Cursor, designed to transform Git repository code into code snippets with semantic embeddings for intelligent code search and retrieval.

## 🚀 Features

- **Code Snippet Generation**: Automatically processes Git repositories and converts code into searchable snippets
- **Semantic Search**: Generates semantic embeddings for intelligent code retrieval based on user queries
- **Multi-Language Support**: Optimized for Python, Java, Go, JavaScript, and TypeScript
- **Flexible Backends**: Supports multiple vector database backends and embedding service providers
- **MCP Integration**: Built-in support for MCP (Model Context Protocol) service calls
- **Deployment Ready**: Flexible deployment options for different environments

## 📋 Requirements

- Python 3.12+
- Git

## 🛠️ Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/we0-dev/we0-index
cd we0-index

# Set up environment configuration
cp .env.example .env
vim .env

# Configure application settings
vim resource/dev.yaml

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync
```

### Development Setup

```bash
# Install development dependencies
uv sync --frozen
```

## ⚙️ Configuration

1. **Environment Variables**: Copy `.env.example` to `.env` and configure your settings
2. **Application Config**: Edit `resource/dev.yaml` to customize your deployment
3. **Vector Database**: Configure your preferred vector database backend
4. **Embedding Service**: Set up your embedding service provider



## 🏗️ Architecture

We0-index is built with a modular architecture supporting:

- **Code Parsers**: Language-specific code parsing and snippet extraction
- **Embedding Engines**: Multiple embedding service integrations
- **Vector Stores**: Pluggable vector database backends
- **Search Interface**: RESTful API and CLI for code search
- **MCP Protocol**: Model Context Protocol for AI integration

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



## 📚 Documentation

For detailed documentation, please visit our [Documentation Site](https://docs.we0-dev.com) or check the `docs/` directory.

## 🐛 Issues

If you encounter any issues, please [create an issue](https://github.com/we0-dev/we0-index/issues) on GitHub.

## 📞 Support

- 📧 Email: we0@wegc.cn 
- 💬 Discussions: [GitHub Discussions](https://github.com/we0-dev/we0-index/discussions)
- 📖 Wiki: [Project Wiki](https://deepwiki.com/we0-dev/we0-index)

## 🌟 Acknowledgments

- Thanks to all contributors who have helped make this project better
- Inspired by Cursor's approach to code intelligence
- Built with modern Python tooling and best practices

---

**Made with ❤️ by the We0-dev Team**