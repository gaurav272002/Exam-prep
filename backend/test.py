import requests
import os
import PyPDF2
import io

# 🔐 Set your API key here (TEMP for testing)
OPENROUTER_API_KEY = ""

# 🧠 AI Extraction Function
def extract_with_ai(text_chunk):

    prompt = f"""
Extract syllabus into structured JSON:

{text_chunk}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    data = response.json()

    # 🔍 DEBUG: print full response
    print("\nFULL RESPONSE:\n", data)

    # ✅ SAFE extraction
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        return f"ERROR: {data}"


# 📄 Extract text from PDF
def extract_pdf_text(file_path):
    with open(file_path, "rb") as f:
        pdf = PyPDF2.PdfReader(f)
        text = ""

        for page in pdf.pages:
            text += page.extract_text() + "\n"

    return text


# ✂️ Chunk text (important for long PDFs)
def chunk_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]


# 🚀 MAIN
if __name__ == "__main__":

    file_path = "sample.pdf"  # 👉 put your PDF here

    print("📄 Reading PDF...")
    text = extract_pdf_text(file_path)

    chunks = chunk_text(text)

    print(f"🔍 Total chunks: {len(chunks)}")

    results = []

    for i, chunk in enumerate(chunks):
        print(f"\n⚡ Processing chunk {i+1}...")

        try:
            output = extract_with_ai(chunk)
            results.append(output)

            print("✅ AI Output:")
            print(output[:500])  # preview

        except Exception as e:
            print("❌ Error:", e)

    print("\n🎯 FINAL RESULTS:")
    for r in results:
        print(r)