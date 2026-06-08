import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])


def score_lead(name: str, business: str, problem: str, email: str) -> dict:
    """
    Score lead hot/cold via Groq.
    Returns: {"score": "hot"|"cold", "reason": str, "confidence": "high"|"medium"|"low"}
    """
    prompt = f"""You are a lead qualification assistant for a business automation agency.
Analyze this lead and classify them.

Lead details:
- Name: {name}
- Business: {business}
- Problem they want to solve: {problem}
- Email: {email}

Scoring criteria:
HOT = specific problem stated, real business context, professional or domain email, clear pain point
COLD = vague interest, fake-looking name, random Gmail with numbers, no real business context, spam-like

Respond with ONLY this JSON. No explanation. No markdown:
{{"score": "hot" or "cold", "reason": "one sentence max", "confidence": "high" or "medium" or "low"}}"""

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

        return json.loads(raw)

    except json.JSONDecodeError:
        return {"score": "cold", "reason": "parsing error — manual review needed", "confidence": "low"}
    except Exception as e:
        return {"score": "cold", "reason": f"scoring error: {str(e)}", "confidence": "low"}


if __name__ == "__main__":
    print("HOT TEST:", score_lead(
        name="Priya Mehta",
        business="JEE coaching institute, 200 students",
        problem="manually calling every inquiry, losing leads who don't follow up within 1 hour",
        email="priya@coachingcentre.com"
    ))
    print("COLD TEST:", score_lead(
        name="xyz123",
        business="nothing",
        problem="hi",
        email="test9999@gmail.com"
    ))
