from langchain_core.prompts import ChatPromptTemplate

document_analysis_prompt = ChatPromptTemplate.from_template("""
You are a highly capable assistant trained to analyze and summarize documents.
Return Only Valid JSON matching the exact schema below

{format_instructions}

Analyze this document:
{document_text}
""")

document_comparision_prompt = ChatPromptTemplate.from_template("""
You will be provided with content form two pdfs. Your tasks are as follows:

1.
                                                               """)

PROMPT_REGISTRY = {'document_analysis': document_analysis_prompt}