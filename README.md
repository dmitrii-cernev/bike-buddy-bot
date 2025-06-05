# 🚴‍♂️ Bike Activity Tracker Bot

A simple and intuitive Telegram bot for tracking your cycling activities and bike maintenance. Log your rides with detailed metrics and keep track of maintenance activities - all through a friendly chat interface!

## ✨ Features

### 🚴 Ride Tracking
- **Step-by-step wizard** for easy data entry
- Track distance, speeds, heart rate, duration, and notes
- Flexible input - add only what you want to track
- View recent rides with formatted summaries

### 🔧 Maintenance Logging
- Quick buttons for common maintenance tasks
- Chain lubrication, tire pressure, brake adjustments, etc.
- Maintenance history tracking with timestamps

### 💾 Data Storage
- SQLite database for reliable local storage
- Persistent data across bot restarts
- All data stored locally on your server

### 🎯 User Experience
- Intuitive button-based navigation
- Real-time data preview during ride entry
- Clear instructions and validation
- Mobile-friendly interface

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone and setup:**
```bash
git clone https://github.com/dmitrii-cernev/bike-buddy-bot.git
cd bike-buddy-bot
```

2. **Create your bot token:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command and follow instructions
   - Copy your bot token

3. **Configure environment:**
```bash
# Create .env file
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
```

4. **Run with Docker:**
```bash
docker compose up --build
```

### Option 2: Local Python Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup environment:**
```bash
# Create .env file
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
```

3. **Run the bot:**
```bash
python bot.py
```

## 📱 How to Use

### Getting Started
1. Start a chat with your bot on Telegram
2. Send `/start` command
3. Use the menu buttons to navigate

### Adding a New Ride

1. **Tap "🚴 Add New Ride"**
2. **Choose what to track first** from the available options:
   - 📏 Distance (required)
   - ⚡ Avg Speed
   - 🚀 Max Speed  
   - 💓 Avg Pulse
   - 💥 Max Pulse
   - ⏱️ Duration
   - 📝 Notes

3. **Enter the value** when prompted:
   - Distance: `25.5` (km)
   - Speed: `22.3` (km/h)
   - Pulse: `145` (bpm)
   - Duration: `1:30` or `90 minutes`
   - Notes: Free text

4. **Continue adding fields** or tap "✅ Done" when finished

**Example Flow:**
```
🚴 Add New Ride
→ 📏 Distance → "25.5"
→ ⚡ Avg Speed → "22.3" 
→ ⏱️ Duration → "1:15"
→ ✅ Done
```

### Logging Maintenance

1. **Tap "🔧 Add Maintenance"**
2. **Select activity type:**
   - 🔗 Chain Lubrication
   - 🛞 Tire Pressure
   - 🛑 Brake Adjustment
   - 🧽 General Cleaning
   - 🔧 Other

3. **Activity is logged** with current date automatically

### Viewing Your Data

- **📊 View Recent Rides**: See your last 5 rides with key metrics
- **🛠️ View Maintenance**: Check recent maintenance activities

## 🏗️ Project Structure

```
bike-activity-tracker/
├── bot.py          # Main bot application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Docker deployment setup
├── .env               # Environment variables (create this)
├── data/              # SQLite database storage (auto-created)
└── README.md          # This file
```

## 🗄️ Database Schema

### Rides Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| date | TEXT | Ride date (YYYY-MM-DD) |
| distance | REAL | Distance in km (required) |
| avg_speed | REAL | Average speed in km/h |
| max_speed | REAL | Maximum speed in km/h |
| avg_pulse | INTEGER | Average heart rate in bpm |
| max_pulse | INTEGER | Maximum heart rate in bpm |
| duration | TEXT | Ride duration |
| notes | TEXT | Additional notes |
| created_at | TIMESTAMP | Record creation time |

### Maintenance Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| date | TEXT | Maintenance date (YYYY-MM-DD) |
| activity_type | TEXT | Type of maintenance performed |
| notes | TEXT | Additional notes |
| created_at | TIMESTAMP | Record creation time |

## 🐳 Docker Deployment

### Build and Run
```bash
# Build and start in background
docker compose up --build

# Stop the bot
docker compose down
```

### Data Persistence
- Database is stored in `./data/bike_activities.db`
- Data persists across container restarts
- Backup by copying the `data/` directory

## 🔧 Configuration

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather (required)

### Customization
You can modify the bot by editing `bot.py`:
- Add new ride fields in `RIDE_FIELDS` dictionary
- Modify maintenance activity types
- Adjust database schema
- Change button layouts and messages

## 📊 Example Usage Scenarios

**Daily Commuter:**
```
Distance: 12.5
Avg Speed: 18.5
Duration: 40 minutes
Notes: Morning commute, light traffic
```

**Weekend Warrior:**
```
Distance: 65.2
Avg Speed: 28.3
Max Speed: 52.1
Avg Pulse: 165
Duration: 2:18
Notes: Great ride through the hills!
```

**Maintenance Day:**
```
🔗 Chain Lubrication
→ Logged for today's date
```

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

---

**Happy Cycling! 🚴‍♂️🚴‍♀️**
