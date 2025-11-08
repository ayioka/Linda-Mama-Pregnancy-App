from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import UserProfile

def home(request):
    return render(request, 'pregnancy/home.html')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'pregnancy/login.html', {'form': form})

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Send welcome email
            try:
                send_mail(
                    'Welcome to Linda Mama Pregnancy Tracker!',
                    f'''Hello {user.first_name} {user.last_name},

Thank you for creating an account with Linda Mama Pregnancy Tracker!

Your account has been successfully created. You can now:
- Track your pregnancy week by week
- Access educational resources
- Connect with healthcare providers
- Monitor your health metrics

Start your journey by visiting your dashboard: http://127.0.0.1:8000/dashboard/

Best regards,
Linda Mama Team''',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Account created successfully! Welcome email sent.')
            except Exception as e:
                messages.warning(request, 'Account created, but failed to send welcome email.')
            
            # Log the user in
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    # Use register.html instead of signup.html
    return render(request, 'pregnancy/register.html', {'form': form})

@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Calculate pregnancy progress if due date is set
    current_week = None
    progress_percentage = 0
    current_trimester = "Not set"
    trimester_message = "Set your due date in profile"
    
    if profile.due_date:
        # Calculate current week of pregnancy
        today = date.today()
        due_date = profile.due_date
        
        # Assuming 40 weeks pregnancy
        total_weeks = 40
        weeks_passed = (today - (due_date - relativedelta(weeks=40))).days // 7
        current_week = max(1, min(weeks_passed, 40))
        
        # Calculate progress percentage
        progress_percentage = min(100, (current_week / total_weeks) * 100)
        
        # Determine trimester
        if current_week <= 13:
            current_trimester = "First Trimester"
            trimester_message = "Early development stage"
        elif current_week <= 26:
            current_trimester = "Second Trimester"
            trimester_message = "Golden trimester - feeling better!"
        else:
            current_trimester = "Third Trimester"
            trimester_message = "Final stretch - almost there!"
    
    context = {
        'profile': profile,
        'current_week': current_week,
        'progress_percentage': progress_percentage,
        'current_trimester': current_trimester,
        'trimester_message': trimester_message,
    }
    return render(request, 'pregnancy/dashboard.html', context)

@login_required
def profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update user fields
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update profile fields
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            profile.date_of_birth = date_of_birth
            
        profile.blood_type = request.POST.get('blood_type', profile.blood_type)
        profile.emergency_contact = request.POST.get('emergency_contact', profile.emergency_contact)
        profile.allergies = request.POST.get('allergies', profile.allergies)
        profile.address = request.POST.get('address', profile.address)
        
        # Handle due date
        due_date = request.POST.get('due_date')
        if due_date:
            profile.due_date = due_date
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'pregnancy/profile.html', context)

@login_required
def baby_development(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    # Calculate current week if due date is set
    current_week = None
    current_trimester = "Not set"
    
    if profile.due_date:
        today = date.today()
        due_date = profile.due_date
        weeks_passed = (today - (due_date - relativedelta(weeks=40))).days // 7
        current_week = max(1, min(weeks_passed, 40))
        
        if current_week <= 13:
            current_trimester = "First Trimester"
        elif current_week <= 26:
            current_trimester = "Second Trimester"
        else:
            current_trimester = "Third Trimester"
    
    # Sample development data based on week
    development_data = get_development_data(current_week)
    
    context = {
        'profile': profile,
        'current_week': current_week,
        'current_trimester': current_trimester,
        **development_data
    }
    return render(request, 'pregnancy/baby_development.html', context)

def get_development_data(week):
    """Get baby development information based on current week"""
    if not week:
        return {}
    
    # Sample development data
    development_data = {
        'baby_size_comparison': get_size_comparison(week),
        'baby_weight': get_baby_weight(week),
        'baby_length': get_baby_length(week),
        'key_developments': get_key_developments(week),
        'maternal_changes': get_maternal_changes(week),
        'upcoming_milestones': get_upcoming_milestones(week),
        'current_tips': get_current_tips(week),
    }
    
    return development_data

def get_size_comparison(week):
    comparisons = {
        1: "poppy seed", 2: "sesame seed", 3: "apple seed", 4: "blueberry",
        5: "sesame seed", 6: "lentil", 7: "blueberry", 8: "kidney bean",
        9: "grape", 10: "kumquat", 11: "fig", 12: "lime",
        13: "pea pod", 14: "lemon", 15: "apple", 16: "avocado",
        17: "turnip", 18: "bell pepper", 19: "tomato", 20: "banana",
        21: "carrot", 22: "spaghetti squash", 23: "mango", 24: "corn",
        25: "rutabaga", 26: "green onion", 27: "cauliflower", 28: "eggplant",
        29: "butternut squash", 30: "cabbage", 31: "coconut", 32: "squash",
        33: "pineapple", 34: "melon", 35: "honeydew", 36: "head of romaine",
        37: "swiss chard", 38: "leek", 39: "mini-watermelon", 40: "pumpkin"
    }
    return comparisons.get(week, "growing baby")

def get_baby_weight(week):
    weights = {
        8: "1g", 12: "14g", 16: "100g", 20: "300g",
        24: "600g", 28: "1kg", 32: "1.7kg", 36: "2.6kg", 40: "3.4kg"
    }
    closest_week = min(weights.keys(), key=lambda x: abs(x - week))
    return weights[closest_week]

def get_baby_length(week):
    lengths = {
        8: "1.6cm", 12: "5.4cm", 16: "11.6cm", 20: "16.4cm",
        24: "21cm", 28: "37.6cm", 32: "42.4cm", 36: "47.4cm", 40: "51.2cm"
    }
    closest_week = min(lengths.keys(), key=lambda x: abs(x - week))
    return lengths[closest_week]

def get_key_developments(week):
    developments = {
        1: ["Rapid cell division begins", "Implantation in uterus"],
        20: ["Baby can hear sounds", "Regular sleep-wake cycles begin", "Vernix caseosa forms on skin"],
        30: ["Eyes can open and close", "Bone marrow makes red blood cells", "Lanugo hair begins to disappear"]
    }
    closest_week = min(developments.keys(), key=lambda x: abs(x - week))
    return developments.get(closest_week, ["Baby is growing and developing!"])

def get_maternal_changes(week):
    changes = {
        1: "You might not feel any changes yet, but amazing things are happening!",
        20: "You may start feeling baby movements - those gentle flutters are your baby saying hello!",
        30: "You might feel more pronounced movements and some discomfort as baby grows."
    }
    closest_week = min(changes.keys(), key=lambda x: abs(x - week))
    return changes.get(closest_week, "Your body is doing amazing work growing your baby!")

def get_upcoming_milestones(week):
    milestones = {
        1: ["First heartbeat detection", "Major organ formation"],
        20: ["Development of senses", "Rapid weight gain"],
        30: ["Brain development peaks", "Lung maturation"]
    }
    closest_week = min(milestones.keys(), key=lambda x: abs(x - week))
    return milestones.get(closest_week, ["Continued growth and development"])

def get_current_tips(week):
    tips = {
        1: ["Take prenatal vitamins", "Stay hydrated", "Get plenty of rest"],
        20: ["Eat small, frequent meals", "Practice gentle exercise", "Start planning your nursery"],
        30: ["Practice relaxation techniques", "Prepare your hospital bag", "Rest when possible"]
    }
    closest_week = min(tips.keys(), key=lambda x: abs(x - week))
    return tips.get(closest_week, ["Listen to your body", "Stay hydrated", "Get regular checkups"])

@login_required
def resources(request):
    return render(request, 'pregnancy/resources.html')

@login_required
def week_tracker(request):
    return render(request, 'pregnancy/week_tracker.html')

@login_required
def health_metrics(request):
    return render(request, 'pregnancy/health_metrics.html')

@login_required
def appointments(request):
    return render(request, 'pregnancy/appointments.html')

@login_required
def emergency(request):
    return render(request, 'pregnancy/emergency.html')

@login_required
def nutrition(request):
    return render(request, 'pregnancy/nutrition.html')

@login_required
def exercise(request):
    return render(request, 'pregnancy/exercise.html')

@login_required
def mental_health(request):
    return render(request, 'pregnancy/mental_health.html')
