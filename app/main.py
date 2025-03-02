import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_model = os.getenv("OPENAI_MODEL")
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

client = openai.OpenAI(api_key=openai_api_key)

# Initialize FastAPI app
app = FastAPI(title="LLM Calculator")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Define calculator functions
CALCULATOR_FUNCTIONS = {
    "explain": {
        "name": "Explain Like I'm 5",
        "prompt": "Explain the following concept as if you were explaining it to a 5-year-old child. Use simple language, analogies, and examples that a child would understand.",
        "input_prompt": "Enter a topic to explain:"
    },
    "summarize": {
        "name": "Summarize",
        "prompt": "Provide a concise summary of the following text, highlighting the key points and main ideas.",
        "input_prompt": "Enter text to summarize:"
    },
    "discover": {
        "name": "How Did We Discover?",
        "prompt": "Explain the historical process of how humans discovered or developed knowledge about the following topic. Include key figures, experiments, and breakthroughs.",
        "input_prompt": "Enter a scientific concept, phenomenon, or technology:"
    },
    "pros_cons": {
        "name": "Pros & Cons",
        "prompt": "List and explain the main advantages (pros) and disadvantages (cons) of the following topic or decision.",
        "input_prompt": "Enter a topic to analyze:"
    },
    "simplify": {
        "name": "Simplify",
        "prompt": "Take the following complex text and simplify it to make it more accessible and easier to understand, while preserving the key information.",
        "input_prompt": "Enter complex text to simplify:"
    }
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with the calculator interface."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "functions": CALCULATOR_FUNCTIONS}
    )

@app.post("/api/calculate/{function_id}", response_class=HTMLResponse)
async def calculate(request: Request, function_id: str, user_input: str = Form(...)):
    """Process user input with the selected calculator function."""
    if function_id not in CALCULATOR_FUNCTIONS:
        raise HTTPException(status_code=404, detail="Function not found")
    
    function = CALCULATOR_FUNCTIONS[function_id]
    system_prompt = function["prompt"]
    
    try:
        response = client.chat.completions.create(
            model=openai_model,  # You can change this to a different model if needed
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        
        # Return just the result text for HTMX to insert
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/function/{function_id}", response_class=HTMLResponse)
async def get_function_prompt(request: Request, function_id: str):
    """Get the input prompt for a specific calculator function."""
    if function_id not in CALCULATOR_FUNCTIONS:
        raise HTTPException(status_code=404, detail="Function not found")
    
    function = CALCULATOR_FUNCTIONS[function_id]
    return function["input_prompt"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 