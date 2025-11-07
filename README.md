# 🗳️ Online Voting System with Facial Recognition

This project is a **secure and intelligent online voting platform** that uses **facial recognition** to verify voters before they can cast their vote.  
It ensures authenticity, eliminates duplicate voting, and promotes transparency in the election process.

---

## 🚀 Features

- 🧍‍♀️ **Facial Recognition** for voter authentication using OpenCV.
- 🧾 **Voter Registration & Login** with image capture and validation.
- 🗳️ **Online Voting Interface** with real-time vote count updates.
- 🔒 **Secure Database** using Django ORM for data storage.
- 🧠 **Admin Panel** to manage voters, candidates, and results.
- 📸 Captures user image during verification.
- ⚙️ Built and tested using **PyCharm IDE**.

---

## 🛠️ Technologies Used

| Component | Technology |
|------------|-------------|
| **Backend** | Python, Django |
| **Frontend** | HTML, CSS, Bootstrap |
| **Database** | SQLite3 |
| **Facial Recognition** | OpenCV |
| **IDE** | PyCharm |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Deepanv98/Online-Voting-System-with-Facial-Recognition.git

###2️⃣ Navigate into the Project
cd Online-Voting-System-with-Facial-Recognition

### 3️⃣ Create a Virtual Environment
python -m venv venv
venv\Scripts\activate   # On Windows

### 4️⃣ Install Dependencies
pip install -r requirements.txt

### 5️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate

### 6️⃣ Start the Server
python manage.py runserver


Now visit http://127.0.0.1:8000 to view the app.

#🧑‍💻 Project Structure
Online-Voting-System-with-Facial-Recognition/
├── manage.py
├── voting_app/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── static/
├── media/
└── README.md

📷 Facial Recognition Overview

The system uses OpenCV’s face recognition module to:

Capture the voter’s face via webcam.

Match it with the registered face dataset.

Allow the vote only if the match is successful.

🧠 Future Enhancements

Integration with government ID verification (e.g., Aadhaar).

Cloud-based deployment.

Multi-factor authentication for extra security.

Real-time analytics dashboard.

👩‍💻 Developed By

Deepa Velayudhan
Python | Django | ML | HTML | CSS
📧 deepanv98@gmail.com

⭐ If you like this project, don’t forget to star the repository on GitHub!
