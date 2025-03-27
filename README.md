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
pytest -v tests/test_event.py
```



## User Authentication
### Register a New User
To use protected endpoints, you must first register an account.

- **Endpoint:** `POST /register/`
- **Request Body (JSON):**
  ```json
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword"
  }
  ```

  
  - **Response (JSON):**
    ```json
    {
      "message": "User registered successfully"
    }
    ```

    
### Login and Get Access Token
After registering, log in to receive an access token.
- **Endpoint: POST /token**
- **Request Body (form-data):**
  ```ini
  username=testuser
  password=securepassword
  ```

  
- **Response (JSON):**
  ```json
    {
      "access_token": "your_generated_token",
      "token_type": "bearer"
    }
  ```
  
  - **Note: Save the access_token. You'll need it to authenticate API requests.**


  ### Use Token for Authenticated Requests
  - **For protected endpoints, include the token in the Authorization header:**
    ```sh
    Authorization: Bearer your_generated_token
    ```
    -**Example cURL request:**
    ```sh
    curl -H "Authorization: Bearer your_generated_token" -X GET http://127.0.0.1:8000/events/
    ```


  

### API Endpoints


| Method  | Endpoint                               | Description                          |
|---------|----------------------------------------|--------------------------------------|
| `POST`  | `/events/`                             | Create a new event                   |
| `GET`   | `/events/`                             | Get all events                       |
| `POST`  | `/attendees/register/`                | Register an attendee                 |
| `PUT`   | `/attendees/checkin/{attendee_id}/`   | Check in an attendee                 |
| `POST`  | `/events/bulk_checkin/{event_id}/`            | Bulk check-in attendees via CSV      |
| `GET`   | `/attendees/{attendee_id}/`           | Get attendee details                 |


### Bulk Attendee Check-in via CSV
- **Upload a CSV file containing attendee IDs for check-in.**
- **Example CSV format:**
```sh
attendee_id
101
102
103
```
- **API Endpoint:**
  ```sh
  POST /attendees/bulk-checkin/
  ```

- **Request Headers:**
  ```sh
  Content-Type: multipart/form-data
  Authorization: Bearer <your_token>
  ```
- **Response Example:**
  ```sh
  {
  "message": "Bulk check-in successful",
  "checked_in": [101, 102, 103],
  "failed": []
  }
