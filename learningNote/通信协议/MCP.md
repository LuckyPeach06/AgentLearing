# MCP(Model Context Protocol)

设计理念：标准化Agent与外部工具/资源的通信方式

设计哲学：上下文共享。
    它不仅是一个RPC协议，他还允许Agent与工具之间共享上下文信息。
    比如，当Agent通过MCP访问一个代码仓库时，MCP不仅可以提供文件内容，还能提供代码结构、依赖关系、提交历史等上下文信息。

# 社区生态
MCP 社区的三个资源库:
    Awesome MCP Servers (https://github.com/punkpeye/awesome-mcp-servers)
        社区维护的 MCP 服务器精选列表
        包含各种第三方服务器
        按功能分类，易于查找

    MCP Servers Website (https://mcpservers.org/)
        官方 MCP 服务器目录网站
        提供搜索和筛选功能
        包含使用说明和示例
        Official MCP Servers (https://github.com/modelcontextprotocol/servers)

    Anthropic 官方维护的服务器
        质量最高、文档最完善
        包含常用服务的实现