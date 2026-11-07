## 项目工程化
1、requirements文件和venv虚拟环境
    venv虚拟环境相当于项目独立的包，每个项目单独一个环境，进行项目间的依赖隔离

    requirements文件相当于pom文件，引入项目依赖

2、requiredments文件中的openai和python-dotenv是什么
    openai是OpenAI 公司官方发布的 Python 客户端库，DeepSeek、Qwen 这些厂商实现了和 OpenAI 一模一样的接口格式(即"OpenAI 兼容协议"),所以同一个 SDK 换个 base_url 就能调它们

    python-dotenv是配置文件加载器，通过load_dotenv()将.env的配置读到环境里，相当于Spring Boot 读 application.yml 注入配置

    openai = 帮你和 LLM 服务通信的工具,python-dotenv = 帮你管理配置和密钥的工具