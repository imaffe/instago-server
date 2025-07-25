from app.llm_calls.gemini_ocr_llm import GeminiOCRLLM
from app.llm_calls.structure_output_llm import StructureOutputLLM

# Initialize Gemini OCR LLM as the default
ai_agent = GeminiOCRLLM()
gemini_ocr_llm = GeminiOCRLLM()  # Also expose Gemini directly for potential future use

# Initialize Structure Output LLM (using OpenRouter by default)
structure_output_llm = StructureOutputLLM(provider="openrouter")

__all__ = ["ai_agent", "gemini_ocr_llm", "structure_output_llm"]
