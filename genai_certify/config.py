# Configuration file for CertifyAI-Pro
# Edit this file with your Google OAuth credentials

# Google OAuth Configuration
GOOGLE_CLIENT_ID = 'your-google-client-id-here'
GOOGLE_CLIENT_SECRET = 'your-google-client-secret-here'

# Application Settings
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Database
DATABASE = 'genai_certify.db'

# Certificate Settings
CERTIFICATE_PASSING_SCORE = 0.6  # 60% to pass
NUMBER_OF_QUESTIONS = 15
EASY_QUESTION_COUNT = 12
HARD_QUESTION_COUNT = 3