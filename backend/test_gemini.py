import google.generativeai as genai

# ✅ Replace with your actual NEW API key here
genai.configure(api_key="AIzaSyBO1KlR0S5mIlvazf73SgplIqV-4VJZIeI")

try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")  # Use flash model for higher quota
    response = model.generate_content("Write a short subject for this email: hello")
    print("✅ Gemini Response:", response.text)
except Exception as e:
    print("❌ Error:", e)
