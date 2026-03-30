# Food Ordering Application 
It is a **web-based food ordering system built using Flask and SQLite**, designed to simulate basic restaurant order management with full CRUD functionality for administrators.

### Admin Features
- Menu management (ceate, read, update, and delete menu items)
- Order management (view, edit, and delete all orders)
- User management overview (edit and delete user profile)

### System Features
- Web-based interface using **Flask**
- Persistent data storage using **SQLite**
- REST-like routing for different functionalities
- Lightweight and easy to run locally

### Project Structure
```
food_ordering_app/
│
├── app.py                          # Main Flask application entry point
├── database.py                     # Database connection and setup
├── init_db.py                      # Initialize database schema
│
├── menu_database_sqlite.py         # Menu-related database operations
├── order_database_sqlite.py        # Order-related database operations
├── user_database_sqlite.py         # User-related database operations
│
├── templates/                      # HTML templates (Jinja2)
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── profile.html
│ ├── menu.html
│ ├── display_menu.html
│ ├── add_menu.html
│ ├── edit_menu.html
│ ├── delete_account.html
│ ├── create_order.html
│ ├── take_order.html
│ ├── orders.html
│ └── order_detail.html
│
├── static/                         # Static assets (CSS)
│ └── style.css
│
├── db/                             # SQLite database storage
│ └── food_ordering.db
│
├── Procfile                        # Deployment entry point using Render
├── requirements.txt                # Python dependencies
└── README.md
```

### Tech Stack
- **Backend**: Flask (Python 3)
- **Database**: SQLite
- **Frontend**: HTML, CSS

### How to Run the Project
1. Clone the repository
```
git clone https://github.com/aliciawijaya98/food_order_apps_mysql.git
cd food-ordering-app
```
2. Install dependencies
```
pip install -r requirements.txt
```

3. Initialize the database
```
python init_db.py
```

4. Run the application
```
python app.py
```
5. Access the application
Open your browser and navigate to: `http://127.0.0.1:5000`

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

### License
This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
