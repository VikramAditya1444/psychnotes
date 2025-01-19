import streamlit as st
import whisper
import google.generativeai as genai
import tempfile
import os
from datetime import datetime

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyCprBIhOYESVA_m2HPawpwiR-oi-zshnT0"
genai.configure(api_key=GEMINI_API_KEY)

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
    """Initialize session state variables if they don't exist"""
    if 'patients' not in st.session_state:
        st.session_state.patients = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'welcome'

def welcome_page():
    """Initial welcome page for the application"""
    st.title("Psychological Analysis Platform")
    
    # Animated welcome message
    st.markdown("""
    <div style='text-align: center; padding: 20px; background-color: #f0f6fc; border-radius: 10px;'>
        <h2>Hii Sarsosha 🌟</h2>
        <p>Your Compassionate Psychological Analysis Companion</p>
    </div>
    """, unsafe_allow_html=True)

    # Registration or Login Choice
    page = st.radio("Choose an Option", 
                    ["New Patient Registration", "Existing Patient Dashboard"])
    
    return page

def patient_registration():
    """Patient registration page"""
    st.header("🩺 Patient Registration")
    
    # Create form for patient details
    with st.form("patient_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Full Name")
            age = st.number_input("Age", min_value=0, max_value=120)
        
        with col2:
            gender = st.selectbox("Gender", 
                                  ["Select", "Male", "Female", "Non-Binary", "Prefer Not to Say"])
        
        submitted = st.form_submit_button("Register Patient")
    
    # Handle form submission
    if submitted:
        if not patient_name or gender == "Select":
            st.error("Please fill in all required fields")
        else:
            # Create patient dictionary
            patient = {
                'id': len(st.session_state.patients) + 1,
                'name': patient_name,
                'age': age,
                'gender': gender,
                'first_visit_date': datetime.now().strftime("%Y-%m-%d"),
                'sessions': []
            }
            
            # Add patient to session state
            st.session_state.patients.append(patient)
            
            st.success(f"Patient {patient_name} registered successfully!")
            st.write(f"Patient ID: {patient['id']}")
            
            return patient

    return None

def patient_dashboard(patient):
    """Comprehensive patient dashboard"""
    # Dashboard Layout
    st.title(f"🩺 Patient Dashboard - {patient['name']}")
    
    # Patient Information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Patient ID", patient['id'])
    with col2:
        st.metric("Age", patient['age'])
    with col3:
        st.metric("Gender", patient['gender'])
    
    # Session History
    st.subheader("📋 Session History")
    
    if not patient['sessions']:
        st.info("No previous sessions recorded")
    else:
        for session in patient['sessions']:
            with st.expander(f"Session on {session['date']}"):
                st.write("**Transcript:**")
                st.text_area("Transcript", session['transcript'], height=200)
                
                st.write("**Structured Transcript:**")
                st.text_area("Structured Transcript", session['structured_transcript'], height=200)
                
                st.write("**Patient Insights:**")
                st.write(session['patient_insights'])
                
                st.write("**Follow-up Questions:**")
                st.write(session['follow_up_questions'])
    
    # New Session Button
    if st.button("Start New Session"):
        return True
    return False

def new_session_page(patient):
    """Page for starting a new therapy session"""
    analyzer = PsychologicalAnalyzer()
    
    st.title("🎙️ New Therapy Session")
    
    # Audio uploader
    uploaded_file = st.file_uploader("📁 Upload Audio File", type=['wav', 'mp3', 'ogg', 'mp4'])
    
    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # Transcribe
        with st.spinner('Transcribing audio...'):
            transcript = analyzer.transcribe_audio(tmp_file_path)

        # Create tabs for different features
        tab1, tab2, tab3, tab4 = st.tabs([
            "📄 Original Transcript", 
            "🔍 Structured Transcript", 
            "🧩 Patient Insights", 
            "❓ Therapeutic Questions"
        ])

        with tab1:
            st.subheader("Original Transcript")
            st.text_area("Full Transcript", transcript, height=300)

        structured_transcript = ""
        patient_insights = ""
        follow_up_questions = ""

        with tab2:
            st.subheader("Structured Transcript")
            with st.spinner('Generating structured transcript...'):
                structured_transcript = analyzer.generate_structured_transcript(transcript)
            st.text_area("Transcript with Speaker Identification", structured_transcript, height=300)

        with tab3:
            st.subheader("Patient Psychological Insights")
            with st.spinner('Analyzing patient insights...'):
                patient_insights = analyzer.generate_patient_insights(transcript)
            st.write(patient_insights)

        with tab4:
            st.subheader("Recommended Therapeutic Follow-up Questions")
            with st.spinner('Generating follow-up questions...'):
                follow_up_questions = analyzer.generate_follow_up_questions(transcript)
            st.write(follow_up_questions)

        # Save session
        if st.button("Save Session"):
            # Create session dictionary
            session = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'transcript': transcript,
                'structured_transcript': structured_transcript,
                'patient_insights': patient_insights,
                'follow_up_questions': follow_up_questions
            }
            
            # Find and update the patient in session state
            for p in st.session_state.patients:
                if p['id'] == patient['id']:
                    p['sessions'].append(session)
                    break
            
            st.success("Session saved successfully!")
            
            # Cleanup temporary file
            os.unlink(tmp_file_path)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Main application flow
    if st.session_state.current_page == 'welcome':
        registration_choice = welcome_page()
        
        if registration_choice == "New Patient Registration":
            new_patient = patient_registration()
            if new_patient:
                st.session_state.current_patient = new_patient
                st.session_state.current_page = 'patient_dashboard'
                st.experimental_rerun()
        else:
            # List existing patients
            st.subheader("Select a Patient")
            patient_names = [p['name'] for p in st.session_state.patients]
            selected_patient_name = st.selectbox("Choose Patient", patient_names)
            
            if selected_patient_name:
                selected_patient = next(p for p in st.session_state.patients if p['name'] == selected_patient_name)
                st.session_state.current_patient = selected_patient
                st.session_state.current_page = 'patient_dashboard'
                st.experimental_rerun()
    
    elif st.session_state.current_page == 'patient_dashboard':
        start_new_session = patient_dashboard(st.session_state.current_patient)
        if start_new_session:
            st.session_state.current_page = 'new_session'
            st.experimental_rerun()
    
    elif st.session_state.current_page == 'new_session':
        new_session_page(st.session_state.current_patient)

if __name__ == "__main__":
    main()