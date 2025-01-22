# import streamlit as st
# import whisper
# import google.generativeai as genai
# import tempfile
# import os
# from datetime import datetime
# import bcrypt
# from pymongo import MongoClient
# from bson import ObjectId
# from pydub import AudioSegment
# import imageio_ffmpeg as ffmpeg  # Ensure you have this library installed

# # Set FFmpeg converter path dynamically
# AudioSegment.converter = ffmpeg.get_ffmpeg_exe()

# # Configuration
# GEMINI_API_KEY = "AIzaSyCprBIhOYESVA_m2HPawpwiR-oi-zshnT0"
# MONGODB_URI =  "mongodb+srv://vikramaditya1533:Jyoadi2484@psych.cyhtk.mongodb.net/?retryWrites=true&w=majority&appName=Psych" 
# genai.configure(api_key=GEMINI_API_KEY)

# # MongoDB Connection
# client = MongoClient(MONGODB_URI)
# db = client['psychology_platform']
# users_collection = db['users']
# patients_collection = db['patients']



# class UserAuth:
#     @staticmethod
#     def hash_password(password):
#         return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
#     @staticmethod
#     def verify_password(password, hashed_password):
#         return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
#     @staticmethod
#     def register_user(username, email, password):
#         if users_collection.find_one({'email': email}):
#             return False, "Email already registered"
        
#         hashed_password = UserAuth.hash_password(password)
#         user = {
#             'username': username,
#             'email': email,
#             'password': hashed_password,
#             'created_at': datetime.now()
#         }
#         users_collection.insert_one(user)
#         return True, "Registration successful"
    
#     @staticmethod
#     def login_user(email, password):
#         user = users_collection.find_one({'email': email})
#         if not user:
#             return False, "User not found"
        
#         if UserAuth.verify_password(password, user['password']):
#             return True, user
#         return False, "Incorrect password"

# class PsychologicalAnalyzer:
#     def __init__(self):
#         # Load Whisper model
#         st.write("Loading Whisper model... (This might take a moment)")
#         self.whisper_model = whisper.load_model("base")
#         self.gemini_model = genai.GenerativeModel('gemini-pro')

#     def transcribe_audio(self, audio_path):
#         """Transcribe audio using Whisper"""
#         st.write("Transcribing audio...")
#         result = self.whisper_model.transcribe(audio_path)
#         return result['text']

#     def generate_structured_transcript(self, transcript):
#         """Generate a structured transcript with identified speakers"""
#         prompt = f"""Analyze the following transcript and restructure it by identifying distinct speakers. 
#         Assign clear labels like 'Therapist' and 'Patient' or 'Person 1' and 'Person 2'. 
#         Format the transcript to clearly show who is speaking:

#         Original Transcript:
#         {transcript}

#         Please provide a reformatted transcript with clear speaker identification."""

#         response = self.gemini_model.generate_content(prompt)
#         return response.candidates[0].content.parts[0].text

#     def generate_patient_insights(self, transcript):
#         """Generate psychological insights about the patient"""
#         prompt = f"""Conduct a detailed psychological analysis of the patient based on this conversation. 
#         Provide insights including:
#         1. Emotional state
#         2. Potential psychological challenges
#         3. Underlying concerns or stressors
#         4. Nonverbal cues (if discernible from the text)
#         5. Preliminary psychological assessment

#         Conversation Transcript:
#         {transcript}"""

#         response = self.gemini_model.generate_content(prompt)
#         return response.candidates[0].content.parts[0].text

#     def generate_follow_up_questions(self, transcript):
#         """Generate therapeutic follow-up questions"""
#         prompt = f"""Based on the following conversation, generate a list of sensitive, 
#         empathetic, and constructive follow-up questions a therapist might ask to 
#         help the patient explore their feelings and challenges more deeply:

#         Conversation Transcript:
#         {transcript}

#         Please provide:
#         1. 5-7 open-ended questions
#         2. Brief rationale for each question
#         3. Approach to asking these questions with empathy"""

#         response = self.gemini_model.generate_content(prompt)
#         return response.candidates[0].content.parts[0].text

# def initialize_session_state():
#     for key in ['logged_in', 'user', 'current_page', 'analysis_results']:
#         if key not in st.session_state:
#             st.session_state[key] = None
#     st.session_state.analysis_results = {
#         'transcript': None,
#         'insights': None,
#         'follow_up': None
#     }

# def auth_page():
#     st.title("Welcome to Psychological Analysis Platform")
    
#     tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
#     with tab1:
#         st.header("Login")
#         with st.form("login_form"):
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             submit_login = st.form_submit_button("Login")
            
#             if submit_login:
#                 success, result = UserAuth.login_user(email, password)
#                 if success:
#                     set_session_user(result)
#                     st.success("Login successful!")
#                     st.rerun()
#                 else:
#                     st.error(result)
    
#     with tab2:
#         st.header("Sign Up")
#         with st.form("signup_form"):
#             username = st.text_input("Username")
#             email = st.text_input("Email", key="signup_email")
#             password = st.text_input("Password", type="password", key="signup_password")
#             confirm_password = st.text_input("Confirm Password", type="password")
#             submit_signup = st.form_submit_button("Sign Up")
            
#             if submit_signup:
#                 if password != confirm_password:
#                     st.error("Passwords do not match")
#                 else:
#                     success, message = UserAuth.register_user(username, email, password)
#                     if success:
#                         # Auto login after signup
#                         login_success, user = UserAuth.login_user(email, password)
#                         if login_success:
#                             set_session_user(user)
#                             st.success("Registration and login successful!")
#                             st.rerun()
#                     else:
#                         st.error(message)

# def set_session_user(user):
#     st.session_state.logged_in = True
#     st.session_state.user = user
#     st.session_state.current_page = 'welcome'
    
#     st.query_params['logged_in'] = 'true'
#     st.query_params['user_id'] = str(user['_id'])
# def patient_registration():
#     """Modified patient registration to work with MongoDB"""
#     st.header("🩺 Patient Registration")
    
#     with st.form("patient_registration_form"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             patient_name = st.text_input("Patient Full Name")
#             age = st.number_input("Age", min_value=0, max_value=120)
        
#         with col2:
#             gender = st.selectbox("Gender", 
#                                 ["Select", "Male", "Female", "Non-Binary", "Prefer Not to Say"])
        
#         submitted = st.form_submit_button("Register Patient")
    
#     if submitted:
#         if not patient_name or gender == "Select":
#             st.error("Please fill in all required fields")
#         else:
#             patient = {
#                 'name': patient_name,
#                 'age': age,
#                 'gender': gender,
#                 'therapist_id': st.session_state.user['_id'],
#                 'first_visit_date': datetime.now(),
#                 'sessions': []
#             }
            
#             result = patients_collection.insert_one(patient)
            
#             st.success(f"Patient {patient_name} registered successfully!")
#             st.write(f"Patient ID: {result.inserted_id}")
            
#             return patient

#     return None




# def welcome_page():
#     """Welcome page after successful login"""
#     st.title(f"Welcome, {st.session_state.user['username']}! 👋")
#     st.write("What would you like to do today?")
    
#     return st.radio(
#         "Choose an option:",
#         ["New Patient Registration", "Access Existing Patient Records"]
#     )

# def patient_dashboard(patient):
#     st.title(f"Patient Dashboard - {patient['name']}")
    
#     # Navigation
#     col1, col2 = st.columns([1, 5])
#     with col1:
#         if st.button("← Back to Welcome"):
#             st.session_state.current_page = 'welcome'
#             st.rerun()
    
#     # Display patient information
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("Patient Information")
#         st.write(f"Age: {patient['age']}")
#         st.write(f"Gender: {patient['gender']}")
#         st.write(f"First Visit: {patient['first_visit_date'].strftime('%Y-%m-%d')}")
    
#     with col2:
#         st.subheader("Quick Actions")
#         start_new_session = st.button("Start New Session")
    
#     # Display session history
#     st.subheader("Session History")
#     if 'sessions' in patient and patient['sessions']:
#         for idx, session in enumerate(reversed(patient['sessions']), 1):
#             with st.expander(f"Session {len(patient['sessions']) - idx + 1} - {session['date'].strftime('%Y-%m-%d')}"):
#                 tab1, tab2, tab3 = st.tabs(["Transcript", "Insights", "Follow-up"])
                
#                 with tab1:
#                     st.write(session['transcript'])
                
#                 with tab2:
#                     st.write(session['insights'])
                
#                 with tab3:
#                     st.write(session['follow_up_questions'])
#     else:
#         st.info("No previous sessions recorded")
    
#     return start_new_session


# def new_session_page(patient):
#     st.title(f"New Session - {patient['name']}")
    
#     # Navigation
#     col1, col2 = st.columns([1, 5])
#     with col1:
#         if st.button("← Back to Dashboard"):
#             st.session_state.current_page = 'patient_dashboard'
#             st.rerun()
    
#     # Initialize analyzer
#     analyzer = PsychologicalAnalyzer()
    
#     # Audio upload
#     audio_file = st.file_uploader("Upload Session Recording", type=['wav', 'mp3', 'm4a'])
    
#     if audio_file:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
#             tmp_file.write(audio_file.getvalue())
#             audio_path = tmp_file.name
        
#         try:
#             # Process audio in tabs
#             tab1, tab2, tab3 = st.tabs(["Transcript", "Insights", "Follow-up Questions"])
            
#             with st.spinner("Processing audio..."):
#                 # Tab 1: Transcripts
#                 with tab1:
#                     transcript = analyzer.transcribe_audio(audio_path)
#                     structured_transcript = analyzer.generate_structured_transcript(transcript)
#                     st.subheader("Raw Transcript")
#                     st.write(transcript)
#                     st.subheader("Structured Transcript")
#                     st.write(structured_transcript)
#                     st.session_state.analysis_results['transcript'] = structured_transcript
                
#                 # Tab 2: Insights
#                 with tab2:
#                     insights = analyzer.generate_patient_insights(structured_transcript)
#                     st.subheader("Psychological Insights")
#                     st.write(insights)
#                     st.session_state.analysis_results['insights'] = insights
                
#                 # Tab 3: Follow-up
#                 with tab3:
#                     follow_up = analyzer.generate_follow_up_questions(structured_transcript)
#                     st.subheader("Recommended Follow-up Questions")
#                     st.write(follow_up)
#                     st.session_state.analysis_results['follow_up'] = follow_up
            
#             # Save button
#             if st.button("Save Session"):
#                 session_data = {
#                     'date': datetime.now(),
#                     'transcript': st.session_state.analysis_results['transcript'],
#                     'insights': st.session_state.analysis_results['insights'],
#                     'follow_up_questions': st.session_state.analysis_results['follow_up']
#                 }
#                 save_session(patient['_id'], session_data)
#                 st.success("Session saved successfully!")
        
#         except Exception as e:
#             st.error(f"Error processing audio: {str(e)}")
        
#         finally:
#             os.unlink(audio_path)


# def get_patient_list():
#     """Get list of patients for the logged-in therapist"""
#     return list(patients_collection.find({'therapist_id': st.session_state.user['_id']}))

# def save_session(patient_id, session_data):
#     """Save session data to MongoDB"""
#     patients_collection.update_one(
#         {'_id': ObjectId(patient_id)},
#         {'$push': {'sessions': session_data}}
#     )

# def main():
#     initialize_session_state()
    
#     # Check for existing session
#     params = st.query_params
#     if not st.session_state.logged_in and 'logged_in' in params:
#         user_id = params.get('user_id')
#         if user_id and len(user_id) == 24:  # Validate ObjectId length
#             try:
#                 user = users_collection.find_one({'_id': ObjectId(user_id)})
#                 if user:
#                     set_session_user(user)
#             except Exception:
#                 st.query_params.clear()
    
#     if not st.session_state.logged_in:
#         auth_page()
#         return
    
#     # Application flow
#     if st.session_state.current_page == 'welcome':
#         registration_choice = welcome_page()
        
#         if registration_choice == "New Patient Registration":
#             new_patient = patient_registration()
#             if new_patient:
#                 st.session_state.current_patient = new_patient
#                 st.session_state.current_page = 'patient_dashboard'
#                 st.rerun()
#         else:
#             st.subheader("Select a Patient")
#             patients = get_patient_list()
#             patient_names = [p['name'] for p in patients]
            
#             if patient_names:
#                 selected_patient_name = st.selectbox("Choose Patient", patient_names)
#                 if selected_patient_name:
#                     selected_patient = next(p for p in patients if p['name'] == selected_patient_name)
#                     st.session_state.current_patient = selected_patient
#                     st.session_state.current_page = 'patient_dashboard'
#                     st.rerun()
#             else:
#                 st.info("No patients registered yet")
    
#     elif st.session_state.current_page == 'patient_dashboard':
#         start_new_session = patient_dashboard(st.session_state.current_patient)
#         if start_new_session:
#             st.session_state.current_page = 'new_session'
#             st.rerun()
    
#     elif st.session_state.current_page == 'new_session':
#         new_session_page(st.session_state.current_patient)
    
#     # Logout button in sidebar
#     if st.sidebar.button("Logout"):
#         for key in st.session_state.keys():
#             del st.session_state[key]
#         st.query_params.clear()
#         st.rerun()

# if __name__ == "__main__":
#     main()




import streamlit as st
import whisper
import google.generativeai as genai
import tempfile
import os
from datetime import datetime
import bcrypt
from pymongo import MongoClient
from bson import ObjectId
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg

# Set FFmpeg converter path dynamically
AudioSegment.converter = ffmpeg.get_ffmpeg_exe()

# Configuration
GEMINI_API_KEY = "AIzaSyCprBIhOYESVA_m2HPawpwiR-oi-zshnT0"
MONGODB_URI = "mongodb+srv://vikramaditya1533:Jyoadi2484@psych.cyhtk.mongodb.net/?retryWrites=true&w=majority&appName=Psych"
genai.configure(api_key=GEMINI_API_KEY)

# MongoDB Connection
client = MongoClient(MONGODB_URI)
db = client['psychology_platform']
users_collection = db['users']
patients_collection = db['patients']

# Custom CSS
st.markdown("""
<style>
    div.stForm {
        background-color: white;
        padding: 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    .stButton button {
        width: 100%;
        border-radius: 0.25rem;
        height: 2.5rem;
        background-color: #1e88e5;
        color: white;
        border: none;
        font-weight: 500;
    }
    
    .nav-button button {
        background-color: #f8f9fa;
        color: #2c3e50;
        border: 1px solid #dee2e6;
    }
    
    div.stAlert {
        border-radius: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding-top: 10px;
        border-radius: 4px 4px 0 0;
    }
    
    div.stTextInput input,
    div.stSelectbox select {
        border-radius: 0.25rem;
    }
    
    div.stSuccess, div.stError {
        padding: 1rem;
        border-radius: 0.25rem;
    }
    
    .custom-metric {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e88e5;
    }
    
    .metric-label {
        color: #6c757d;
        margin-top: 0.5rem;
    }
    
    .patient-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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
        with st.spinner("Loading Whisper model..."):
            self.whisper_model = whisper.load_model("base")
            self.gemini_model = genai.GenerativeModel('gemini-pro')

    def transcribe_audio(self, audio_path):
        with st.spinner("Transcribing audio..."):
            result = self.whisper_model.transcribe(audio_path)
            return result['text']

    def generate_structured_transcript(self, transcript):
        prompt = f"""Analyze and restructure this transcript identifying speakers as 'Therapist' and 'Patient':
        {transcript}"""
        response = self.gemini_model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text

    def generate_patient_insights(self, transcript):
        prompt = f"""Analyze patient psychology from this conversation, covering:
        - Emotional state
        - Psychological challenges
        - Underlying stressors
        - Nonverbal cues
        - Preliminary assessment
        
        Transcript: {transcript}"""
        response = self.gemini_model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text

    def generate_follow_up_questions(self, transcript):
        prompt = f"""Generate therapeutic follow-up questions based on this conversation:
        {transcript}
        
        Include:
        - 5-7 empathetic questions
        - Rationale for each
        - Approach guidance"""
        response = self.gemini_model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'auth'
    if 'current_patient_id' not in st.session_state:
        st.session_state.current_patient_id = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {
            'transcript': None,
            'insights': None,
            'follow_up': None
        }


def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("PsychNotes")
        st.markdown("##### Mental Health Analysis Platform")
        
        tab1, tab2 = st.tabs(["🔑 Login", "✨ Sign Up"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=True):
                st.markdown("### Welcome Back!")
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Password", type="password")
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("Remember me")
                submit_login = st.form_submit_button("Sign In")
                
                if submit_login:
                    success, result = UserAuth.login_user(email, password)
                    if success:
                        set_session_user(result)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result)
        
        with tab2:
            with st.form("signup_form", clear_on_submit=True):
                st.markdown("### Create Account")
                username = st.text_input("👤 Username")
                email = st.text_input("📧 Email", key="signup_email")
                col1, col2 = st.columns(2)
                with col1:
                    password = st.text_input("🔒 Password", type="password", key="signup_password")
                with col2:
                    confirm_password = st.text_input("🔒 Confirm Password", type="password")
                st.checkbox("I agree to the Terms of Service")
                submit_signup = st.form_submit_button("Create Account")
                
                if submit_signup:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = UserAuth.register_user(username, email, password)
                        if success:
                            login_success, user = UserAuth.login_user(email, password)
                            if login_success:
                                set_session_user(user)
                                st.success("Registration successful!")
                                st.rerun()
                        else:
                            st.error(message)

def set_session_user(user):
    st.session_state.logged_in = True
    st.session_state.user = user
    st.session_state.current_page = 'welcome'
    st.query_params['logged_in'] = 'true'
    st.query_params['user_id'] = str(user['_id'])

def welcome_page():
    # st.markdown("""
    #     <div class="logout-btn">
    #         <button onclick="window.location.href='?logout=true'">
    #             🚪 Logout
    #         </button>
    #     </div>
    # """, unsafe_allow_html=True)
    
    st.title(f"Welcome, {st.session_state.user['username']}!")
    st.markdown("### Quick Actions")
    choice = st.radio(
        "",
        ["➕ New Patient Registration", "📁 Access Patient Records"],
        horizontal=True
    )
    
    if choice == "📁 Access Patient Records":
        patients = list(patients_collection.find({'therapist_id': st.session_state.user['_id']}))
        st.markdown(f"### Patient Records (Total: {len(patients)})")
        
        if patients:
            patient_table = []
            for p in patients:
                session_count = len(p.get('sessions', []))
                last_session = p['sessions'][-1]['date'] if p.get('sessions') else p['first_visit_date']
                patient_table.append({
                    "Name": p['name'],
                    "Age": p['age'],
                    "Gender": p['gender'],
                    "Sessions": session_count,
                    "Last Visit": last_session.strftime('%Y-%m-%d')
                })
            
            st.dataframe(
                patient_table,
                column_config={
                    "Name": st.column_config.TextColumn("Name"),
                    "Age": st.column_config.NumberColumn("Age"),
                    "Gender": st.column_config.TextColumn("Gender"),
                    "Sessions": st.column_config.NumberColumn("Sessions"),
                    "Last Visit": st.column_config.DateColumn("Last Visit"),
                },
                hide_index=True,
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_patient_name = st.selectbox(
                    "Select Patient to View", 
                    options=[p['name'] for p in patients],
                    key='patient_selector'
                )
            
            with col2:
                st.markdown('<div class="view-patient-btn">', unsafe_allow_html=True)
                view_button = st.button("View Patient", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
            if view_button and selected_patient_name:
                selected_patient = patients_collection.find_one({
                    'name': selected_patient_name,
                    'therapist_id': st.session_state.user['_id']
                })
                
                if selected_patient:
                    st.session_state.current_patient_id = str(selected_patient['_id'])
                    st.session_state.current_page = 'patient_dashboard'
                    st.rerun()
        else:
            st.info("No patients registered yet")
    
    return choice

def patient_registration():
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
        <h2 style='margin:0'>🩺 New Patient Registration</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("patient_registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Patient Full Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            contact = st.text_input("Contact Number")
        with col2:
            gender = st.selectbox("Gender", 
                                ["Select", "Male", "Female", "Non-Binary", "Prefer Not to Say"])
            email = st.text_input("Email")
            emergency_contact = st.text_input("Emergency Contact")
        
        medical_history = st.text_area("Medical History")
        notes = st.text_area("Additional Notes")
        
        submitted = st.form_submit_button("Register Patient")
    
        if submitted:
            if not patient_name or gender == "Select":
                st.error("Please fill in all required fields")
            else:
                patient = {
                    'name': patient_name,
                    'age': age,
                    'gender': gender,
                    'contact': contact,
                    'email': email,
                    'emergency_contact': emergency_contact,
                    'medical_history': medical_history,
                    'notes': notes,
                    'therapist_id': st.session_state.user['_id'],
                    'first_visit_date': datetime.now(),
                    'sessions': []
                }
                result = patients_collection.insert_one(patient)
                st.success(f"Patient {patient_name} registered successfully!")
                return patient
    return None

def edit_patient_profile(patient):
    with st.form("edit_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Patient Name", value=patient.get('name', ''))
            age = st.number_input("Age", value=patient.get('age', 0))
            contact = st.text_input("Contact", value=patient.get('contact', ''))
        with col2:
            gender = st.selectbox("Gender", 
                                ["Select", "Male", "Female", "Non-Binary", "Prefer Not to Say"],
                                index=["Select", "Male", "Female", "Non-Binary", "Prefer Not to Say"].index(patient.get('gender', 'Select')))
            email = st.text_input("Email", value=patient.get('email', ''))
            emergency_contact = st.text_input("Emergency Contact", value=patient.get('emergency_contact', ''))
        
        medical_history = st.text_area("Medical History", value=patient.get('medical_history', ''))
        notes = st.text_area("Session Notes", value=patient.get('notes', ''))
        
        if st.form_submit_button("Update Profile"):
            patients_collection.update_one(
                {'_id': patient['_id']},
                {'$set': {
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'contact': contact,
                    'email': email,
                    'emergency_contact': emergency_contact,
                    'medical_history': medical_history,
                    'notes': notes
                }}
            )
            st.success("Profile updated successfully!")
            return True
    return False


def patient_dashboard(patient):
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
        <h2 style='margin:0'>{patient['name']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.current_page = 'welcome'
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["📋 Profile", "📝 Sessions", "📊 Analysis"])
    
    with tab1:
        edit_patient_profile(patient)
    
    with tab2:
        if 'sessions' in patient and patient['sessions']:
            for idx, session in enumerate(reversed(patient['sessions']), 1):
                with st.expander(f"Session {len(patient['sessions']) - idx + 1} - {session['date'].strftime('%Y-%m-%d')}"):
                    tabs = st.tabs(["📝 Transcript", "🔍 Insights", "❓ Follow-up"])
                    with tabs[0]:
                        st.write(session['transcript'])
                    with tabs[1]:
                        st.write(session['insights'])
                    with tabs[2]:
                        st.write(session['follow_up_questions'])
        else:
            st.info("No sessions recorded yet")
    
    with tab3:
        if 'sessions' in patient and patient['sessions']:
            session_dates = [session['date'].strftime('%Y-%m-%d') for session in patient['sessions']]
            selected_date = st.selectbox("Select Session Date", session_dates)
            if selected_date:
                session = next(s for s in patient['sessions'] if s['date'].strftime('%Y-%m-%d') == selected_date)
                
                st.markdown("### Session Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Key Insights")
                    st.write(session['insights'])
                
                with col2:
                    st.markdown("#### Recommended Actions")
                    st.write(session['follow_up_questions'])
        else:
            st.info("No analysis available yet")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎙️ Start New Session", use_container_width=True):
            st.session_state.current_page = 'new_session'
            st.rerun()


def new_session_page(patient):
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
        <h2 style='margin:0'>New Session</h2>
        <p style='color: #6c757d; margin:0'>Patient: {patient['name']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.current_page = 'patient_dashboard'
            st.rerun()
    
    analyzer = PsychologicalAnalyzer()
    audio_file = st.file_uploader("🎙️ Upload Session Recording", type=['wav', 'mp3', 'm4a'])
    
    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
            tmp_file.write(audio_file.getvalue())
            audio_path = tmp_file.name
        
        try:
            progress_bar = st.progress(0)
            st.markdown("### Analysis Progress")
            
            # Process audio first
            with st.spinner("Transcribing audio..."):
                transcript = analyzer.transcribe_audio(audio_path)
                progress_bar.progress(30)
                structured_transcript = analyzer.generate_structured_transcript(transcript)
                progress_bar.progress(50)
                insights = analyzer.generate_patient_insights(structured_transcript)
                progress_bar.progress(75)
                follow_up = analyzer.generate_follow_up_questions(structured_transcript)
                progress_bar.progress(100)
            
            # Then show results
            tabs = st.tabs(["📝 Transcript", "🔍 Insights", "❓ Follow-up Questions"])
            with tabs[0]:
                st.write(structured_transcript)
                st.session_state.analysis_results['transcript'] = structured_transcript
            
            with tabs[1]:
                st.write(insights)
                st.session_state.analysis_results['insights'] = insights
            
            with tabs[2]:
                st.write(follow_up)
                st.session_state.analysis_results['follow_up'] = follow_up
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Session", use_container_width=True):
                    save_session(patient['_id'], {
                        'date': datetime.now(),
                        'transcript': st.session_state.analysis_results['transcript'],
                        'insights': st.session_state.analysis_results['insights'],
                        'follow_up_questions': st.session_state.analysis_results['follow_up']
                    })
                    st.success("Session saved successfully!")
            
            with col2:
                if st.button("🔄 Start New Recording", use_container_width=True):
                    st.session_state.analysis_results = {
                        'transcript': None,
                        'insights': None,
                        'follow_up': None
                    }
                    st.rerun()
        
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
        
        finally:
            os.unlink(audio_path)


def get_patient_list():
    return list(patients_collection.find({'therapist_id': st.session_state.user['_id']}))

def save_session(patient_id, session_data):
    patients_collection.update_one(
        {'_id': ObjectId(patient_id)},
        {'$push': {'sessions': session_data}}
    )

def main():
    initialize_session_state()
    
    # Check for logout
    params = st.query_params
    if params.get('logout'):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.query_params.clear()
        st.rerun()
    
    # Check for existing session
    if not st.session_state.logged_in and 'logged_in' in params:
        user_id = params.get('user_id')
        if user_id and len(user_id) == 24:
            try:
                user = users_collection.find_one({'_id': ObjectId(user_id)})
                if user:
                    set_session_user(user)
            except Exception:
                st.query_params.clear()
    
    if not st.session_state.logged_in:
        auth_page()
        return
    
    if st.session_state.current_page == 'welcome':
        registration_choice = welcome_page()
        
        if registration_choice == "➕ New Patient Registration":
            new_patient = patient_registration()
            if new_patient:
                st.session_state.current_patient_id = str(new_patient['_id'])
                st.session_state.current_page = 'patient_dashboard'
                st.rerun()
                
    elif st.session_state.current_page == 'patient_dashboard':
        if st.session_state.current_patient_id:
            current_patient = patients_collection.find_one(
                {'_id': ObjectId(st.session_state.current_patient_id)}
            )
            if current_patient:
                start_new_session = patient_dashboard(current_patient)
                if start_new_session:
                    st.session_state.current_page = 'new_session'
                    st.rerun()
            else:
                st.error("Patient not found")
                st.session_state.current_page = 'welcome'
                st.rerun()
                
    elif st.session_state.current_page == 'new_session':
        if st.session_state.current_patient_id:
            current_patient = patients_collection.find_one(
                {'_id': ObjectId(st.session_state.current_patient_id)}
            )
            if current_patient:
                new_session_page(current_patient)
            else:
                st.error("Patient not found")
                st.session_state.current_page = 'welcome'
                st.rerun()


if __name__ == "__main__":
    main()