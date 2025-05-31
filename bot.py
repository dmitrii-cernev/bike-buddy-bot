import sqlite3
import logging
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_ACTION, ADDING_RIDE_WIZARD, RIDE_INPUT, ADDING_MAINTENANCE = range(4)

# Ride data fields
RIDE_FIELDS = {
    "📏 Distance": "distance",
    "⚡ Avg Speed": "avg_speed", 
    "🚀 Max Speed": "max_speed",
    "💓 Avg Pulse": "avg_pulse",
    "💥 Max Pulse": "max_pulse", 
    "⏱️ Duration": "duration",
    "📝 Notes": "notes"
}

class BikeBot:
    def __init__(self, token):
        self.token = token
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with tables for rides and maintenance"""
        conn = sqlite3.connect('bike_activities.db')
        cursor = conn.cursor()
        
        # Create rides table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                distance REAL NOT NULL,
                avg_speed REAL,
                max_speed REAL,
                avg_pulse INTEGER,
                max_pulse INTEGER,
                duration TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create maintenance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_ride(self, data):
        """Add a new ride to the database"""
        conn = sqlite3.connect('bike_activities.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rides (date, distance, avg_speed, max_speed, avg_pulse, max_pulse, duration, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        
        conn.commit()
        conn.close()
    
    def add_maintenance(self, date, activity_type, notes=""):
        """Add maintenance activity to the database"""
        conn = sqlite3.connect('bike_activities.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO maintenance (date, activity_type, notes)
            VALUES (?, ?, ?)
        ''', (date, activity_type, notes))
        
        conn.commit()
        conn.close()
    
    def get_recent_rides(self, limit=5):
        """Get recent rides from database"""
        conn = sqlite3.connect('bike_activities.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, distance, avg_speed, duration
            FROM rides
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rides = cursor.fetchall()
        conn.close()
        return rides
    
    def get_recent_maintenance(self, limit=5):
        """Get recent maintenance activities"""
        conn = sqlite3.connect('bike_activities.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, activity_type, notes
            FROM maintenance
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        maintenance = cursor.fetchall()
        conn.close()
        return maintenance

# Initialize bot instance
bike_bot = BikeBot(os.getenv("TELEGRAM_BOT_TOKEN"))

def get_ride_wizard_keyboard(ride_data):
    """Generate keyboard for ride wizard based on what's already filled"""
    available_fields = []
    
    for display_name, field_key in RIDE_FIELDS.items():
        if field_key not in ride_data:
            available_fields.append(KeyboardButton(display_name))
    
    # Create keyboard with 2 buttons per row
    keyboard = []
    for i in range(0, len(available_fields), 2):
        row = available_fields[i:i+2]
        keyboard.append(row)
    
    # Add control buttons
    control_buttons = []
    if ride_data:  # Only show Done if some data is entered
        control_buttons.append(KeyboardButton("✅ Done"))
    control_buttons.append(KeyboardButton("❌ Cancel"))
    
    if control_buttons:
        keyboard.append(control_buttons)
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def format_current_ride_data(ride_data):
    """Format current ride data for display"""
    if not ride_data:
        return "No data entered yet."
    
    message = "Current ride data:\n"
    field_display = {
        "distance": "📏 Distance: {} km",
        "avg_speed": "⚡ Avg Speed: {} km/h",
        "max_speed": "🚀 Max Speed: {} km/h", 
        "avg_pulse": "💓 Avg Pulse: {} bpm",
        "max_pulse": "💥 Max Pulse: {} bpm",
        "duration": "⏱️ Duration: {}",
        "notes": "📝 Notes: {}"
    }
    
    for field, value in ride_data.items():
        if field in field_display:
            message += field_display[field].format(value) + "\n"
    
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    keyboard = [
        [KeyboardButton("🚴 Add New Ride"), KeyboardButton("🔧 Add Maintenance")],
        [KeyboardButton("📊 View Recent Rides"), KeyboardButton("🛠️ View Maintenance")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Initialize user context
    context.user_data.clear()
    
    await update.message.reply_text(
        "Welcome to your Bike Activity Tracker! 🚴‍♂️\n\n"
        "What would you like to do?",
        reply_markup=reply_markup
    )
    return CHOOSING_ACTION

async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu choices"""
    text = update.message.text
    
    if text == "🚴 Add New Ride":
        context.user_data['ride_data'] = {}
        context.user_data['current_field'] = None
        
        keyboard = get_ride_wizard_keyboard({})
        await update.message.reply_text(
            "Let's add a new ride! 🚴‍♂️\n\n"
            "What would you like to add first?",
            reply_markup=keyboard
        )
        return ADDING_RIDE_WIZARD
    
    elif text == "🔧 Add Maintenance":
        keyboard = [
            [KeyboardButton("🔗 Chain Lubrication"), KeyboardButton("🛞 Tire Pressure")],
            [KeyboardButton("🛑 Brake Adjustment"), KeyboardButton("🧽 General Cleaning")],
            [KeyboardButton("🔧 Other"), KeyboardButton("❌ Cancel")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "What maintenance did you perform?",
            reply_markup=reply_markup
        )
        return ADDING_MAINTENANCE
    
    elif text == "📊 View Recent Rides":
        rides = bike_bot.get_recent_rides()
        if rides:
            message = "🚴 Recent Rides:\n\n"
            for ride in rides:
                date, distance, avg_speed, duration = ride
                message += f"📅 {date}\n"
                message += f"📏 Distance: {distance} km\n"
                if avg_speed:
                    message += f"⚡ Avg Speed: {avg_speed} km/h\n"
                if duration:
                    message += f"⏱️ Duration: {duration}\n"
                message += "─────────────\n"
        else:
            message = "No rides recorded yet. Add your first ride! 🚴‍♂️"
        
        await update.message.reply_text(message)
        return CHOOSING_ACTION
    
    elif text == "🛠️ View Maintenance":
        maintenance = bike_bot.get_recent_maintenance()
        if maintenance:
            message = "🔧 Recent Maintenance:\n\n"
            for item in maintenance:
                date, activity_type, notes = item
                message += f"📅 {date}\n"
                message += f"🔧 {activity_type}\n"
                if notes:
                    message += f"📝 {notes}\n"
                message += "─────────────\n"
        else:
            message = "No maintenance records yet. Time to service your bike! 🔧"
        
        await update.message.reply_text(message)
        return CHOOSING_ACTION

async def handle_ride_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ride wizard field selection"""
    text = update.message.text
    ride_data = context.user_data.get('ride_data', {})
    
    if text == "✅ Done":
        if 'distance' not in ride_data:
            await update.message.reply_text(
                "⚠️ Distance is required! Please add distance before finishing.",
                reply_markup=get_ride_wizard_keyboard(ride_data)
            )
            return ADDING_RIDE_WIZARD
        
        # Save ride to database
        today = datetime.now().strftime("%Y-%m-%d")
        db_data = (
            today,
            ride_data.get('distance'),
            ride_data.get('avg_speed'),
            ride_data.get('max_speed'), 
            ride_data.get('avg_pulse'),
            ride_data.get('max_pulse'),
            ride_data.get('duration'),
            ride_data.get('notes')
        )
        
        bike_bot.add_ride(db_data)
        
        # Return to main menu
        keyboard = [
            [KeyboardButton("🚴 Add New Ride"), KeyboardButton("🔧 Add Maintenance")],
            [KeyboardButton("📊 View Recent Rides"), KeyboardButton("🛠️ View Maintenance")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        summary = format_current_ride_data(ride_data)
        await update.message.reply_text(
            f"✅ Ride saved successfully!\n\n{summary}\n"
            "What would you like to do next?",
            reply_markup=reply_markup
        )
        
        context.user_data.clear()
        return CHOOSING_ACTION
    
    elif text == "❌ Cancel":
        keyboard = [
            [KeyboardButton("🚴 Add New Ride"), KeyboardButton("🔧 Add Maintenance")],
            [KeyboardButton("📊 View Recent Rides"), KeyboardButton("🛠️ View Maintenance")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Ride cancelled. What would you like to do?",
            reply_markup=reply_markup
        )
        
        context.user_data.clear()
        return CHOOSING_ACTION
    
    # Check if user selected a field to add
    selected_field = None
    for display_name, field_key in RIDE_FIELDS.items():
        if text == display_name:
            selected_field = field_key
            break
    
    if selected_field:
        context.user_data['current_field'] = selected_field
        
        # Provide specific instructions based on field
        field_instructions = {
            "distance": "Please enter the distance in kilometers (e.g., 25.5):",
            "avg_speed": "Please enter average speed in km/h (e.g., 22.3):",
            "max_speed": "Please enter maximum speed in km/h (e.g., 45.2):",
            "avg_pulse": "Please enter average pulse in bpm (e.g., 145):",
            "max_pulse": "Please enter maximum pulse in bpm (e.g., 180):",
            "duration": "Please enter duration (e.g., 1:30 or 90 minutes):",
            "notes": "Please enter any notes about the ride:"
        }
        
        current_data = format_current_ride_data(ride_data)
        await update.message.reply_text(
            f"{current_data}\n\n{field_instructions.get(selected_field, 'Please enter the value:')}",
            reply_markup=ReplyKeyboardRemove()
        )
        return RIDE_INPUT
    
    # Invalid selection
    await update.message.reply_text(
        "Please select a field to add or choose Done/Cancel.",
        reply_markup=get_ride_wizard_keyboard(ride_data)
    )
    return ADDING_RIDE_WIZARD

async def handle_ride_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user input for ride field values"""
    text = update.message.text.strip()
    current_field = context.user_data.get('current_field')
    ride_data = context.user_data.get('ride_data', {})
    
    if not current_field:
        await update.message.reply_text("Something went wrong. Let's start over.")
        return await start(update, context)
    
    try:
        # Parse input based on field type
        if current_field in ['distance', 'avg_speed', 'max_speed']:
            value = float(text)
        elif current_field in ['avg_pulse', 'max_pulse']:
            value = int(text)
        else:
            value = text
        
        # Store the value
        ride_data[current_field] = value
        context.user_data['ride_data'] = ride_data
        context.user_data['current_field'] = None
        
        # Return to wizard with updated keyboard
        keyboard = get_ride_wizard_keyboard(ride_data)
        current_data = format_current_ride_data(ride_data)
        
        await update.message.reply_text(
            f"✅ Added!\n\n{current_data}\n\nWhat would you like to add next?",
            reply_markup=keyboard
        )
        
        return ADDING_RIDE_WIZARD
        
    except ValueError:
        field_name = [k for k, v in RIDE_FIELDS.items() if v == current_field][0]
        await update.message.reply_text(
            f"Invalid input for {field_name}. Please enter a valid number."
        )
        return RIDE_INPUT

async def add_maintenance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle maintenance activity selection"""
    text = update.message.text.strip()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if text == "❌ Cancel":
        keyboard = [
            [KeyboardButton("🚴 Add New Ride"), KeyboardButton("🔧 Add Maintenance")],
            [KeyboardButton("📊 View Recent Rides"), KeyboardButton("🛠️ View Maintenance")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "Maintenance cancelled. What would you like to do?",
            reply_markup=reply_markup
        )
        return CHOOSING_ACTION
    
    # Map button text to activity names
    activity_map = {
        "🔗 Chain Lubrication": "Chain Lubrication",
        "🛞 Tire Pressure": "Tire Pressure Check", 
        "🛑 Brake Adjustment": "Brake Adjustment",
        "🧽 General Cleaning": "General Cleaning",
        "🔧 Other": "Other Maintenance"
    }
    
    activity_type = activity_map.get(text, text)
    bike_bot.add_maintenance(today, activity_type)
    
    # Return to main menu
    keyboard = [
        [KeyboardButton("🚴 Add New Ride"), KeyboardButton("🔧 Add Maintenance")],
        [KeyboardButton("📊 View Recent Rides"), KeyboardButton("🛠️ View Maintenance")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ Maintenance logged successfully!\n\n"
        f"📅 Date: {today}\n"
        f"🔧 Activity: {activity_type}\n\n"
        "What would you like to do next?",
        reply_markup=reply_markup
    )
    
    return CHOOSING_ACTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    keyboard = [
        [KeyboardButton("🚴 Add New Ride"), KeyboardButton("🔧 Add Maintenance")],
        [KeyboardButton("📊 View Recent Rides"), KeyboardButton("🛠️ View Maintenance")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Operation cancelled. What would you like to do?",
        reply_markup=reply_markup
    )
    context.user_data.clear()
    return CHOOSING_ACTION

def main():
    """Main function to run the bot"""
    # Get token from environment variable
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with: TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_choice)],
            ADDING_RIDE_WIZARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ride_wizard)],
            RIDE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ride_input)],
            ADDING_MAINTENANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_maintenance_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Start the bot
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
