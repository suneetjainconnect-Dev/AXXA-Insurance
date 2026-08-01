"""
GenAI & Agentic AI Certification Platform
Professional Certification System with Google OAuth & PDF Certificates
"""

import os
import sqlite3
import random
import secrets
import io
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth

# Configuration
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE = 'genai_certify.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_certificate_number():
    """Generate unique certificate number"""
    return f"CAIP-{secrets.token_hex(6).upper()}"

def save_user_attempt(user_id, score, total_questions):
    """Save user's attempt to history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_attempts (user_id, score, total_questions)
        VALUES (?, ?, ?)
    ''', (user_id, score, total_questions))
    conn.commit()
    conn.close()

def save_certificate(user_id, score, total_questions):
    """Save certificate to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    certificate_number = generate_certificate_number()
    cursor.execute('''
        INSERT INTO certificates (user_id, score, total_questions, certificate_number)
        VALUES (?, ?, ?, ?)
    ''', (user_id, score, total_questions, certificate_number))
    conn.commit()
    cert_id = cursor.lastrowid
    conn.close()
    return cert_id, certificate_number

def get_random_questions(num_questions=15):
    """Get random questions with mixed difficulty"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    questions = []
    
    # Get 12 easy questions
    cursor.execute('SELECT * FROM questions WHERE difficulty = ?', ('easy',))
    easy_questions = cursor.fetchall()
    if len(easy_questions) >= 12:
        questions.extend(random.sample(easy_questions, 12))
    else:
        questions.extend(easy_questions)
    
    # Get 3 medium/hard questions
    cursor.execute('SELECT * FROM questions WHERE difficulty IN (?, ?)', ('medium', 'hard'))
    hard_questions = cursor.fetchall()
    if len(hard_questions) >= 3:
        questions.extend(random.sample(hard_questions, 3))
    else:
        questions.extend(hard_questions)
    
    random.shuffle(questions)
    conn.close()
    return questions[:15]

def get_question_by_id(question_id):
    """Get a specific question by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
    question = cursor.fetchone()
    conn.close()
    return question

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        return user
    return None

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    """Initialize database with questions and tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create certificates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            passed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            certificate_number TEXT UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create user_attempts table for history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_answer INTEGER NOT NULL,
            difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
            category TEXT
        )
    ''')
    
    # Insert 80 questions - 40 easy + 36 medium + 4 hard
    questions = [
        ('What does GENAI stand for?', 'Generative Artificial Intelligence', 'General Artificial Intelligence', 'Global AI Network', 'Generated Algorithms Interface', 1, 'easy', 'basics'),
        ('Which is a Generative AI model?', 'ChatGPT', 'Spam filter', 'Recommendation system', 'Facial recognition', 1, 'easy', 'basics'),
        ('What is the main capability of Generative AI?', 'Classify existing data', 'Generate new content', 'Predict future trends', 'Analyze images', 2, 'easy', 'basics'),
        ('Which company created ChatGPT?', 'Google', 'OpenAI', 'Microsoft', 'Meta', 2, 'easy', 'basics'),
        ('What is a Large Language Model (LLM)?', 'A model with many parameters', 'A database system', 'A programming language', 'A hardware device', 1, 'easy', 'basics'),
        ('Which technique is used in Generative AI?', 'Transformer architecture', 'Linear regression', 'K-means clustering', 'Decision trees', 1, 'easy', 'basics'),
        ('What is prompting in Generative AI?', 'Asking questions to the AI', 'Training a model', 'Debugging code', 'Hardware setup', 1, 'easy', 'basics'),
        ('Which is NOT a Generative AI application?', 'Text summarization', 'Image generation', 'Data classification', 'Code generation', 3, 'easy', 'basics'),
        ('What is AI', 'Artificial Intelligence', 'Automated Interface', 'Advanced Integration', 'Application Intelligence', 1, 'easy', 'basics'),
        ('What is an agent in AI?', 'A software program that acts independently', 'A hardware component', 'A database', 'A programming language', 1, 'easy', 'basics'),
        ('What is natural language processing?', 'AI that understands human language', 'Data storage', 'Image processing', 'Network security', 1, 'easy', 'basics'),
        ('Which is a generative AI image model?', 'Stable Diffusion', 'ResNet', 'VGG16', 'Inception', 1, 'easy', 'basics'),
        ('What does NLP stand for?', 'Natural Language Processing', 'Neural Learning Process', 'Natural Language Program', 'Network Language Protocol', 1, 'easy', 'basics'),
        ('What is machine learning?', 'Computers learning from data', 'Hardware installation', 'Network configuration', 'Database management', 1, 'easy', 'basics'),
        ('Which is a popular AI programming language?', 'Python', 'HTML', 'CSS', 'SQL', 1, 'easy', 'basics'),
        ('What is supervised learning?', 'Learning with labeled data', 'Learning without labels', 'Reinforcement learning', 'Deep learning', 1, 'easy', 'basics'),
        ('What is unsupervised learning?', 'Learning without labeled data', 'Learning with labels', 'Supervised learning', 'Transfer learning', 1, 'easy', 'basics'),
        ('Which is a generative model?', 'GAN', 'SVM', 'Logistic Regression', 'Linear Regression', 1, 'easy', 'basics'),
        ('What is a neural network?', 'Computing system inspired by brain', 'Database network', 'File system', 'Operating system', 1, 'easy', 'basics'),
        ('What is deep learning?', 'Neural networks with many layers', 'Simple ML models', 'Data mining', 'Web development', 1, 'easy', 'basics'),
        ('What is a transformer model?', 'Attention-based neural network', 'Data transformation tool', 'Database model', 'Network protocol', 1, 'medium', 'transformers'),
        ('What is tokenization in NLP?', 'Breaking text into tokens', 'Encryption method', 'Data compression', 'Image processing', 1, 'medium', 'nlp'),
        ('What is fine-tuning in AI?', 'Adapting pre-trained model', 'Hardware calibration', 'Data cleaning', 'Network optimization', 1, 'medium', 'training'),
        ('What is prompt engineering?', 'Designing effective prompts for AI', 'Software engineering', 'Network design', 'Database schema', 1, 'medium', 'basics'),
        ('What is RAG in AI?', 'Retrieval-Augmented Generation', 'Random Access Generation', 'Remote Access Gateway', 'Rapid Application Generation', 1, 'medium', 'advanced'),
        ('What is sentiment analysis?', 'Detecting emotional tone', 'Hardware testing', 'Network analysis', 'Database optimization', 1, 'medium', 'nlp'),
        ('What is text generation?', 'Creating new text content', 'Text storage', 'Text encryption', 'Text compression', 1, 'medium', 'generative'),
        ('What is code generation AI?', 'Creates computer code', 'Debugs code', 'Compiles code', 'Optimizes code', 1, 'medium', 'applications'),
        ('What is an AI agent?', 'AI that perceives and acts on environment', 'Simple AI program', 'Static AI model', 'Database AI', 1, 'easy', 'agentic'),
        ('What defines an AI agent?', 'Autonomy and action-taking', 'Internet connection', 'Cloud storage', 'Network speed', 1, 'easy', 'agentic'),
        ('What is multi-agent system?', 'Multiple AI agents collaborating', 'Single AI agent', 'Hardware agents', 'User agents', 1, 'easy', 'agentic'),
        ('What is agent autonomy?', 'Independent decision-making', 'User control', 'Cloud control', 'Network control', 1, 'easy', 'agentic'),
        ('What is agent reasoning?', 'Decision-making process', 'Hardware calculation', 'Data storage', 'Network routing', 1, 'easy', 'agentic'),
        ('What is tool use in AI agents?', 'Agents using external tools', 'Hardware tools', 'Software tools', 'Network tools', 1, 'medium', 'agentic'),
        ('What is agent planning?', 'Generating action sequences', 'Data planning', 'Network planning', 'Storage planning', 1, 'medium', 'agentic'),
        ('What is agent memory?', 'Agent stores experiences', 'Hardware memory', 'Cloud memory', 'Network memory', 1, 'medium', 'agentic'),
        ('What is agent perception?', 'Agent senses environment', 'Hardware sensing', 'Data sensing', 'Network sensing', 1, 'medium', 'agentic'),
        ('What is agent architecture?', 'Agent system design', 'Hardware design', 'Network design', 'Software design', 1, 'medium', 'agentic'),
        ('What is goal-directed behavior?', 'Actions toward specific goals', 'Random actions', 'Hardware actions', 'Network actions', 1, 'medium', 'agentic'),
        ('What is a hallucination in AI?', 'AI generating false information', 'Hardware glitch', 'Network error', 'Data corruption', 1, 'hard', 'issues'),
        ('What is bias in AI?', 'Systematic errors in AI predictions', 'Hardware bias', 'Network bias', 'Storage bias', 1, 'hard', 'ethics'),
        ('What is explainable AI?', 'AI that explains its decisions', 'Simple AI', 'Cloud AI', 'Mobile AI', 1, 'hard', 'ethics'),
        ('What is federated learning?', 'Distributed machine learning', 'Centralized learning', 'Cloud learning', 'Local learning', 1, 'hard', 'architecture'),
        ('What is differential privacy?', 'Privacy-preserving data analysis', 'Network security', 'Database security', 'File encryption', 1, 'hard', 'privacy'),
        ('What is a generative adversarial network?', 'Two networks competing', 'Single neural network', 'Database system', 'Network protocol', 1, 'hard', 'gans'),
        ('What is transfer learning?', 'Applying knowledge to new tasks', 'Transferring files', 'Moving models', 'Copying data', 1, 'hard', 'learning'),
        ('What is an embedding in NLP?', 'Word representations in vector space', 'Text encoding', 'Data storage', 'Network routing', 1, 'hard', 'nlp'),
        ('What is attention mechanism?', 'Focusing on relevant information', 'Memory recall', 'Data retrieval', 'Storage optimization', 1, 'hard', 'transformers'),
        ('What is BDI architecture?', 'Belief-Desire-Intention', 'Binary-Data-Interface', 'Basic-Device-Integration', 'Best-Data-Index', 1, 'hard', 'agentic'),
        ('What is agent delegation?', 'Agent assigns tasks to others', 'User assigns tasks', 'Hardware assigns', 'Network assigns', 1, 'hard', 'agentic'),
        ('What is a chatbot?', 'AI program for conversation', 'Chat application', 'Social media app', 'Email client', 1, 'medium', 'applications'),
        ('Which is a popular LLM?', 'GPT series', 'Excel', 'Word', 'PowerPoint', 1, 'medium', 'llms'),
        ('What is zero-shot learning?', 'Task without examples', 'No learning required', 'Hardware learning', 'Cloud learning', 1, 'medium', 'learning'),
        ('What is multi-modal AI?', 'Processes multiple data types', 'Single data type', 'Audio only', 'Image only', 1, 'medium', 'basics'),
        ('What is an LLM?', 'Large Language Model', 'Low Learning Machine', 'Linear Logic Model', 'Large Learning Method', 1, 'medium', 'llms'),
        ('Which is NOT a text-generation model?', 'GPT-4', 'BERT', 'Mistral', 'Claude', 2, 'medium', 'llms'),
        ('What is model fine-tuning?', 'Adapting model to specific task', 'Hardware tuning', 'Network tuning', 'Storage tuning', 1, 'medium', 'training'),
        ('What israg stand for?', 'Retrieval-Augmented Generation', 'Random Access Generation', 'Remote Access Gateway', 'Rapid Application Generation', 1, 'medium', 'advanced'),
        ('What is agent orchestration?', 'Coordinating multiple agents', 'Single agent control', 'Hardware control', 'Network control', 1, 'hard', 'agentic'),
        ('What is agent reasoning?', 'Logical decision making', 'Hardware calculation', 'Data storage', 'Network routing', 1, 'medium', 'agentic'),
        ('What is chain of thought prompting?', 'Step-by-step reasoning prompts', 'Simple questions', 'Image prompts', 'Audio prompts', 1, 'medium', 'basics'),
        ('What is few-shot learning?', 'Learning from few examples', 'Learning slowly', 'Hardware limitation', 'Small dataset only', 1, 'medium', 'learning'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO questions 
        (question, option1, option2, option3, option4, correct_answer, difficulty, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', questions)
    
    conn.commit()
    conn.close()
    print(f"Database initialized with {len(questions)} questions")
# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', user=get_current_user())

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/google-login')
def google_login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google-callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = google.authorize_access_token()
        userinfo_endpoint = "https://openid.googleapis.com/v1/userinfo"
        userinfo = google.get(userinfo_endpoint).json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (userinfo['email'],))
        user = cursor.fetchone()
        
        if user is None:
            cursor.execute('''
                INSERT INTO users (google_id, email, name, picture, last_login)
                VALUES (?, ?, ?, ?, ?)
            ''', (userinfo['sub'], userinfo['email'], userinfo.get('name'), 
                  userinfo.get('picture'), datetime.now()))
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user['id']
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                          (datetime.now(), user_id))
            conn.commit()
        
        conn.close()
        
        session['user_id'] = user_id
        session['user_email'] = userinfo['email']
        session['user_name'] = userinfo.get('name', 'User')
        session['user_picture'] = userinfo.get('picture')
        
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM user_attempts 
        WHERE user_id = ? 
        ORDER BY attempted_at DESC 
        LIMIT 10
    ''', (session['user_id'],))
    attempts = cursor.fetchall()
    
    cursor.execute('''
        SELECT * FROM certificates WHERE user_id = ? 
        ORDER BY passed_at DESC LIMIT 1
    ''', (session['user_id'],))
    certificate = cursor.fetchone()
    conn.close()
    
    return render_template('dashboard.html', user=get_current_user(), 
                          attempts=attempts, certificate=certificate)

@app.route('/start-quiz')
@login_required
def start_quiz():
    """Start a new quiz"""
    questions = get_random_questions(15)
    session['current_quiz'] = {
        'questions': [q['id'] for q in questions],
        'answers': {},
        'started_at': datetime.now().isoformat()
    }
    session['current_question_index'] = 0
    return redirect(url_for('quiz_question', question_index=0))

@app.route('/quiz/<int:question_index>', methods=['GET', 'POST'])
@login_required
def quiz_question(question_index):
    """Display quiz question"""
    if 'current_quiz' not in session:
        return redirect(url_for('start_quiz'))
    
    quiz = session['current_quiz']
    questions_ids = quiz['questions']
    
    if question_index >= len(questions_ids):
        return redirect(url_for('complete_quiz'))
    
    question_id = questions_ids[question_index]
    question = get_question_by_id(question_id)
    
    if request.method == 'POST':
        answer = int(request.form.get('answer', 0))
        quiz['answers'][question_id] = answer
        session['current_quiz'] = quiz
        
        if question_index < len(questions_ids) - 1:
            return redirect(url_for('quiz_question', question_index=question_index + 1))
        else:
            return redirect(url_for('complete_quiz'))
    
    return render_template('quiz.html', user=get_current_user(), 
                          question=question, question_index=question_index,
                          total_questions=len(questions_ids))

@app.route('/complete-quiz')
@login_required
def complete_quiz():
    """Complete quiz and calculate score"""
    if 'current_quiz' not in session:
        return redirect(url_for('start_quiz'))
    
    quiz = session['current_quiz']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    score = 0
    total = len(quiz['questions'])
    
    for question_id, user_answer in quiz['answers'].items():
        cursor.execute('SELECT correct_answer FROM questions WHERE id = ?', (question_id,))
        correct = cursor.fetchone()['correct_answer']
        if user_answer == correct:
            score += 1
    
    conn.close()
    
    save_user_attempt(session['user_id'], score, total)
    
    passed = score >= total * 0.6
    certificate = None
    if passed:
        cert_id, cert_number = save_certificate(session['user_id'], score, total)
        certificate = {
            'id': cert_id,
            'certificate_number': cert_number,
            'score': score,
            'total': total,
            'passed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    session.pop('current_quiz', None)
    
    return render_template('result.html', user=get_current_user(), 
                          score=score, total=total, passed=passed, 
                          certificate=certificate)

@app.route('/certificate/<int:cert_id>/download')
@login_required
def download_certificate(cert_id):
    """Download certificate"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, u.email, u.name 
        FROM certificates c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.id = ?
    ''', (cert_id,))
    certificate = cursor.fetchone()
    conn.close()
    
    if not certificate or certificate['user_id'] != session['user_id']:
        flash('Certificate not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('certificate_preview.html', certificate=certificate, user=get_current_user())

@app.route('/certificate/<int:cert_id>/share')
@login_required
def share_certificate(cert_id):
    """Share certificate details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, u.email, u.name 
        FROM certificates c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.id = ?
    ''', (cert_id,))
    certificate = cursor.fetchone()
    conn.close()
    
    if not certificate or certificate['user_id'] != session['user_id']:
        flash('Certificate not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('share_certificate.html', certificate=certificate)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)