# Personal Activity Dashboard

A comprehensive Python dashboard for analyzing personal daily activity tracking data from `diaw.txt` files.

## Features

### 📊 Interactive Web Dashboard
- **Real-time data visualization** with Streamlit web interface
- **Multiple analysis tabs**: Overview, Time Analysis, Trends, Courses, Sleep
- **Interactive filtering** by date range and activity categories
- **Fall-themed color palette** matching the analysis notebook aesthetics

### 📈 Comprehensive Analytics
- **Activity categorization**: P=Productive, R=Routine, E=Eat, S=Social, W=Workout, F=Fun, GOD=God, LO=Sleep
- **Time allocation analysis** with pie charts and stacked bar graphs
- **Daily and weekly pattern recognition**
- **Sleep duration tracking** and trend analysis
- **Course-specific tracking** (ITSC vs hw ITSC, STAT vs hw STAT)

### 🎨 Visualization Types
- Time distribution pie charts
- Daily activity allocation bar charts
- Weekly pattern heatmaps
- Sleep trend line graphs
- Course comparison charts
- Activity intensity by hour

## Installation

1. **Set up Python environment**:
   ```bash
   cd "path/to/your/project"
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit plotly pandas numpy
   ```

## Usage

### Web Dashboard
1. **Start the dashboard**:
   ```bash
   streamlit run activity_dashboard.py
   ```

2. **Access the dashboard**:
   - Open your browser to `http://localhost:8501`
   - Upload your `diaw.txt` file or place it in the same directory
   - Use the sidebar filters to customize your analysis

### Data Format
Your `diaw.txt` file should follow this format:

```
7/24/25 Th 0830-0040
0030 LO lo
0025 S comm
0020 R br
0015 P notes
0000 F yt
2345 P school
...
```

**Format specifications**:
- **Day headers**: `M/D/YY DayOfWeek StartTime-EndTime`
- **Activity records**: `HHMM Category Description`
- **Categories**: P, R, E, S, W, F, GOD, LO (see legend above)

## Dashboard Sections

### 📊 Overview Tab
- Activity category distribution pie chart
- Activity count by category bar chart
- Category summary statistics table

### ⏰ Time Analysis Tab
- Daily time allocation by category
- Stacked daily time view
- Interactive time allocation charts

### 📈 Trends Tab
- Weekly activity patterns
- Time of day heatmap
- Activity intensity analysis

### 🎓 Courses Tab
- Course-specific time tracking
- ITSC vs homework comparison
- STAT vs homework comparison
- Pattern matching analysis

### 😴 Sleep Tab
- Sleep duration distribution histogram
- Sleep statistics and metrics
- Sleep trend analysis over time

## Based On
This dashboard is based on the comprehensive analysis methodology from `activity_analysis.ipynb`, including:
- Data parsing and duration calculation algorithms
- Fall-themed visualization color schemes
- Activity categorization system
- Sleep analysis methodology

## Technical Details
- **Framework**: Streamlit for web interface
- **Visualization**: Plotly for interactive charts
- **Data Processing**: Pandas and NumPy
- **Caching**: Streamlit's @st.cache_data for performance
- **Color Scheme**: Fall-themed palette with dark compatibility

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all dependencies are installed in your virtual environment
2. **File not found**: Place `diaw.txt` in the same directory as the script
3. **Date parsing errors**: Verify your date format matches M/D/YY
4. **Empty visualizations**: Check that your activity categories match the expected codes

### Performance Tips
- Use date range filters for large datasets
- The dashboard caches parsed data for faster reloading
- Consider filtering categories for focused analysis

## Example Analysis Outputs
- Daily time allocation showing 8+ hours of productive activities
- Weekly patterns revealing productivity peaks
- Sleep analysis showing average 7-8 hours per night
- Course tracking showing homework vs lecture time ratios

## Future Enhancements
- Export functionality for charts and data
- Comparison between different time periods
- Goal setting and progress tracking
- Mobile-responsive design improvements

---

## 🚀 Sharing & Deployment Guide

### Will the dashboard stay running?
**NO** - The Streamlit dashboard will stop when:
- ❌ You close the terminal window
- ❌ Your computer goes to sleep or shuts down
- ❌ You run `pkill -f streamlit`

**To keep it running locally:**
```bash
# Run in background (keeps running even if terminal closes)
nohup streamlit run activity_dashboard.py --server.headless true &

# Stop it later with:
pkill -f streamlit
```

### 📤 How Others Can View Your Dashboard

#### Option 1: Streamlit Community Cloud (RECOMMENDED ⭐)
**Best for:** Permanent hosting, sharing with anyone worldwide

**Steps:**
1. **Create GitHub account** at https://github.com (if you don't have one)

2. **Push your project to GitHub:**
   ```bash
   cd "/Users/kamonwhiteside/Downloads/pythonics/Prod Program ai3"
   
   # Initialize git (if not already done)
   git init
   git add activity_dashboard.py diaw.txt requirements.txt README.md
   git commit -m "Initial commit: Personal Time Tracker"
   git branch -M main
   
   # Create a new repo on GitHub, then connect it:
   git remote add origin https://github.com/YOUR_USERNAME/time-tracker.git
   git push -u origin main
   ```

3. **Deploy to Streamlit Cloud:**
   - Visit https://share.streamlit.io
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Main file: `activity_dashboard.py`
   - Click "Deploy"!

4. **Share your URL:** You'll get something like:
   `https://your-username-time-tracker.streamlit.app`

**Benefits:**
- ✅ FREE forever
- ✅ Works 24/7 (no need to keep computer on)
- ✅ Automatic updates when you push to GitHub
- ✅ Share with anyone via URL

**Privacy Note:** ⚠️ Your data will be public unless you use a private GitHub repo (requires GitHub Pro)

---

#### Option 2: Local Network (Same WiFi Only)
**Best for:** Showing to people on your WiFi without internet

While the dashboard is running on your computer, others can access it at:
- **Network URL**: `http://192.168.1.97:8501` (from terminal output)

**Benefits:**
- ✅ FREE
- ✅ Data stays on your computer
- ✅ No setup needed

**Limitations:**
- ⚠️ Only works on same WiFi network
- ⚠️ Your computer must stay on
- ⚠️ IP address may change if you restart WiFi

---

#### Option 3: ngrok (Temporary Public Access)
**Best for:** Quick demos or temporary sharing (a few hours/days)

1. **Install ngrok:** https://ngrok.com/download

2. **Run ngrok:**
   ```bash
   ngrok http 8501
   ```

3. **Share the URL** ngrok gives you (e.g., `https://abc123.ngrok.io`)

**Benefits:**
- ✅ Quick setup (2 minutes)
- ✅ Anyone can access via internet
- ✅ Free tier available

**Limitations:**
- ⚠️ URL changes every time you restart ngrok
- ⚠️ Your computer must stay on
- ⚠️ Free tier has limitations

---

#### Option 4: Cloud Hosting (Advanced)
**Best for:** Professional deployments with full control

Deploy to cloud platforms:
- **Heroku** (easiest cloud option)
- **AWS/Google Cloud** (most powerful)
- **DigitalOcean** (good balance)
- **PythonAnywhere** (Python-focused)

**Requires:** Docker knowledge, credit card, technical setup

---

### 🎯 Recommended: Streamlit Cloud

For sharing with others, **Streamlit Community Cloud is the best option** because:
1. It's completely FREE
2. Works 24/7 without your computer
3. Easy to update (just push to GitHub)
4. Professional-looking URL
5. Takes only 5 minutes to set up

### 📝 Quick Start Commands

```bash
# Check if git is installed
git --version

# If not, install git (macOS with Homebrew)
brew install git

# Navigate to your project
cd "/Users/kamonwhiteside/Downloads/pythonics/Prod Program ai3"

# Make sure requirements.txt exists
ls requirements.txt

# Initialize and push to GitHub
git init
git add .
git commit -m "Add Personal Time Tracker Dashboard"
git branch -M main

# Create a new repository on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main

# Then deploy on Streamlit Cloud (via website)
# Visit: https://share.streamlit.io
```

---

### 🔒 Privacy Considerations

Your `diaw.txt` contains personal activity data. Before sharing:

1. **Review your data** - Make sure you're okay with others seeing it
2. **Use private GitHub repos** if you want to restrict access
3. **Remove sensitive descriptions** from diaw.txt if needed
4. **Consider sample data** for public demos

---

### ❓ FAQ

**Q: Will it cost money?**
A: Streamlit Cloud is free for public repos. Private repos may require GitHub Pro ($4/month).

**Q: Can I password-protect it?**
A: Streamlit Cloud doesn't have built-in auth, but you can add custom authentication code.

**Q: What if I update my data?**
A: Just push changes to GitHub - Streamlit Cloud auto-updates!

**Q: Can I use my own domain?**
A: Not on the free tier, but you get a nice streamlit.app subdomain.

---

## 📧 Support

Questions? Issues? Open an issue on GitHub or reach out!