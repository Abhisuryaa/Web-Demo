# TechVritti - Student Assessment System

A comprehensive student assessment platform that allows students to create profiles, take skill evaluation quizzes, and track their progress.

## Features

- User registration and authentication
- Professional profile creation
- Skills assessment quiz system
- Dynamic dashboard
- Progress tracking
- Modern and responsive UI

## Technical Stack

- Backend: Flask (Python)
- Database: SQLAlchemy with SQLite
- Frontend: HTML5, CSS3, JavaScript
- UI Framework: Bootstrap 5
- Authentication: Flask-Login

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
techvritti/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   └── quiz.html
├── app.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"# Web-Demo" 
"# Web-Demo" 
"# Web-Demo" 
"# Web-Demo" 
