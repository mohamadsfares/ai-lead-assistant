from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

response = client.messages.create(         
    model="claude-haiku-5-5",
    max_tokens=1000,
    system="You are the website assistant for Cedar Ridge Roofing & Renovation, "
           "a home-improvement company in Columbus, Ohio. Answer customer questions in a friendly, "
           "short way.",                   
    messages=[{"role": "user", "content": "How much does a new asphalt shingle roof cost, and do you serve Westerville?"}],
)

for block in response.content:
    if block.type=="text":
        print(block.text)
         

print(response.usage)
print(response.stop_reason)