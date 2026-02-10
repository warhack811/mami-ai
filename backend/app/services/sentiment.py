from langchain_groq import ChatGroq
from app.core.config import settings
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class SentimentResult(BaseModel):
    mood: str = Field(description="User's emotional state (e.g., Happy, Angry, Frustrated, Neutral, Rushed)")
    urgency: str = Field(description="Urgency level (Low, Medium, High)")
    suggested_tone: str = Field(description="The tone the assistant should adopt (e.g., Empathetic, Concise, Cheerful)")

# Use a fast model for this middleware task
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)
parser = JsonOutputParser(pydantic_object=SentimentResult)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Analyze the user's message for sentiment and suggest a response tone. Return JSON."),
    ("user", "{text}\n\n{format_instructions}")
])

chain = prompt | llm | parser

async def analyze_sentiment(text: str) -> SentimentResult:
    try:
        # Default fallback
        result = await chain.ainvoke({"text": text, "format_instructions": parser.get_format_instructions()})
        return SentimentResult(**result)
    except Exception as e:
        print(f"Sentiment Analysis Failed: {e}")
        return SentimentResult(mood="Neutral", urgency="Low", suggested_tone="Helpful and Professional")
