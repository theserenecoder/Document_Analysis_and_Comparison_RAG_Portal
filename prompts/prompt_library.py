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

1. Compare the content in two PDFs.
2. Identify the ifference in PDF and note down the page number.
3. The output you provide must be page wise comparision content.
4. If any page do not have any change, mention as 'NO CHANGE'.

Input Documents:

{combined_docs}

Your response should follow this format:

{format_instruction}
""")

PROMPT_REGISTRY = {
    'document_analysis': document_analysis_prompt,
    'document_comparision': document_comparision_prompt
}