# 📚 本地 RAG 智能 PDF 问答助手 (Zero-DLL 架构)

基于 Streamlit + DeepSeek API + BM25 算法构建的极简、轻量级文档智能问答 Web 应用。

## 💡 项目背景与痛点解决

在传统的本地 RAG（检索增强生成）架构中，大量依赖如 ChromaDB、FastEmbed 等底层需要 C++ 编译环境的稠密向量检索方案。这在 Windows 环境下极易引发 `WinError 1114` 等动态链接库 (DLL) 初始化崩溃的系统级兼容性问题。

**本项目通过架构降级与重构，彻底废弃了复杂的本地 C++ 依赖：**
采用 100% 纯 Python 实现的 **BM25 稀疏检索算法** 配合 `jieba` 中文分词，实现了真正的跨平台“开箱即用”，并在专有名词和关键词召回率上表现优异。

## ✨ 核心特性

* 🛡️ **拒绝环境地狱**：零 C++ 编译依赖，纯 Python 架构，告别 Windows 下的底层环境冲突。
* ⚡ **极速精准检索**：利用 TF-IDF 的变种 BM25 算法，针对中文长文本实现极速、高召回率的切片检索。
* 💬 **现代化交互 UI**：采用 Streamlit 框架，打造流畅的沉浸式对话体验。
* 🔒 **隐私与安全**：支持通过 Web UI 动态注入大模型 API Key，代码层面零硬编码敏感信息。

## 🛠️ 技术栈

- **前端与交互**: Streamlit
- **大语言模型**: DeepSeek-Chat (OpenAI 兼容接口)
- **文档处理**: pypdf, langchain-text-splitters
- **核心检索算法**: rank_bm25, jieba

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone [https://github.com/你的用户名/你的仓库名.git](https://github.com/你的用户名/你的仓库名.git)
cd 你的仓库名