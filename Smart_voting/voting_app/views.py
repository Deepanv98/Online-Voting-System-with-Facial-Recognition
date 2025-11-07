from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserData
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout, authenticate
import random
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta  # Use Python's built-in datetime module
from django.contrib.auth.decorators import login_required
import cv2
import os
from django.http import JsonResponse
from admin_panel.models import *
# Create your views here.

def home(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        fname=request.POST.get("fname")
        lname=request.POST.get("lname")
        dob=request.POST.get("dob")
        gender=request.POST.get("gender")
        email=request.POST.get("email")
        mob=request.POST.get("mob")
        add1=request.POST.get("add1")
        add2=request.POST.get("add2")
        city=request.POST.get("city")
        state=request.POST.get("state")
        pcode=request.POST.get("pcode")
        pass1=request.POST.get("pass1")
        pass2=request.POST.get("pass2")
        if pass1==pass2:
            if User.objects.filter(email=email).exists():
                messages.warning(request,"Email Exists!")
            elif UserData.objects.filter(phone=mob).exists():
                messages.warning(request,"Mobile Number Exists!")
            else:
                user = User.objects.create(first_name=fname, last_name=lname, email=email, username=email, password=make_password(pass1))
                userdata = UserData.objects.create(user=user, phone=mob, dob=dob, gender=gender, address1=add1, address2=add2, city=city, state=state,postcode=pcode)
                user.save()
                userdata.save()
                messages.success(request, "User registered successfully!")
                return redirect(signin)
        else:
            messages.warning(request,"Password Mismatch!!")
    return render(request, 'register.html')


import cv2
import os
from django.http import JsonResponse
from django.shortcuts import render

# Define paths for storing face data and model
FACE_DATA_DIR = "face_data"
MODEL_DIR = "models"
os.makedirs(FACE_DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def face_capture(request):
    """
    Capture faces and save to a directory.
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id", "default_user")
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        cap = cv2.VideoCapture(0)  # Open the webcam

        if not cap.isOpened():
            return JsonResponse({"status": "error", "message": "Camera not accessible"})

        face_dir = os.path.join(FACE_DATA_DIR, user_id)
        os.makedirs(face_dir, exist_ok=True)
        count = 0

        while count < 30:  # Capture 50 face images
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                count += 1
                face_img = gray[y:y + h, x:x + w]
                file_path = os.path.join(face_dir, f"{user_id}_{count}.jpg")
                cv2.imwrite(file_path, face_img)

            if count >= 30:
                break

        cap.release()
        return JsonResponse({"status": "success", "message": f"Captured 30 face images for {user_id}"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})


def train_model(request):
    """
    Train the face recognition model using collected data.
    """
    if request.method == "POST":
        try:
            from sklearn.neighbors import KNeighborsClassifier
            import numpy as np
            import pickle

            # Load the face data
            faces = []
            labels = []
            label_map = {}
            current_label = 0

            for user_dir in os.listdir(FACE_DATA_DIR):
                user_path = os.path.join(FACE_DATA_DIR, user_dir)
                for img_name in os.listdir(user_path):
                    img_path = os.path.join(user_path, img_name)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    faces.append(img.flatten())
                    labels.append(current_label)

                label_map[current_label] = user_dir
                current_label += 1

            # Train KNN classifier
            knn = KNeighborsClassifier(n_neighbors=5)
            knn.fit(faces, labels)

            # Save the model
            model_path = os.path.join(MODEL_DIR, "face_recognition_model.pkl")
            with open(model_path, "wb") as f:
                pickle.dump({"model": knn, "label_map": label_map}, f)

            return JsonResponse({"status": "success", "message": "Model trained successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Training failed: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request method"})


def capture_and_train_page(request):
    """
    Render the HTML page for capturing and training.
    """
    return render(request, "capture_and_train.html")


def signin(request):
    if request.method == "POST":
        username=request.POST.get('email')
        password=request.POST.get('password')
        print(username, password)
        user = authenticate(username=username,password=password)
        print(user)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect(home)
        else:
            messages.warning(request,"Invalid Credentials!")
    return render(request, 'login.html')


def generate_otp():
    """Generates a 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    """Sends the OTP to the given email address"""
    subject = "Your OTP for Verification"
    message = f"Your One-Time Password (OTP) is: {otp}\n\nThis OTP is valid for 5 minutes."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


def reset(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            otp = generate_otp()  # Generate a 6-digit OTP

            # Save the OTP, email, and timestamp in the session
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['otp_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Store timestamp

            try:
                send_otp_email(email, otp)  # Send OTP to the email
                messages.success(request, "OTP has been sent to your email address!")
                return redirect(change_password)
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
        else:
            messages.error(request, "Email address does not exist!.")

    return render(request, 'forgot.html')



def change_password(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        email = request.session.get('email')
        otp_timestamp_str = request.session.get('otp_timestamp')
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")

        # Check OTP expiration (5 minutes)
        if otp_timestamp_str:
            otp_timestamp = datetime.strptime(otp_timestamp_str, '%Y-%m-%d %H:%M:%S')
            if datetime.now() > otp_timestamp + timedelta(minutes=5):
                messages.error(request, "The OTP has expired. Please request a new one.")
                return render(request, 'reset.html')

        # Validate OTP and password match
        if entered_otp == session_otp:
            if pass1 == pass2:
                try:
                    # Find the user by email
                    user = User.objects.get(email=email)
                    user.set_password(pass1)  # Set the new password securely
                    user.save()

                    # Clear session variables after successful password reset
                    del request.session['otp']
                    del request.session['email']
                    del request.session['otp_timestamp']

                    messages.success(request, "Your password has been reset successfully!")
                    return redirect(signin)  # Redirect to home page or login page
                except User.DoesNotExist:
                    messages.error(request, "No user found with the provided email.")
            else:
                messages.error(request, "Passwords do not match. Please try again.")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'reset.html')


def vote(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        voter_id = request.user.id  # Assuming the voter is logged in and `request.user` has the voter details

        # Prevent duplicate voting
        if VotingResult.objects.filter(voter_id=voter_id).exists():
            messages.error(request, "You have already voted!")
            return redirect('vote')

        # Save the vote
        VotingResult.objects.create(candidate_id=candidate_id, voter_id=voter_id)
        messages.success(request, "Your vote has been recorded!")
        return redirect('vote')

    # Fetch all candidates from the Candidate table
    candidates = Candidate.objects.all()
    context = {'candidates': candidates}
    return render(request, 'vote.html', context)


def signout(request):
    logout(request)
    return redirect(home)