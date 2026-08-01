# AXXA Insurance - Django Web Application

A comprehensive insurance management system built with Django for AXXA Insurance company.

## Features

- **Customer Registration & Login**
  - Secure user authentication system
  - Customer profile management

- **Policy Management**
  - View and manage insurance policies
  - Policy details and documents
  - Policy status tracking

- **Claims Processing**
  - Submit new claims
  - Track claim status
  - Upload supporting documents
  - View claim history

- **Premium Calculator**
  - Estimate insurance premiums
  - Multiple policy type support

- **Customer Dashboard**
  - Overview of policies and claims
  - Notifications system
  - Quick navigation

## Tech Stack

- **Backend**: Django 6.0.7 (Python 3.12)
- **Database**: SQLite (production-ready)
- **Frontend**: Bootstrap 5.3, Font Awesome 6.4
- **Server**: Django development server

## Prerequisites

- Python 3.12+
- Miniconda/Anaconda (optional but recommended)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/suneetjainconnect-Dev/AXXA-Insurance.git
cd AXXA-Insurance
```

### 2. Create and Activate Conda Environment

```bash
conda env create -f environment.yml
conda activate axxa_insurance
```

Or create manually:

```bash
conda create -n axxa_insurance python=3.12 -y
conda activate axxa_insurance
```

### 3. Install Dependencies

```bash
pip install django
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Project Structure

```
Project4/
├── axxa_insurance/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── insurance/               # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Form definitions
│   ├── admin.py            # Admin configuration
│   └── templates/          # HTML templates
├── static/                 # Static files (CSS, JS)
├── templates/             # Global templates
├── media/                 # User uploaded files
├── manage.py              # Django management script
└── README.md
```

## Models

### Customer
- User profile extension
- Contact information
- Personal details

### Policy
- Insurance policy details
- Policy types: Health, Life, Motor, Home, Travel, Business
- Status tracking

### Claim
- Claim submission and tracking
- Document management
- Status workflow

### Document
- File uploads for policies and claims

### Notification
- Customer notifications
- Priority levels
- Read/unread status

## Key Features

1. **Responsive Design**: Mobile-friendly interface using Bootstrap 5
2. **Secure Authentication**: Django's built-in authentication
3. **File Uploads**: Secure document handling
4. **Admin Interface**: Complete administrative control
5. **Custom Templates**: Professional insurance-focused UI

## Deployment

### Environment Variables

Create a `.env` file in the project root:

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com
```

### Production Server

For production deployment, use a WSGI server like Gunicorn with Nginx as a reverse proxy.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is proprietary to AXXA Insurance.

## Contact

- Email: support@axxainsurance.com
- Phone: 1-800-AXXA-INS (1-800-299-2467)
- Website: https://www.axxainsurance.com
