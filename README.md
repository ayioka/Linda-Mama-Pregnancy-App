# Linda Mama Pregnancy App 🤰

This is a comprehensive web-based maternal health tracking system I built to support pregnant mothers throughout their pregnancy journey from conception to delivery. This is my Flask-based web application that bridges healthcare gaps for expectant mothers in Kenya and across Africa.

![Linda Mama](https://img.shields.io/badge/Linda-Mama-pink) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-green) ![License](https://img.shields.io/badge/License-MIT-yellow) ![Live](https://img.shields.io/badge/Live-Demo-success)

## 🌟 Live Demo

**🚀 Try it out now**: [https://lindamamapregnancytracker.onrender.com/](https://lindamamapregnancytracker.onrender.com/)

**Test Credentials**:
- **Admin Account**: `admin@lindamama.com` / `admin123`
- **Or create your own account** with any of the three roles

## 📖 About My Project

I developed Linda Mama to address maternal health challenges in underserved communities. This platform provides interactive tools for tracking pregnancy milestones, accessing professional health guidance, and receiving timely medical support.

### What I Built

- **👥 Multi-Role System**: Separate interfaces for Pregnant Mothers, Clinicians, and Administrators
- **📊 Pregnancy Tracking**: Week-by-week progress monitoring and milestone tracking
- **🏥 Medical Management**: Appointment scheduling and medical records
- **🔐 Secure Authentication**: Role-based access control with password encryption
- **📱 Responsive Design**: Mobile-friendly interface for accessibility
- **🎨 Beautiful UI**: Custom pink-themed design with smooth animations

## 🛠️ My Tech Stack

### Backend
- **Python 3.8+** with **Flask** framework
- **Flask-SQLAlchemy** for database ORM
- **Flask-Login** for authentication management
- **Flask-Bcrypt** for password security
- **Gunicorn** for production deployment

### Frontend
- **HTML5**, **CSS3** with custom pink theme
- **Bootstrap 5.3** for responsive design
- **JavaScript** for interactive features

### Database & Deployment
- **SQLite** for development
- **PostgreSQL** for production on Render
- **Render** for cloud hosting

## 🏃‍♀️ How to Run Locally

If you want to run this project on your local machine:

### 1. Clone My Repository
```bash
git clone https://github.com/ayioka/Linda-Mama-Pregrancy-App.git
cd Linda-Mama-Pregrancy-App
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run the Application
```bash
python app.py
```

### 6. Access the App
Open your browser to: `http://localhost:5000`

## 👥 User Roles I Implemented

### 🤰 Pregnant Mothers
- Personalized pregnancy dashboard
- Appointment booking and management
- Medical records access
- Pregnancy progress tracking
- Emergency contact features

### 👩‍⚕️ Healthcare Clinicians
- Patient management system
- Appointment scheduling
- Medical records access
- Clinical dashboard overview

### ⚙️ System Administrators
- Complete user management
- System monitoring and analytics
- Application configuration
- Role-based permissions

## 🗄️ My Database Design

I designed a relational database with these core tables:
- **users** - User accounts with role-based access
- **appointments** - Medical appointment scheduling
- **medical_records** - Patient health information
- **vitals_logs** - Pregnancy vital signs tracking

## 🌐 How I Deployed

I deployed this application on **Render** with the following setup:

1. **Web Service** on Render with Python environment
2. **PostgreSQL** database for production data
3. **Gunicorn** as the production WSGI server
4. **Environment variables** for secure configuration

The deployment is fully automated through Render's GitHub integration - every push to main automatically deploys updates.

## 📈 Features I'm Proud Of

- ✅ **Complete authentication system** with role-based access
- ✅ **Responsive design** that works on all devices
- ✅ **Production-ready deployment** with proper security
- ✅ **Clean, maintainable code** structure
- ✅ **User-friendly interface** with intuitive navigation

## 🔮 Future Enhancements I'm Planning

- [ ] Mobile app version with React Native
- [ ] SMS notifications for appointments
- [ ] Integration with local healthcare systems
- [ ] Multilingual support (Swahili, Luo, Kikuyu)
- [ ] Advanced analytics for healthcare providers

## 📊 Project Impact

This project addresses critical maternal health challenges by:
- Providing accessible pregnancy tracking tools
- Connecting mothers with healthcare providers
- Offering reliable health information
- Reducing barriers to maternal care

## 🤝 Contributing

I welcome contributions! If you'd like to improve Linda Mama:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact Me

**Shem Ayioka**
- GitHub: [@ayioka](https://github.com/ayioka)
- Project Link: [https://github.com/ayioka/Linda-Mama-Pregrancy-App](https://github.com/ayioka/Linda-Mama-Pregrancy-App)
- Live App: [https://lindamamapregnancytracker.onrender.com/](https://lindamamapregnancytracker.onrender.com/)
