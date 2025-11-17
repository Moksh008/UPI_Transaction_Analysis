# Finoro - UPI Digital Payments Analysis Platform

Finoro is a comprehensive analytics platform for analyzing UPI digital payment trends in India. The platform provides interactive visualizations, forecasting capabilities, and AI-powered insights for understanding transaction patterns, user behavior, and geographic distribution of digital payments.

## 📸 Platform Screenshots

### Main Dashboard
![Finoro Dashboard](./screenshots/dashboard.png)
*Interactive dashboard showing transaction analytics and trends*

### Geographic Analysis
![Geographic View](./screenshots/geographic-view.png)
*State-wise distribution of UPI transactions*

### AI Chat Assistant
![AI Chat](./screenshots/ai-chat.png)
*AI-powered insights and analysis*

### Power BI Dashboard
![Power BI Dashboard](./screenshots/powerbi-dashboard.png)
*Advanced analytics and reporting in Power BI*

## ✨ Features

- **Interactive Dashboard**: Real-time visualization of UPI transaction data
- **Geographic Analysis**: State-wise and district-wise transaction mapping
- **Transaction Type Analysis**: Breakdown by payment categories
- **Forecasting**: ML-powered predictions for future trends
- **AI Chat Assistant**: Natural language queries for data insights
- **User Authentication**: Secure login with Firebase
- **Dark/Light Theme**: Customizable user interface

## 🛠️ Tech Stack

### Frontend
- React.js with Vite
- TailwindCSS for styling
- Firebase Authentication
- Recharts for data visualization
- Framer Motion for animations

### Backend
- Python Flask
- Pandas for data processing
- Prophet for forecasting
- CORS enabled API

### Data Analysis
- Python (Pandas, NumPy)
- Matplotlib & Seaborn for visualizations
- Prophet for time series forecasting

## 📋 Prerequisites

Before running the platform, ensure you have the following installed:

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn** package manager
- **Git** (optional, for cloning)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Moksh008/BE_UPI_Analysis.git
cd "UPI Digital Payments Analysis"
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables (Optional)

Create a `.env` file in the backend directory if needed for API keys or configurations.

#### Start the Backend Server

```bash
python api.py
```

The backend server will start on `http://localhost:5000`

**Note**: Keep this terminal running while using the application.

### 3. Frontend Setup

Open a new terminal window/tab:

#### Install Node Dependencies

```bash
cd Frontend
npm install
```

#### Configure Firebase

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Email/Password authentication
3. Copy your Firebase configuration
4. Update `src/firebase.js` with your credentials:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

#### Start the Frontend Development Server

```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

### 4. Access the Platform

Open your browser and navigate to:
```
http://localhost:5173
```

## 📁 Project Structure

```
Finoro/
├── backend/                # Flask backend server
│   ├── api.py             # Main API endpoints
│   ├── app.py             # Alternative entry point
│   └── requirements.txt   # Python dependencies
├── Frontend/              # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   └── App.jsx        # Main app component
│   └── package.json       # Node dependencies
├── data/                  # CSV datasets
│   ├── agg_trans.csv
│   ├── agg_user.csv
│   ├── map_trans.csv
│   └── ...
├── src/                   # Python analysis scripts
│   ├── eda.py            # Exploratory Data Analysis
│   └── forecast.py       # Forecasting models
└── outputs/              # Generated plots and results
```

## 🎯 Usage Guide

### First Time Setup

1. **Sign Up**: Create a new account using the signup page
2. **Login**: Access the platform with your credentials
3. **Dashboard**: Explore the overview dashboard with key metrics
4. **Geographic View**: Analyze state-wise transaction data
5. **Transaction Types**: View category-wise payment breakdowns
6. **Forecasting**: Access ML-powered predictions
7. **AI Chat**: Ask questions about the data in natural language

### API Endpoints

The backend provides the following endpoints:

- `GET /api/states` - Get list of states
- `GET /api/overview` - Get overview statistics
- `GET /api/geographic` - Get geographic data
- `GET /api/transaction-types` - Get transaction type breakdown
- `GET /api/forecast` - Get forecasting data
- `POST /api/chat` - AI chat interface

## 🔧 Troubleshooting

### Backend Issues

**Port Already in Use**
```bash
# Kill the process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Module Not Found**
```bash
pip install -r requirements.txt --upgrade
```

### Frontend Issues

**Dependencies Installation Failed**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Firebase Configuration Error**
- Ensure you've correctly configured `src/firebase.js`
- Verify Firebase project settings
- Check that Email/Password authentication is enabled

### CORS Issues

If you encounter CORS errors, ensure the backend `api.py` has proper CORS configuration:
```python
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
```

## 📊 Data Sources

The platform analyzes UPI transaction data including:
- Aggregated transaction data
- User statistics
- Geographic mapping (state, district, pincode level)
- Transaction categories and payment modes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👥 Team

Developed as part of the Advanced Data Structures (ADS) course project.

## 📧 Contact

For queries or support, please reach out through the GitHub repository issues section.

---

**Finoro** - Empowering Digital Payment Insights 🚀
