# Event Management System API
Built with Python, FastAPI, and MongoDB.

## Features
- CRUD for Events
- Participant registration with capacity limits
- Statistics and Keyword Search

## How to Test
1. Visit the live link:https://backendeventmanager.onrender.com/docs#/
2. Use the `/docs` endpoint for interactive API testing.


Event Management System API
A robust backend system built to manage simple events and participant registrations. This project fulfills all core requirements, including database persistence, capacity limits, and duplicate registration prevention.

Live Demo
Backend URL: https://backendeventmanager.onrender.com
Interactive API Docs: backendeventmanager.onrender.com

Tech Stack
Framework: Python (FastAPI)
Database: MongoDB Atlas (Cloud)
Deployment: Render
Version Control: Git & GitHub (following Conventional Commits)

Key Features
Event Management: Create, view, update, and delete events.
Participant Registration:
Prevents duplicate emails for the same event.
Automatically enforces maxParticipants limits.
Search & Filters: Search for events by keyword.
Statistics: View total events, total registrations, and identify the most popular event.
Clean Architecture: Uses Pydantic for data validation and proper HTTP status codes.

Project Structure
text
├── main.py            # Main application logic and routes
├── requirements.txt   # Python dependencies
├── .gitignore         # Shields sensitive .env files
└── README.md          # Project documentation


Local Setup
Clone the repository:
bash
git clone https://github.com/aa7225/BackendEventManager.git


Install dependencies:
bash
pip install -r requirements.txt


Set up environment variables:
Create a .env file in the root directory:
text
MONGO_URI=your_mongodb_connection_string


Run the server:
bash
python -m uvicorn main:app --reload

Access the API: Open http://127.0.0.1 in your browser.



