import os, json, pdfplumber
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract raw text from a text-based PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text as string, empty string if extraction fails
    """
    full_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    return full_text.strip()
def extract_structured(raw_text: str, schema_description: str) -> dict:
    """
    Extract structured data from raw text using Groq LLM.

    Args:
        raw_text: Raw text extracted from PDF
        schema_description: Natural language description of fields to extract

    Returns:
        Dictionary with extracted fields, or {"error": "..."} on failure
    """
    if not raw_text:
        return {"error": "No text extracted from PDF"}
    
    if len(raw_text) > 6000:
        raw_text = raw_text[:6000] + "\n[truncated]"
    
    prompt = f"""Extract the following information from the text below.
Return ONLY valid JSON. No explanation. No markdown. No code blocks.

What to extract: {schema_description}

Text:
{raw_text}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        raw = response.choices[0].message.content.strip()

        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                try:
                    return json.loads(part)
                except:
                    continue

        # find first { and last } → extract only the JSON part
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(raw[start:end])

        return json.loads(raw)

    except json.JSONDecodeError as e:
        return {
            "error": "JSON parsing failed",
            "raw_response": raw,
            "detail": str(e)
        }
    except Exception as e:
        return {"error": str(e)}
def save_result(result: dict, output_path: str):
    """Save extracted data to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved to: {output_path}")

def process_pdf(pdf_path: str, schema_description: str) -> dict:
    """Full pipeline: PDF path → structured dict."""
    print(f"Processing: {pdf_path}")
    
    raw_text = extract_text_from_pdf(pdf_path)
    
    if not raw_text:
        return {"error": "Could not extract text. PDF may be scanned/image-based."}
    
    print(f"Extracted {len(raw_text)} characters")
    
    result = extract_structured(raw_text, schema_description)
    
    return result
if __name__ == "__main__":
    # replace paths and print statemnts below according to your own PDF paths
    # TEST : Group Theory Tutorial
    result = process_pdf(
        r"D:\PROJECT\1\AI AUTOMATION\day-2\tutorial_groups.pdf",
        "course_code, topic, problems (list of {problem_number, description, subtasks (list)}), challenging_problems (list)"
    )
    print("\n=== GROUP THEORY OUTPUT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))