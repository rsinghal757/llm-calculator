import os
import json
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
import openai
from typing import Dict, Optional

# Load environment variables
load_dotenv()

# Initialize OpenAI client
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

# Path to the functions configuration file
FUNCTIONS_FILE = "app/functions.json"

# Load calculator functions from file or use defaults
def load_calculator_functions():
    try:
        if os.path.exists(FUNCTIONS_FILE):
            with open(FUNCTIONS_FILE, "r") as f:
                return json.load(f)
        else:
            # Default calculator functions
            default_functions = {
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
            # Save default functions to file
            with open(FUNCTIONS_FILE, "w") as f:
                json.dump(default_functions, f, indent=4)
            return default_functions
    except Exception as e:
        print(f"Error loading calculator functions: {e}")
        return {}

# Save calculator functions to file
def save_calculator_functions(functions):
    try:
        with open(FUNCTIONS_FILE, "w") as f:
            json.dump(functions, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving calculator functions: {e}")
        return False

# Get calculator functions dependency
def get_calculator_functions():
    return load_calculator_functions()

# Define routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, functions: Dict = Depends(get_calculator_functions)):
    """Render the home page with the calculator interface."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "functions": functions}
    )

@app.post("/api/calculate/{function_id}", response_class=HTMLResponse)
async def calculate(
    request: Request, 
    function_id: str, 
    user_input: str = Form(...),
    functions: Dict = Depends(get_calculator_functions)
):
    """Process user input with the selected calculator function."""
    if function_id not in functions:
        raise HTTPException(status_code=404, detail="Function not found")
    
    function = functions[function_id]
    system_prompt = function["prompt"]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # You can change this to a different model if needed
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
async def get_function_prompt(
    request: Request, 
    function_id: str,
    functions: Dict = Depends(get_calculator_functions)
):
    """Get the input prompt for a specific calculator function."""
    if function_id not in functions:
        raise HTTPException(status_code=404, detail="Function not found")
    
    function = functions[function_id]
    return function["input_prompt"]

@app.get("/manage", response_class=HTMLResponse)
async def manage_functions(request: Request, functions: Dict = Depends(get_calculator_functions)):
    """Render the function management page."""
    return templates.TemplateResponse(
        "manage.html", 
        {"request": request, "functions": functions}
    )

@app.get("/edit/{function_id}", response_class=HTMLResponse)
async def edit_function_form(
    request: Request, 
    function_id: str,
    functions: Dict = Depends(get_calculator_functions)
):
    """Render the edit function form."""
    if function_id != "new" and function_id not in functions:
        raise HTTPException(status_code=404, detail="Function not found")
    
    function = functions.get(function_id, {"name": "", "prompt": "", "input_prompt": ""})
    return templates.TemplateResponse(
        "edit.html", 
        {
            "request": request, 
            "function": function, 
            "function_id": function_id,
            "is_new": function_id == "new"
        }
    )

@app.post("/save-function", response_class=RedirectResponse)
async def save_function(
    request: Request,
    function_id: str = Form(...),
    is_new: bool = Form(False),
    name: str = Form(...),
    prompt: str = Form(...),
    input_prompt: str = Form(...),
    new_function_id: Optional[str] = Form(None),
    functions: Dict = Depends(get_calculator_functions)
):
    """Save a function (new or edited)."""
    # Validate inputs
    if not name or not prompt or not input_prompt:
        raise HTTPException(status_code=400, detail="All fields are required")
    
    # For new functions, use the new_function_id
    if is_new:
        if not new_function_id:
            raise HTTPException(status_code=400, detail="Function ID is required for new functions")
        
        # Check if function ID already exists
        if new_function_id in functions:
            raise HTTPException(status_code=400, detail="Function ID already exists")
        
        function_id = new_function_id
    
    # Update or add the function
    functions[function_id] = {
        "name": name,
        "prompt": prompt,
        "input_prompt": input_prompt
    }
    
    # Save to file
    save_calculator_functions(functions)
    
    # Redirect to the manage page
    return RedirectResponse(url="/manage", status_code=303)

@app.post("/delete-function/{function_id}", response_class=RedirectResponse)
async def delete_function(
    request: Request,
    function_id: str,
    functions: Dict = Depends(get_calculator_functions)
):
    """Delete a function."""
    if function_id not in functions:
        raise HTTPException(status_code=404, detail="Function not found")
    
    # Remove the function
    del functions[function_id]
    
    # Save to file
    save_calculator_functions(functions)
    
    # Redirect to the manage page
    return RedirectResponse(url="/manage", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 