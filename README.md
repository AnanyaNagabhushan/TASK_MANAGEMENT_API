```md
# 📝 Task Management API:
A simple and secure Task Management API built using Flask, PostgreSQL, and JWT Authentication.  
This project allows users to register, log in, and manage tasks with full CRUD functionality.  
Environment variables are used for database configuration and secret key protection.

## 🚀 Features
- 🔐 JWT-based authentication  
- 🧾 User registration and login  
- 🗂️ Add, view, update, and delete tasks  
- 🗄️ PostgreSQL integration  
- ⚙️ Flask-Migrate for database migrations  
- 🧩 Modular and scalable architecture  
- 🌱 .env support for secure configuration  

## 🛠️ Tech Stack

- Python
- Flask
- Flask-JWT-Extended
- Flask-Migrate
- Flask-SQLAlchemy
- PostgreSQL
- python-dotenv

# ⚙️ How to Run This Project Locally

Follow these steps to set up the API on your system:

## 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/task-management-api.git
cd task-management-api
````
## 2️⃣ Create a virtual environment

```bash
python -m venv venv
```

Activate it:

### Windows:

```bash
venv\Scripts\activate
```

### Mac/Linux:

```bash
source venv/bin/activate
```

## 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Create a `.env` file

Create a file named `.env` inside the root folder and add:

DATABASE_URL=postgresql+psycopg2://username:password@localhost/tasks_db
JWT_SECRET_KEY=your_secret_key
FLASK_APP=main.py
FLASK_ENV=development

Update username/password to your local database setup.

## 5️⃣ Run database migrations

```bash
flask db upgrade
```

## 6️⃣ Start the server

```bash
flask run
```

Now the API runs at:

http://127.0.0.1:5000


# 🧪 Running Tests

```bash
pytest
```

# 👩‍💻 Author
**Ananya N**
Software Developer | Flask | Full Stack | AI Enthusiast


# 📜 License
This project is open-source under the **MIT License**.

If you want badges (like “Made with Flask,” “Python 3.10,” “MIT License”) I can add those too!
```
