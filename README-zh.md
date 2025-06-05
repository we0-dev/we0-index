# We0-index

一个基于Python的类似Cursor的代码索引引擎，可将Git仓库代码转化为代码片段并生成语义embedding，根据用户query实现智能代码搜索和检索。

## 🚀 功能特性

- **代码片段生成**：自动处理Git仓库，将代码转换为可搜索的代码片段
- **语义搜索**：生成语义embeddings，基于用户查询实现智能代码检索
- **多语言支持**：针对Python、Java、Go、JavaScript和TypeScript进行优化
- **灵活后端**：支持多种向量数据库后端和embedding服务提供商
- **MCP集成**：内置MCP（模型上下文协议）服务调用支持
- **部署就绪**：为不同环境提供灵活的部署选项

## 📋 环境要求

- Python 3.12+
- Git

## 🛠️ 安装

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/we0-dev/we0-index
cd we0-index

# 设置环境配置
cp .env.example .env
vim .env

# 配置应用设置
vim resource/dev.yaml

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate
uv sync
```

### 开发环境设置

```bash
# 安装开发依赖
uv sync --frozen
```

## ⚙️ 配置

1. **环境变量**：将`.env.example`复制为`.env`并配置您的设置
2. **应用配置**：编辑`resource/dev.yaml`以自定义您的部署
3. **向量数据库**：配置您首选的向量数据库后端
4. **Embedding服务**：设置您的embedding服务提供商

## 🚀 启动服务

We0-index支持两种运行模式：Web API服务和MCP协议服务。

### Web API 模式

启动FastAPI Web服务器，提供RESTful API接口：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动Web服务
python main.py --mode fastapi
```

Web服务将在配置的主机和端口上启动（默认配置请查看`resource/dev.yaml`）。

### MCP 协议模式

启动MCP（模型上下文协议）服务，用于AI集成：

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动MCP服务（默认使用streamable-http传输协议）
python main.py --mode mcp

# 指定其他传输协议
python main.py --mode mcp --transport stdio
python main.py --mode mcp --transport websocket
```

MCP服务默认使用streamable-http传输协议运行，可与支持MCP的AI客户端集成。

### 运行参数

**模式参数**：
- `--mode fastapi`：启动Web API服务
- `--mode mcp`：启动MCP协议服务

**传输协议参数**（仅适用于MCP模式）：
- `--transport streamable-http`：使用HTTP流传输（默认）
- `--transport stdio`：使用标准输入输出传输
- `--transport websocket`：使用WebSocket传输


## 🏗️ 架构

We0-index采用模块化架构，支持：

- **代码解析器**：特定语言的代码解析和片段提取
- **Embedding引擎**：多种embedding服务集成
- **向量存储**：可插拔的向量数据库后端
- **搜索接口**：用于代码搜索的RESTful API和CLI
- **MCP协议**：用于AI集成的模型上下文协议

## 🤝 贡献

我们欢迎贡献！请查看我们的[贡献指南](CONTRIBUTING.md)了解详情。

1. Fork 仓库
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 📝 许可证

本项目基于MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。


## 📚 文档

详细文档请访问我们的[文档站点](https://docs.we0-dev.com)或查看`docs/`目录。

## 🐛 问题反馈

如果您遇到任何问题，请在GitHub上[创建issue](https://github.com/we0-dev/we0-index/issues)。

## 📞 支持

- 📧 邮箱：we0@wegc.cn 
- 💬 讨论：[GitHub Discussions](https://github.com/we0-dev/we0-index/discussions)
- 📖 Wiki：[项目Wiki](https://deepwiki.com/we0-dev/we0-index)

## 🌟 致谢

- 感谢所有帮助改进这个项目的贡献者
- 灵感来源于Cursor的代码智能方法
- 使用现代Python工具和最佳实践构建

---

**由We0-dev团队用❤️制作**
