import streamlit as st
import whisper
import google.generativeai as genai
import tempfile
import os
from datetime import datetime
import bcrypt
from pymongo import MongoClient
from bson import ObjectId

# Configuration
GEMINI_API_KEY = "AIzaSyCprBIhOYESVA_m2HPawpwiR-oi-zshnT0"
MONGODB_URI = "mongodb+srv://2023ebcs752:CiMTewlE52HKCjRp@cluster0.bxnxs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB URI
genai.configure(api_key=GEMINI_API_KEY)

# MongoDB Connection
client = MongoClient(MONGODB_URI)
db = client['psychology_platform']
users_collection = db['users']
patients_collection = db['patients']

class UserAuth:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verify_password(password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    @staticmethod
    def register_user(username, email, password):
        if users_collection.find_one({'email': email}):
            return False, "Email already registered"
        
        hashed_password = UserAuth.hash_password(password)
        user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.now()
        }
        users_collection.insert_one(user)
        return True, "Registration successful"
    
    @staticmethod
    def login_user(email, password):
        user = users_collection.find_one({'email': email})
        if not user:
            return False, "User not found"
        
        if UserAuth.verify_password(password, user['password']):
            return True, user
        return False, "Incorrect password"

class PsychologicalAnalyzer:
    def __init__(self):
        # Load Whisper model
        st.write("Loading Whisper model... (This might take a moment)")
        self.whisper_model = whisper.load_model("base")
        self.gemini_model = genai.GenerativeModel('gemini-pro')

    def transcribe_audio(self, audio_path):
        """Transcribe audio using Whisper"""
        st.write("Transcribing audio...")
        result = self.whisper_model.transcribe(audio_path)
        return result['text']

    def generate_structured_transcript(self, transcript):
        """Generate a structured transcript with identified speakers"""
        prompt = f"""Analyze the following transcript and restructure it by identifying distinct speakers. 
        Assign clear labels like 'Therapist' and 'Patient' or 'Person 1' and 'Person 2'. 
        Format the transcript to clearly show who is speaking:

        Original Transcript:
        {transcript}

        Please provide a reformatted transcript with clear speaker identification."""

        response = self.gemini_model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text

    def generate_patient_insights(self, transcript):
        """Generate psychological insights about the patient"""
        prompt = f"""Conduct a detailed psychological analysis of the patient based on this conversation. 
        Provide insights including:
        1. Emotional state
        2. Potential psychological challenges
        3. Underlying concerns or stressors
        4. Nonverbal cues (if discernible from the text)
        5. Preliminary psychological assessment

        Conversation Transcript:
        {transcript}"""

        response = self.gemini_model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text

    def generate_follow_up_questions(self, transcript):
        """Generate therapeutic follow-up questions"""
        prompt = f"""Based on the following conversation, generate a list of sensitive, 
        empathetic, and constructive follow-up questions a therapist might ask to 
        help the patient explore their feelings and challenges more deeply:

        Conversation Transcript:
        {transcript}

        Please provide:
        1. 5-7 open-ended questions
        2. Brief rationale for each question
        3. Approach to asking these questions with empathy"""

        response = self.gemini_model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text

def initialize_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'auth'

def auth_page():
    """Authentication page with login and signup options"""
    st.title("Welcome to Psychological Analysis Platform")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                success, result = UserAuth.login_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = result
                    st.session_state.current_page = 'welcome'
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error(result)
    
    with tab2:
        st.header("Sign Up")
        with st.form("signup_form"):
            username = st.text_input("Username")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_signup = st.form_submit_button("Sign Up")
            
            if submit_signup:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = UserAuth.register_user(username, email, password)
                    if success:
                        st.success(message)
                        st.info("Please login with your credentials")
                    else:
                        st.error(message)

def patient_registration():
    """Modified patient registration to work with MongoDB"""
    st.header("🩺 Patient Registration")
    
    with st.form("patient_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Full Name")
            age = st.number_input("Age", min_value=0, max_value=120)
        
        with col2:
            gender = st.selectbox("Gender", 
                                ["Select", "Male", "Female", "Non-Binary", "Prefer Not to Say"])
        
        submitted = st.form_submit_button("Register Patient")
    
    if submitted:
        if not patient_name or gender == "Select":
            st.error("Please fill in all required fields")
        else:
            patient = {
                'name': patient_name,
                'age': age,
                'gender': gender,
                'therapist_id': st.session_state.user['_id'],
                'first_visit_date': datetime.now(),
                'sessions': []
            }
            
            result = patients_collection.insert_one(patient)
            
            st.success(f"Patient {patient_name} registered successfully!")
            st.write(f"Patient ID: {result.inserted_id}")
            
            return patient

    return None

def get_patient_list():
    """Get list of patients for the logged-in therapist"""
    return list(patients_collection.find({'therapist_id': st.session_state.user['_id']}))

def save_session(patient_id, session_data):
    """Save session data to MongoDB"""
    patients_collection.update_one(
        {'_id': ObjectId(patient_id)},
        {'$push': {'sessions': session_data}}
    )

def main():
    initialize_session_state()
    
    if not st.session_state.logged_in:
        auth_page()
        return
    
    # Rest of the application flow
    if st.session_state.current_page == 'welcome':
        registration_choice = welcome_page()
        
        if registration_choice == "New Patient Registration":
            new_patient = patient_registration()
            if new_patient:
                st.session_state.current_patient = new_patient
                st.session_state.current_page = 'patient_dashboard'
                st.experimental_rerun()
        else:
            st.subheader("Select a Patient")
            patients = get_patient_list()
            patient_names = [p['name'] for p in patients]
            
            if patient_names:
                selected_patient_name = st.selectbox("Choose Patient", patient_names)
                if selected_patient_name:
                    selected_patient = next(p for p in patients if p['name'] == selected_patient_name)
                    st.session_state.current_patient = selected_patient
                    st.session_state.current_page = 'patient_dashboard'
                    st.experimental_rerun()
            else:
                st.info("No patients registered yet")
    
    elif st.session_state.current_page == 'patient_dashboard':
        start_new_session = patient_dashboard(st.session_state.current_patient)
        if start_new_session:
            st.session_state.current_page = 'new_session'
            st.experimental_rerun()
    
    elif st.session_state.current_page == 'new_session':
        new_session_page(st.session_state.current_patient)
    
    # Add logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.current_page = 'auth'
        st.experimental_rerun()

if __name__ == "__main__":
    main()