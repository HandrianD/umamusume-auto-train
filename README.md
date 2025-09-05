# 🏇 Umamusume Auto Train - Advanced AI Edition

An **next-generation** automated training system for Umamusume Pretty Derby featuring **AI-like learning capabilities**, **intelligent event handling**, and **advanced energy management** that far surpasses the original implementations.

🚀 **This fork has evolved significantly beyond the original repositories** with sophisticated features not available elsewhere:

**Forked from**: [samsulpanjul/umamusume-auto-train](https://github.com/samsulpanjul/umamusume-auto-train)  
**Originally inspired by**: [shiokaze/UmamusumeAutoTrainer](https://github.com/shiokaze/UmamusumeAutoTrainer)

## 🏆 **What Makes This Fork Superior**

❌ **Original repositories lack**: Event learning, user intervention, personal preference tracking, energy-based event choices, advanced logging  
✅ **This fork provides**: All basic features PLUS advanced AI-like capabilities that learn and adapt to your playstyle!

[Demo video](https://youtu.be/CXSYVD-iMJk)

![Screenshot](screenshot.png)

# ⚠️ USE IT AT YOUR OWN RISK ⚠️

I am not responsible for any issues, account bans, or losses that may occur from using this automation tool.
Use responsibly and at your own discretion.

## ✨ **Exclusive Advanced Features**

### � **AI-Like Event Intelligence** (Not available in original!)
- **🎯 Intelligent Event Choice System** - Energy-based logic that automatically picks option 1 when energy < 80%
- **📚 Personal Learning System** - Learns from your manual choices and builds personal preferences
- **⏱️ User Intervention Timeout** - 20-second countdown for manual event decisions with real-time feedback
- **🔄 Session-based Learning** - Remembers your choices across multiple bot sessions
- **📊 Advanced Event Logging** - Comprehensive JSON logging with metadata, timestamps, and context tracking
- **🎲 Smart Defaults** - Intelligent fallback choices when no personal preference exists

### ⚡ **Advanced Energy Management** (Enhanced beyond original!)
- **🔍 Multi-Method Energy Detection** - Multiple algorithms for accurate energy level detection
- **📈 Dynamic Energy Thresholds** - Configurable never_rest_energy and skip_training_energy levels
- **🏥 Smart Infirmary Logic** - Enhanced skip_infirmary_unless_missing_energy system
- **⚖️ Energy-based Decision Making** - Event choices adapt based on current energy levels

### 🎯 **Enhanced Priority Weight System** (More advanced than original!)
- **📊 Advanced Priority Weights** - HEAVY/MEDIUM/LIGHT/NONE with custom multipliers [1.0, 0.8, 0.6, 0.5, 0.4]
- **🧮 Weighted Stat Scoring** - Sophisticated training score calculations with priority multipliers
- **🏆 Training Optimization** - Combines stat gains with priority weights and support card bonuses
- **📈 Dynamic Scoring** - Real-time calculation of optimal training choices

### 📝 **Comprehensive Data Collection** (Unique to this fork!)
- **🗄️ Event Data JSON Logging** - Complete event tracking in `event_data.json` with 8+ logged events
- **📊 Context Tracking** - Character data, support cards, training year, current stats
- **🎮 User Intervention Logging** - Tracks manual choices vs automated decisions
- **📈 Personal Learning Data** - Builds preference profiles for better future choices

## 🚀 **Core Automation** (All original features + enhancements!)

### 🤖 **Standard Features** (✅ All Present!)
- **Intelligent Training System** - Optimal training selection with support card analysis
- **Advanced Racing Logic** - Fan count goals with matching aptitude selection
- **Mood & Energy Management** - Enhanced mood monitoring and energy handling
- **Debuff Handling** - Automatic infirmary visits for debuffed characters
- **G1 Race Prioritization** - Smart G1 race selection for fan farming
- **Auto Skill Purchase** - Intelligent skill buying with custom skill lists

### 🎯 **Enhanced Training Features** (Improved beyond original!)
- **Stat Target System** - Skip training when stats meet target values
- **Rainbow Training Optimization** - Advanced multi-stat training detection
- **Enhanced Failure Rate Analysis** - Sophisticated risk assessment algorithms
- **Advanced Support Card Analysis** - Detailed support card presence and bonus calculation
- **Dynamic Training Logic** - Year-based strategy switching with fallback mechanisms
- **Smart Defaults** - Uses learned data to make optimal choices for unknown events

### 🗄️ Data Management & Scraping
- **Real-time Data Scraping** - On-demand scraping of missing character and support card data
- **Gametora Integration** - Scrapes event data from [gametora.com](https://gametora.com/)
- **Self-contained Scrapers** - Scrapers can work independently with web fallback
- **Standardized Data Format** - Consistent data structure across all scraped information
- **Data Validation** - Ensures scraped data quality and consistency

## 🏆 **Technical Excellence**

### 🔧 **Advanced Architecture** (2000+ lines of sophisticated code!)
- **🧠 Advanced State Management** - Comprehensive `core/state.py` with intelligent event handling
- **⚡ Enhanced Energy Detection** - Multiple detection methods with fallback mechanisms  
- **📊 Smart Event Processing** - Real-time event analysis with context awareness
- **🎯 Priority Weight Algorithms** - Advanced scoring with weighted multipliers
- **📝 Comprehensive Logging** - JSON-based event tracking with rich metadata
- **🔄 Session Persistence** - Data retention across bot restarts and sessions

### 🌐 **Modern Web Interface** (Enhanced beyond original!)
- **📱 Responsive Design** - Works on desktop and mobile browsers
- **⚙️ Advanced Configuration** - Fine-tune all bot parameters in real-time
- **🎨 Visual Selectors** - Character and support card selection with images  
- **📊 Priority Weight Controls** - Interactive priority weight and multiplier management
- **⚡ Energy Management UI** - Visual controls for energy thresholds and detection
- **🎯 Event Data Collection Settings** - Configure learning parameters and timeouts

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
- **Friend Support Cards** - During recreation, the bot cannot decide between dating friend support cards vs. the Uma character
- **Cant use Claw Machine** - The bot cannot utilize the claw machine mini-game for item acquisition
- **G1 Race Priority Override** - When `prioritize_g1_race` is enabled, the bot prioritizes racing even with low energy or after 3+ consecutive races

## 🎯 Roadmap & TODO

### ✅ **Completed Advanced Features** (Beyond Original!)
- ✅ **AI-like Event Learning System** - Personal preference tracking and smart defaults
- ✅ **User Intervention Timeout** - 20-second manual choice system with countdown
- ✅ **Energy-based Event Choices** - Automatically pick option 1 when energy < 80%
- ✅ **Advanced Priority Weight System** - HEAVY/MEDIUM/LIGHT/NONE with custom multipliers
- ✅ **Comprehensive Event Data Logging** - JSON logging with metadata and context
- ✅ **Enhanced Energy Management** - Multi-method detection with configurable thresholds
- ✅ **Session-based Learning** - Persistent learning across bot restarts
- ✅ **Real-time Event Context Tracking** - Character, support card, and stat awareness
- ✅ **Advanced Training Score Calculations** - Weighted priority scoring system
- ✅ **Personal Learning Data Collection** - Build preference profiles from manual choices

### ✅ **Standard Features** (All Original Features Present!)
- ✅ Prioritize G1 races for fan farming
- ✅ Auto-purchase skills system  
- ✅ Stat target feature with skip logic
- ✅ Web interface with visual selectors
- ✅ Advanced failure rate calculations
- ✅ Dynamic training logic switching
- ✅ Comprehensive error handling
- ✅ Support card event handling
- ✅ Enhanced mood management and thresholds
- ✅ Rainbow training optimization

### 🚧 **Features Not in Original** (Missing from base repository!)
- ❌ **Race Position Selection** - Only feature missing from original (6/7 basic features implemented)
- ❌ **Race Retry on Loss** - Feature doesn't exist in original either
- ❌ **Advanced Event Learning** - Original has basic event handling only
- ❌ **User Intervention System** - Original has no manual choice capability
- ❌ **Personal Preference Tracking** - Original cannot learn from user behavior

### 🔄 **In Progress** (Completing the final missing features!)
- 🔧 **Race Position Selection by Type** - Only remaining feature from original (sprint/mile/medium/long position selection)
- 🔧 **Web Interface Position Controls** - UI components for position management

### 📝 **Future Innovation Plans** (Beyond any existing implementations!)
- 🚀 **Advanced AI Event Prediction** - Predict optimal choices based on learning data  
- 🚀 **Performance Analytics Dashboard** - Detailed training session analysis and reporting
- 🚀 **Adaptive Training Strategies** - AI-driven strategy adjustment based on performance
- 🚀 **Multi-Character Learning Transfer** - Apply learned preferences across different characters
- 🚀 **Predictive Energy Management** - Forecast energy needs for optimal planning
- 🚀 **Smart Goal Detection** - Automatically adapt training based on changing objectives

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
