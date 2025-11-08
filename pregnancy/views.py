# pregnancy/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

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
        
        # Calculate start date (40 weeks before due date)
        start_date = due_date - relativedelta(weeks=40)
        
        # Calculate weeks passed
        days_passed = (today - start_date).days
        weeks_passed = days_passed // 7 if days_passed > 0 else 0
        current_week = max(1, min(weeks_passed, 40))
        
        # Calculate progress percentage
        total_weeks = 40
        progress_percentage = min(100, max(0, (current_week / total_weeks) * 100))
        
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
        start_date = due_date - relativedelta(weeks=40)
        days_passed = (today - start_date).days
        weeks_passed = days_passed // 7 if days_passed > 0 else 0
        current_week = max(1, min(weeks_passed, 40))
        
        if current_week <= 13:
            current_trimester = "First Trimester"
        elif current_week <= 26:
            current_trimester = "Second Trimester"
        else:
            current_trimester = "Third Trimester"
    
    # Get development data based on week
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
        return {
            'baby_size_comparison': 'Not available',
            'baby_weight': 'Not available',
            'baby_length': 'Not available',
            'key_developments': ['Set your due date in profile to see development information'],
            'maternal_changes': 'Set your due date in profile to see maternal changes',
            'upcoming_milestones': ['Set your due date to see upcoming milestones'],
            'current_tips': ['Set your due date to get personalized tips']
        }
    
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
        8: ["Neural tube forms", "Heart begins to beat", "Major organs start developing"],
        12: ["Fingers and toes form", "Sex organs develop", "Reflexes begin"],
        16: ["Muscles develop", "Baby can make faces", "Sucking reflex develops"],
        20: ["Baby can hear sounds", "Regular sleep-wake cycles begin", "Vernix caseosa forms on skin"],
        24: ["Lungs develop", "Taste buds form", "Rapid brain growth"],
        28: ["Eyes can open", "Brain develops rapidly", "Baby can dream"],
        30: ["Eyes can open and close", "Bone marrow makes red blood cells", "Lanugo hair begins to disappear"],
        36: ["Lungs mature", "Fat layers build up", "Baby positions for birth"],
        40: ["Full term development", "Ready for birth", "All organs developed"]
    }
    closest_week = min(developments.keys(), key=lambda x: abs(x - week))
    return developments.get(closest_week, ["Baby is growing and developing!"])

def get_maternal_changes(week):
    changes = {
        1: "You might not feel any changes yet, but amazing things are happening!",
        8: "You may experience morning sickness, fatigue, and breast tenderness.",
        12: "Morning sickness may improve, energy might return, and baby bump may start showing.",
        20: "You may start feeling baby movements - those gentle flutters are your baby saying hello!",
        28: "You might experience back pain, shortness of breath, and more pronounced baby movements.",
        30: "You might feel more pronounced movements and some discomfort as baby grows.",
        36: "You may experience Braxton Hicks contractions, nesting instinct, and increased fatigue."
    }
    closest_week = min(changes.keys(), key=lambda x: abs(x - week))
    return changes.get(closest_week, "Your body is doing amazing work growing your baby!")

def get_upcoming_milestones(week):
    milestones = {
        1: ["First heartbeat detection", "Major organ formation"],
        12: ["First trimester screening", "Reduced miscarriage risk"],
        20: ["Anatomy scan ultrasound", "Feeling baby movements"],
        24: ["Viability milestone", "Rapid weight gain begins"],
        28: ["Third trimester begins", "Gestational diabetes test"],
        36: ["Weekly checkups begin", "Baby drops into position"]
    }
    closest_week = min(milestones.keys(), key=lambda x: abs(x - week))
    return milestones.get(closest_week, ["Continued growth and development"])

def get_current_tips(week):
    tips = {
        1: ["Take prenatal vitamins", "Stay hydrated", "Get plenty of rest", "Avoid harmful substances"],
        12: ["Eat small, frequent meals", "Continue prenatal vitamins", "Start maternity clothes", "Gentle exercise"],
        20: ["Eat small, frequent meals", "Practice gentle exercise", "Start planning your nursery", "Stay hydrated"],
        28: ["Monitor blood pressure", "Practice good posture", "Elevate feet when sitting", "Sleep on side"],
        30: ["Practice relaxation techniques", "Prepare your hospital bag", "Rest when possible", "Monitor baby movements"],
        36: ["Pack hospital bag", "Practice breathing exercises", "Finalize birth plan", "Rest frequently"]
    }
    closest_week = min(tips.keys(), key=lambda x: abs(x - week))
    return tips.get(closest_week, ["Listen to your body", "Stay hydrated", "Get regular checkups", "Eat nutritious meals"])

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
        
        # Handle date fields
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            try:
                profile.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format for date of birth')
        
        due_date = request.POST.get('due_date')
        if due_date:
            try:
                profile.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format for due date')
        
        profile.blood_type = request.POST.get('blood_type', profile.blood_type)
        profile.emergency_contact = request.POST.get('emergency_contact', profile.emergency_contact)
        profile.allergies = request.POST.get('allergies', profile.allergies)
        profile.address = request.POST.get('address', profile.address)
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'pregnancy/profile.html', context)

# Add other essential views
@login_required
def appointments(request):
    return render(request, 'pregnancy/appointments.html')

@login_required
def nutrition(request):
    return render(request, 'pregnancy/nutrition.html')

@login_required
def symptoms(request):
    return render(request, 'pregnancy/symptoms.html')
