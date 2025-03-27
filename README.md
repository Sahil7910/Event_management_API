# Event Management API 🎉

This is a **FastAPI-based** Event Management API that allows users to create events, register attendees, and track check-ins.

## 🚀 Features
- **Event Management**: Create, update, List events.
- **Attendee Registration**: Register attendees for events.
- **Check-in System**: Allow attendees to check in to an event.
- **Bulk Check-in**: Upload a CSV file to check in multiple attendees at once
- **Authentication**: Secure access using JWT tokens.

## 🏗️ Tech Stack
- **FastAPI** 🚀 (for API development)
- **SQLAlchemy** (for database ORM)
- **SQLite** (for data storage)
- **Pytest** (for testing)


## 📦 Installation & Setup

###  Clone the repository
```sh
git clone https://github.com/Sahil7910/Event_management_API.git
cd Event_management_API
```

### Create a Virtual Environment & Install Dependencies
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

###  Set Up Database
```sh
python database.py
```

###  Run the Server
```sh
uvicorn main:app --reload
```
The API will be available at: http://127.0.0.1:8000

### Running Tests
```sh
pytest
```

### Authentication
-**Uses JWT tokens for authentication.**
-**Get a token via /token endpoint.**



 
