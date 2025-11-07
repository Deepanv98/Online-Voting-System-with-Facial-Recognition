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
from django.shortcuts import redirect
import cv2
import os
from django.http import JsonResponse
from admin_panel.models import *
import numpy as np
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count


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
                user = authenticate(username=email, password=pass1)
                login(request, user)
                return redirect(capture_and_train_page)
        else:
            messages.warning(request,"Password Mismatch!!")
            messages.warning(request,"Password Mismatch!!")
    return render(request, 'register.html')


def capture_and_train_page(request):
    """
    Render the HTML page for capturing and training.
    """
    return render(request, "capture_faces.html")

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


# Ensure the dataset directory exists
dataset_path = os.path.join(settings.BASE_DIR, 'dataset')
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

@csrf_exempt
def capture_face(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'User ID not provided.'})

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)

        count = 0
        while count < 50:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                count += 1
                face = gray[y:y+h, x:x+w]
                cv2.imwrite(f"{dataset_path}/User.{user_id}.{count}.jpg", face)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            cv2.imshow('Capturing Faces', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return JsonResponse({'status': 'success', 'message': f'Captured {count} face samples for User ID: {user_id}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def train_model(request):
    if request.method == 'POST':
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        image_paths = [os.path.join(dataset_path, f) for f in os.listdir(dataset_path)]
        face_samples = []
        ids = []

        for image_path in image_paths:
            gray_image = Image.open(image_path).convert('L')
            image_np = np.array(gray_image, 'uint8')
            user_id = int(os.path.split(image_path)[-1].split('.')[1])
            faces = face_cascade.detectMultiScale(image_np)

            for (x, y, w, h) in faces:
                face_samples.append(image_np[y:y+h, x:x+w])
                ids.append(user_id)

        recognizer.train(face_samples, np.array(ids))
        recognizer.write(os.path.join(settings.BASE_DIR, 'trainer.yml'))
        return JsonResponse({'status': 'success', 'message': "Training completed and model saved.", 'redirect_url': '/'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def face_recognition_view(request):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer.yml')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)
    face_recognized = False  # Flag to check if a face is recognized

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            user_id, confidence = recognizer.predict(face)

            if confidence < 50 and request.user.id == int(user_id):  # Adjust threshold as needed
                text = f"User ID: {user_id} ({100 - confidence:.2f}%)"
                color = (0, 255, 0)
                face_recognized = True
                return redirect(vote, user_id=user_id)
            else:
                text = "Unknown"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow('Recognizing Faces', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Redirect to the home page if no face was recognized
    if not face_recognized:
        return redirect('home')  # Replace 'home' with the name of your home page URL pattern


def vote(request, user_id):
    voter_id = request.user.id  # Assuming the voter is logged in

    # Check if the user has already voted
    has_voted = VotingResult.objects.filter(voter_id=voter_id).exists()

    if request.method == 'POST' and not has_voted:
        candidate_id = request.POST.get('candidate_id')
        # Save the vote
        VotingResult.objects.create(candidate_id=candidate_id, voter_id=voter_id)
        messages.success(request, "Your vote has been recorded!")
        has_voted = True  # Update the flag after voting

    # Fetch all candidates from the Candidate table
    candidates = Candidate.objects.all()
    context = {'candidates': candidates, 'has_voted': has_voted}
    return render(request, 'vote.html', context)


def election_results(request):
    # Annotate each candidate with their vote count
    candidates = Candidate.objects.annotate(vote_count=Count('votingresult')).order_by('-vote_count')
    context = {'candidates': candidates}
    return render(request, 'election_results.html', context)


def signout(request):
    logout(request)
    return redirect(home)