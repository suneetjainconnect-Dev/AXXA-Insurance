from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Policy(models.Model):
    POLICY_TYPE_CHOICES = [
        ('health', 'Health Insurance'),
        ('life', 'Life Insurance'),
        ('motor', 'Motor/Car Insurance'),
        ('home', 'Home Insurance'),
        ('travel', 'Travel Insurance'),
        ('business', 'Business Insurance'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    policy_number = models.CharField(max_length=50, unique=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPE_CHOICES)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='policies')
    provider_name = models.CharField(max_length=100, default='AXXA Insurance')
    start_date = models.DateField()
    end_date = models.DateField()
    premium_amount = models.DecimalField(max_digits=12, decimal_places=2)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.policy_number} - {self.policy_type}"
    
    @property
    def is_active(self):
        from datetime import date
        return self.status == 'active' and self.start_date <= date.today() <= self.end_date


class Claim(models.Model):
    CLAIM_TYPE_CHOICES = [
        ('health', 'Health Claim'),
        ('life', 'Life Claim'),
        ('motor', 'Motor Claim'),
        ('home', 'Home Claim'),
        ('travel', 'Travel Claim'),
        ('business', 'Business Claim'),
    ]
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('requested_info', 'Additional Information Required'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('settled', 'Settled'),
    ]
    
    claim_number = models.CharField(max_length=50, unique=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='claims')
    claim_type = models.CharField(max_length=20, choices=CLAIM_TYPE_CHOICES)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='claims')
    description = models.TextField()
    incident_date = models.DateField()
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    processed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    rejection_reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.claim_number} - {self.claim_type}"
    
    @property
    def pending_amount(self):
        return self.claim_amount - self.processed_amount


class Document(models.Model):
    document_type = models.CharField(max_length=50)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.policy or self.claim}"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('policy_expiry', 'Policy Expiry Reminder'),
        ('premium_due', 'Premium Due Reminder'),
        ('claim_status', 'Claim Status Update'),
        ('policyRenewal', 'Policy Renewal Offer'),
        ('general', 'General Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.customer}"
