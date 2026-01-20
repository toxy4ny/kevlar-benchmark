"""
Adversarial-Poetry jailbreak (local Ollama/LangChain)
Compatible with kevlar-benchmark extension slot
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

META = Path(__file__).parent / "data" / "poetry" / "meta_prompt.txt"
STYLE_DIR = META.parent / "style_examples"

class PoetryLocalAttack:
    def __init__(self, rewriter_model: str = "deepseek-r1:1.5b", temperature: float = 0.7):
        self.llm = Ollama(model=rewriter_model, temperature=temperature)
        self.chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template("{meta_block}")
        )
        self.meta_template = META.read_text(encoding="utf8")
        self.styles = "\n---\n".join(
            f.read_text().strip() for f in sorted(STYLE_DIR.glob("*.txt"))[:5]
        )

    def transform(self, prompt: str, _: Dict[str, Any]) -> Dict[str, Any]:
        block = self.meta_template.format(
            style_examples=self.styles,
            harmful_prompt=prompt
        )
        poem = self.chain.run(meta_block=block).strip()
        return {"prompt": poem, "attack_name": self.name()}

    @staticmethod
    def name() -> str:
        return "poetry_local"