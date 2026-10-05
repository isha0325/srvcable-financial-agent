import glob
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env file
load_dotenv()

# Initialize OpenAI client pointing to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

RESEARCH_FOLDER = "./candidate/research_pack"
TICKER = "NSE: SRVCABLE"


def load_documents(folder):
    """Load all markdown files from the research folder."""
    documents = {}
    files = glob.glob(os.path.join(folder, "*.md"))

    for file in files:
        name = os.path.basename(file)
        with open(file, "r", encoding="utf-8") as f:
            documents[name] = f.read()

    return documents


def generate_brief():
    # Read research files
    documents = load_documents(RESEARCH_FOLDER)

    if not documents:
        print("No markdown files found in research_pack folder.")
        return

    print(f"Loaded {len(documents)} documents.")
    print(f"Generating research brief for {TICKER} via OpenRouter...")

    # Combine all documents into prompt
    research_text = ""
    for filename, content in documents.items():
        research_text += (
            f"\n--- DOCUMENT ---\n"
            f"FILENAME: {filename}\n"
            f"CONTENT:\n{content}\n"
        )

    prompt = f"""
You are a financial analyst. Analyze the research documents given below
for {TICKER} (Sarvottam Cables).

Create a concise one-page financial research brief in Markdown.

Include these 5 sections:

1. **Snapshot**
   Give a short overview of the company, its main business,
   and important financial/stock information.

2. **Bull Case**
   Mention 3-4 important growth opportunities, strengths,
   or positive catalysts.

3. **Bear Case**
   Mention 3-4 major risks, financial problems,
   operational issues, or governance concerns.

4. **Open Questions**
   Mention 3-4 important things that are still unclear
   or should be monitored.

5. **Sources**
   Mention the exact filenames used for the information.

Use only the information available in the research documents.

--- RESEARCH DOCUMENTS ---
{research_text}
"""

    # Call OpenRouter's free model router
    response = client.chat.completions.create(
        model="openrouter/free",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "You are a financial analyst who creates structured stock research briefs.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    brief = response.choices[0].message.content

    # Save output
    output_file = "RESEARCH_BRIEF_SRVCABLE.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(brief)

    print(f"Done! Research brief saved to {output_file}")


if __name__ == "__main__":
    generate_brief()