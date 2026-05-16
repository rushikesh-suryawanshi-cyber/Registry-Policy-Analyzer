from typing import List, Dict, Any, Optional
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class IntelligenceAgent:
    """LangChain-powered agent for advanced AI insights (Hardening, Migration, Explainability)."""

    def __init__(self, llm_model: str = "llama3.2:1b"):
        self.llm = Ollama(model=llm_model)

    def explain_policy(self, policy_data: Dict[str, Any]) -> str:
        """Explains a complex policy setting in simple terms."""
        template = """You are a Windows Security Expert. Explain the following Group Policy in simple terms to a junior sysadmin.
Explain WHAT it does, WHY it is important, and the potential RISK of enabling or disabling it.

Policy Name: {name}
Description: {description}
Registry Path: {key}\\{val}

Explanation:"""
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "name": policy_data.get('name', 'Unknown'),
            "description": policy_data.get('explainText', 'No description'),
            "key": policy_data.get('key', 'Unknown'),
            "val": policy_data.get('valueName', 'Unknown')
        })

    def recommend_browser_hardening(self) -> str:
        """Generates browser hardening recommendations."""
        template = """You are a Cybersecurity Expert. Provide a high-level summary of the top 3 Group Policy settings an administrator should configure to harden a web browser (like Edge or Chrome) on a Windows network. Focus on phishing, extensions, and password saving. Keep it actionable."""
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({})

    def get_migration_guidance(self, old_os: str = "Windows 10", new_os: str = "Windows 11") -> str:
        """Provides migration guidance between Windows versions."""
        template = """You are an Enterprise Architect. Briefly summarize the key Group Policy considerations when migrating from {old_os} to {new_os}. Mention deprecated settings like Cortana and new settings like Taskbar alignment."""
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"old_os": old_os, "new_os": new_os})
