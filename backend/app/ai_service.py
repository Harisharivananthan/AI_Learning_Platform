import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_recommendation(user_name: str, progress_summary: str) -> str:
    """
    Generate personalized AI course recommendations or feedback.
    """
    try:
        prompt = f"""
        The user {user_name} has the following learning progress:
        {progress_summary}.
        Suggest 2–3 personalized AI or ML courses to continue learning effectively.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert AI mentor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating AI recommendation: {e}"
