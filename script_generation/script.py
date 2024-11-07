from openai import OpenAI
import os
client = OpenAI()
# Set your OpenAI API key
client.api_key = os.getenv("OPENAI_API_KEY")


def generate_script():
    prompt = f"Generate a new script."
    
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Generate a script in paragraph form that is for a motivational tiktok account where it is 2 sentences and the topic and tone is the voice and genre of Andrew Tate and David Goggins and really makes you feel in a way that you will regret for the rest of your life if you dont do the thing. Only provide the text and nothing else. No other text besides the main 2."},
        {
            "role": "user",
            "content": prompt
        }
    ]
)
    
    return (completion.choices[0].message.content)

# Example usage
# if __name__ == "__main__":
#    script_text = generate_script()
#    print(script_text)
