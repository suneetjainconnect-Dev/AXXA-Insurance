from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Customer, Policy, Claim, Document, Notification
from .forms import CustomerForm, PolicyForm, ClaimForm, DocumentForm


def index(request):
    """Home page for AXXA Insurance"""
    return render(request, 'insurance/index.html')


def about(request):
    """About AXXA Insurance"""
    return render(request, 'insurance/about.html')


def contact(request):
    """Contact page"""
    return render(request, 'insurance/contact.html')


@login_required
def dashboard(request):
    """Customer dashboard"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        customer = None
    
    policies = Policy.objects.filter(customer=customer) if customer else []
    claims = Claim.objects.filter(customer=customer) if customer else []
    notifications = Notification.objects.filter(customer=customer, is_read=False) if customer else []
    
    context = {
        'customer': customer,
        'policies': policies,
        'claims': claims,
        'notifications': notifications,
    }
    return render(request, 'insurance/dashboard.html', context)


@login_required
def policy_list(request):
    """List all policies for the customer"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('dashboard')
    
    policies = Policy.objects.filter(customer=customer)
    
    query = request.GET.get('q')
    if query:
        policies = policies.filter(
            Q(policy_number__icontains=query) |
            Q(policy_type__icontains=query)
        )
    
    context = {
        'policies': policies,
        'query': query,
    }
    return render(request, 'insurance/policy_list.html', context)


@login_required
def policy_detail(request, pk):
    """Policy details"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('dashboard')
    
    policy = get_object_or_404(Policy, pk=pk, customer=customer)
    claims = policy.claims.all()
    documents = policy.documents.all()
    
    context = {
        'policy': policy,
        'claims': claims,
        'documents': documents,
    }
    return render(request, 'insurance/policy_detail.html', context)


@login_required
def claim_list(request):
    """List all claims for the customer"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('dashboard')
    
    claims = Claim.objects.filter(customer=customer)
    
    query = request.GET.get('q')
    if query:
        claims = claims.filter(
            Q(claim_number__icontains=query) |
            Q(claim_type__icontains=query)
        )
    
    context = {
        'claims': claims,
        'query': query,
    }
    return render(request, 'insurance/claim_list.html', context)


@login_required
def claim_detail(request, pk):
    """Claim details"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('dashboard')
    
    claim = get_object_or_404(Claim, pk=pk, customer=customer)
    documents = claim.documents.all()
    
    context = {
        'claim': claim,
        'documents': documents,
    }
    return render(request, 'insurance/claim_detail.html', context)


@login_required
def create_claim(request, policy_id):
    """Create a new claim for a policy"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('dashboard')
    
    policy = get_object_or_404(Policy, id=policy_id, customer=customer)
    
    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.policy = policy
            claim.customer = customer
            claim.claim_number = f"CLM-{policy.id}-{Claim.objects.filter(policy=policy).count() + 1}"
            claim.save()
            messages.success(request, "Claim submitted successfully.")
            return redirect('policy_detail', pk=policy.id)
    else:
        form = ClaimForm()
    
    context = {
        'policy': policy,
        'form': form,
    }
    return render(request, 'insurance/claim_form.html', context)


@login_required
def upload_document(request, claim_id):
    """Upload documents for a claim"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('dashboard')
    
    claim = get_object_or_404(Claim, id=claim_id, customer=customer)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.claim = claim
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('claim_detail', pk=claim.id)
    else:
        form = DocumentForm()
    
    context = {
        'claim': claim,
        'form': form,
    }
    return render(request, 'insurance/document_upload.html', context)


@login_required
def profile(request):
    """View and edit customer profile"""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        customer = Customer(user=request.user)
        customer.save()
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
    }
    return render(request, 'insurance/profile.html', context)


def policy_catalog(request):
    """View available policy types"""
    policy_types = [
        ('health', 'Health Insurance', 'Comprehensive health coverage for you and your family'),
        ('life', 'Life Insurance', 'Financial security for your loved ones'),
        ('motor', 'Motor Insurance', 'Protection for your vehicle against accidents and damage'),
        ('home', 'Home Insurance', 'Secure your home and belongings'),
        ('travel', 'Travel Insurance', 'Protect your trips with comprehensive coverage'),
        ('business', 'Business Insurance', 'Safeguard your business assets and operations'),
    ]
    
    context = {
        'policy_types': policy_types,
    }
    return render(request, 'insurance/policy_catalog.html', context)


@login_required
def mark_notification_read(request, pk):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, pk=pk, customer=request.user.customer)
    notification.is_read = True
    notification.save()
    return redirect('dashboard')


def premium_calculator(request):
    """Premium calculator"""
    context = {}
    
    if request.method == 'POST':
        policy_type = request.POST.get('policy_type')
        coverage_amount = float(request.POST.get('coverage_amount', 0))
        age = int(request.POST.get('age', 0))
        
        # Simplified premium calculation
        base_rates = {
            'health': 5000,
            'life': 3000,
            'motor': 8000,
            'home': 4000,
            'travel': 2000,
            'business': 15000,
        }
        
        rate = base_rates.get(policy_type, 0)
        premium = rate + (coverage_amount * 0.01) + (age * 50)
        
        context = {
            'premium': premium,
            'coverage_amount': coverage_amount,
            'policy_type': policy_type,
        }
    
    return render(request, 'insurance/premium_calculator.html', context)
