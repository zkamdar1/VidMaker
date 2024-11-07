import openai

# Set your OpenAI API key
openai.api_key = "YOUR_API_KEY_HERE"

def generate_script(topic):
    prompt = f"Generate a script about the topic: {topic}. Keep it engaging and concise."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()
