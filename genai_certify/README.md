# CertifyAI-Pro - GenAI & Agentic AI Certification Platform

A professional certification platform for Generative AI and Agentic AI knowledge assessment.

## Features

- 🎓 Google OAuth authentication
- 📚 120+ questions covering GENAI and Agentic AI concepts
- 📝 15-question certification quiz (12 easy + 3 advanced)
- 🎖️ Professional PDF certificates
- 📊 Performance tracking and history
- 🔗 LinkedIn share functionality
- 🔐 Secure and private user data

## Project Structure

```
genai_certify/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── database.db           # SQLite database (auto-created)
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── dashboard.html    # User dashboard
│   ├── quiz.html         # Quiz interface
│   ├── result.html       # Results page
│   ├── certificate_template.html  # Certificate PDF template
│   └── share_certificate.html     # Certificate sharing
├── static/
│   └── style.css         # Custom styling
└── certificates/         # Generated certificates
```

## Installation

### Prerequisites

1. Python 3.8 or higher
2. pip (Python package manager)
3. wkhtmltopdf (for PDF generation)

### Setup Steps

#### 1. Install wkhtmltopdf (Required for PDF generation)

**Windows:**
```bash
# Download from: https://wkhtmltopdf.org/downloads.html
# Or using Chocolatey:
choco install wkhtmltopdf
```

**macOS:**
```bash
brew install wkhtmltopdf
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install wkhtmltopdf
```

#### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth credentials
5. Add authorized redirect URI: `http://localhost:5000/google-callback`
6. Copy the Client ID and Secret

#### 4. Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:GOOGLE_CLIENT_ID="your-client-id-here"
$env:GOOGLE_CLIENT_SECRET="your-client-secret-here"
```

**Windows (CMD):**
```cmd
set GOOGLE_CLIENT_ID=your-client-id-here
set GOOGLE_CLIENT_SECRET=your-client-secret-here
```

**Linux/macOS:**
```bash
export GOOGLE_CLIENT_ID="your-client-id-here"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"
```

#### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## How It Works

### User Flow

1. User visits the site and clicks "Get Certified"
2. User authenticates with Google account
3. User can take the certification quiz
4. Quiz generates 15 random questions (12 easy, 3 hard)
5. User submits answers and receives score
6. If score ≥ 60%, user gets a certificate
7. Certificate can be downloaded as PDF
8. User can share certificate on LinkedIn

### Question Categories

- **Easy (60%):** 12 questions covering basics
  - GENAI fundamentals
  - Basic AI concepts
  - Common tools and platforms
  
- **Medium/Hard (40%):** 3 questions covering advanced topics
  - LLM architecture
  - Agent systems
  - Advanced concepts

### Certificate System

- Unique certificate number generated for each pass
- Certificate includes user name, score, and date
- PDF format with professional design
- Shareable link for verification

## Security Features

- Google OAuth for secure authentication
- Password hashing for local accounts
- Session management
- SQL injection prevention
- XSS protection via Jinja2 templating
- CORS configuration

## Technologies Used

- **Backend:** Python, Flask
- **Database:** SQLite
- **Authentication:** Google OAuth 2.0
- **PDF Generation:** pdfkit (wkhtmltopdf)
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript

## Customization

### Add More Questions

Edit `app.py` and add questions to the `questions_genai` and `questions_agentic` lists:

```python
('Question text?', 'Option 1', 'Option 2', 'Option 3', 'Option 4', correct_answer, difficulty, category),
```

### Change Certificate Design

Edit `templates/certificate_template.html` to customize the certificate layout.

### Modify Quiz Settings

In `app.py`, adjust:
- Number of questions: `get_random_questions(15)`
- Passing score: `score >= total * 0.6`
- Difficulty distribution

## Deployment

### Using Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn app:app
```
3. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku config:set GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=...
heroku run python app.py --app your-app-name
```

### Using PythonAnywhere

1. Upload code to PythonAnywhere
2. Set up virtualenv
3. Install dependencies
4. Configure WSGI file
5. Set environment variables in dashboard

## Troubleshooting

### PDF Generation Issues

If certificates aren't generating:
1. Verify wkhtmltopdf is installed
2. Check PATH includes wkhtmltopdf binary
3. Test: `wkhtmltopdf --version`

### OAuth Issues

If login fails:
1. Verify redirect URI matches exactly
2. Check Client ID and Secret are correct
3. Ensure Google+ API is enabled
4. Verify domain is whitelisted if using production

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Open an issue on GitHub
- Email support@certifyai-pro.com
- Join our Discord community

---

**CertifyAI-Pro** - Empowering AI professionals with verified certifications