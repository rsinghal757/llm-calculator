# LLM Calculator

A web application that provides a simple interface for performing various tasks using OpenAI's APIs.

## Features

- Terminal-like interface for input and output
- Calculator-style buttons for different LLM tasks
- Tasks include: Explain Like I'm 5, Summarize, How Did We Discover X?, and more
- Simple and intuitive UI with HTMX for interactivity

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```
5. Run the application:
   ```
   uvicorn app.main:app --reload
   ```
6. Open your browser and navigate to `http://localhost:8000`

## Technologies Used

- Backend: Python with FastAPI
- Frontend: HTML, CSS, JavaScript with HTMX
- API: OpenAI's APIs for LLM functionality 