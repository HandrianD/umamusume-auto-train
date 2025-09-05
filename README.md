# 🏇 Umamusume Auto Train - Enhanced Edition

An advanced automated training system for Umamusume Pretty Derby with intelligent event handling, comprehensive data scraping, and a modern web interface.

This project is inspired by [shiokaze/UmamusumeAutoTrainer](https://github.com/shiokaze/UmamusumeAutoTrainer) and [samsulpanjul/umamusume-auto-train](https://github.com/samsulpanjul/umamusume-auto-train), with significant enhancements and new features.

[Demo video](https://youtu.be/CXSYVD-iMJk)

![Screenshot](screenshot.png)

# ⚠️ USE IT AT YOUR OWN RISK ⚠️

I am not responsible for any issues, account bans, or losses that may occur from using this automation tool.
Use responsibly and at your own discretion.

## ✨ Features

### 🤖 Core Automation
- **Intelligent Training System** - Automatically selects optimal training based on support cards and failure rates
- **Advanced Racing Logic** - Keeps racing until fan count meets goals, always picks races with matching aptitude
- **Mood & Energy Management** - Monitors character mood and handles low energy situations
- **Debuff Handling** - Automatically goes to infirmary when character has debuffs
- **G1 Race Prioritization** - Prioritizes G1 races for efficient fan farming
- **Smart Rest Logic** - Rests when training options are suboptimal

### 🎯 Advanced Training Features
- **Stat Target System** - Skip training stats that already meet target values
- **Rainbow Training Optimization** - Prioritizes multi-stat training opportunities
- **Failure Rate Analysis** - Calculates and avoids high-risk training sessions
- **Support Card Analysis** - Chooses training based on support card presence and bonuses
- **Dynamic Training Logic** - Switches between different strategies based on character year

### 🛒 Skill Management
- **Auto-Purchase Skills** - Automatically buys configured skills when skill points are available
- **Smart Skill Selection** - Prioritizes skills based on your custom skill list
- **Skill Point Monitoring** - Tracks skill points and purchases at optimal times

### 🌐 Modern Web Interface
- **Live Configuration** - Real-time configuration changes via web browser at `http://127.0.0.1:8000/`
- **Character Selection** - Browse and select from all available characters with images
- **Support Card Management** - Visual support card selection with filtering
- **Scenario Selection** - Choose from different training scenarios (URA, Aoharu, etc.)
- **Advanced Settings** - Fine-tune training parameters, mood thresholds, and stat caps

### 🧠 Intelligent Event System
- **OCR Event Reading** - Reads event text and makes intelligent choices
- **Event Data Collection** - Learns from events and improves future decision making
- **Character Event Database** - Comprehensive database of character-specific events
- **Support Card Event Database** - Database of support card events with optimal choices
- **Event Type Detection** - Distinguishes between different event types for better handling
- **Smart Defaults** - Uses learned data to make optimal choices for unknown events

### 🗄️ Data Management & Scraping
- **Real-time Data Scraping** - On-demand scraping of missing character and support card data
- **Gametora Integration** - Scrapes event data from [gametora.com](https://gametora.com/)
- **Self-contained Scrapers** - Scrapers can work independently with web fallback
- **Standardized Data Format** - Consistent data structure across all scraped information
- **Data Validation** - Ensures scraped data quality and consistency

### 🔧 Technical Enhancements
- **Modular Architecture** - Organized codebase with core modules in dedicated directory
- **FastAPI Backend** - Modern async web server for configuration and scraping
- **TypeScript Frontend** - Type-safe React frontend with modern UI components
- **Error Handling** - Comprehensive error handling and recovery mechanisms
- **Backward Compatibility** - Supports multiple data formats for seamless upgrades

## 🚀 Getting Started

### 📋 Requirements

- **Python 3.10+** - [Download here](https://www.python.org/downloads/)
- **Screen Resolution** - Must be 1920x1080
- **Game Settings** - Fullscreen mode required
- **Windows OS** - Tested on Windows 10/11

### ⚙️ Setup

#### 1. Clone Repository

```bash
git clone https://github.com/HandrianD/umamusume-auto-train
cd umamusume-auto-train
```

**Alternative:** Download the ZIP file and extract it, then open PowerShell in the extracted folder.

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Game Preparation

**IMPORTANT:** Make sure these conditions are met before starting:

- ✅ Screen resolution is exactly **1920x1080**
- ✅ Game is running in **fullscreen mode**
- ✅ Your Uma has already **won trophies** for races (bot skips races without trophies)
- ✅ All **confirmation pop-ups are disabled** in game settings
- ✅ Game is on the **career lobby screen** (with Tazuna hint icon visible)

### 🎮 Usage

#### Start the Bot

```bash
python main.py
```

#### Controls
- Press **F1** to start/stop the bot
- The bot will automatically handle training, racing, and events

#### Web Configuration
Open your browser and navigate to: **http://127.0.0.1:8000/**

The web interface allows you to:
- Select characters and support cards visually
- Configure training parameters
- Set stat targets and priority
- Enable/disable features
- Monitor event data collection

## 🧠 Training Logic

The bot uses sophisticated training algorithms with multiple strategies:

### 🎯 Primary Training Strategies

1. **Most Support Cards Strategy**
   - Trains in areas with the highest number of support cards
   - Maximizes stat gains through support bonuses
   - Prioritized during first year for rapid development

2. **Rainbow Training Strategy** 
   - Prioritizes multi-stat training opportunities
   - Activated when rainbow bonuses are available
   - Used from second year onwards for balanced growth

3. **Failure Rate Optimization**
   - Calculates failure probability for each training option
   - Avoids training when failure chance exceeds configured threshold
   - Dynamically adjusts based on character condition

### 🔄 Dynamic Logic Switching

- **Year 1 (Junior):** Focus on support card quantity for foundation building
- **Year 2+ (Classic/Senior):** Switch to rainbow training for optimal stat distribution
- **Fallback Logic:** If no rainbow training available, reverts to most support cards strategy

### 📊 Decision Making Process

The bot evaluates each training option based on:
- Number of support cards present
- Rainbow training availability  
- Failure rate probability
- Current stat caps and targets
- Character mood and energy levels

## 🌐 Web Interface Features

### 📱 Modern UI Components
- **Responsive Design** - Works on desktop and mobile browsers
- **Real-time Updates** - Configuration changes apply immediately
- **Visual Selectors** - Character and support card selection with images
- **Advanced Controls** - Fine-tune all bot parameters

### ⚙️ Configuration Options
- **Character Selection** - Browse all characters with filtering
- **Support Card Management** - Visual deck building interface
- **Training Parameters** - Mood thresholds, failure rates, stat caps
- **Event Settings** - Configure event data collection and learning
- **Skill Management** - Auto-buy skill configuration

## 🗃️ Data Management

### 📥 Scraping System
- **On-demand Scraping** - Automatically scrapes missing data when needed
- **Fallback Mechanisms** - Multiple data sources ensure reliability
- **Self-contained Operation** - Works independently without external files
- **Data Validation** - Ensures quality and consistency of scraped information

### 🎯 Event Intelligence
- **Learning System** - Improves decision making based on past events
- **Event Classification** - Distinguishes between character, support, and random events
- **Context Awareness** - Considers current stats, year, and support cards
- **Smart Defaults** - Provides optimal choices for unknown events

## ⚠️ Known Issues

- **Special Event Characters** - Some Uma with unique events/goals (e.g., Restricted Train Goldship, 2 G1 Race Oguri Cap) may not work optimally
- **OCR Misreading** - Failure chance might be misread (e.g., 33% read as 3%), causing the bot to proceed with risky training
- **Chain Event Handling** - Automatically picks the top option during chain events; be careful with Acupuncture events
- **Friend Support Cards** - During recreation, the bot cannot decide between dating friend support cards vs. the Uma character
- **G1 Race Priority Override** - When `prioritize_g1_race` is enabled, the bot prioritizes racing even with low energy or after 3+ consecutive races

## 🎯 Roadmap & TODO

### ✅ Completed Features
- ~~Prioritize G1 races for fan farming~~
- ~~Auto-purchase skills system~~
- ~~Stat target feature with skip logic~~
- ~~Web interface with visual selectors~~
- ~~Event data collection and learning~~
- ~~Modular scraping system~~

### 🔄 In Progress
- Energy level detection and management
- Race position selection by race type
- Priority weight system for stats
- Enhanced failure rate algorithms

### 📝 Future Plans
- **Claw Machine Automation** - Automate claw machine mini-games
- **Advanced Event Prediction** - ML-based event outcome prediction
- **Multi-scenario Optimization** - Scenario-specific training strategies
- **Performance Analytics** - Training session analysis and reporting

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
If you encounter issues or unexpected behavior:
1. Open an issue with detailed description
2. Include screenshots if possible
3. Specify your game version and settings

### 🔧 Development
- **Main Branch**: Stable releases
- **Development**: Check the [dev branch](https://github.com/HandrianD/umamusume-auto-train/tree/dev) for latest features
- **Pull Requests**: Always target the dev branch

### 💡 Feature Requests
- Open an issue with the "enhancement" label
- Describe the feature and its benefits
- Consider implementation complexity

## 📄 License & Credits

This project builds upon the excellent work of:
- [shiokaze/UmamusumeAutoTrainer](https://github.com/shiokaze/UmamusumeAutoTrainer)
- [samsulpanjul/umamusume-auto-train](https://github.com/samsulpanjul/umamusume-auto-train)

Special thanks to the Umamusume community and data providers at [gametora.com](https://gametora.com/).

---

### 🔔 Disclaimer

This tool is for educational and automation purposes. Use responsibly and in accordance with the game's terms of service. The developers are not responsible for any consequences resulting from the use of this software.
