# **AI Judge for Rock-Paper-Scissors Plus** 🤖🎮

*A pure prompt-driven AI system for judging Rock-Paper-Scissors Plus moves*

## 📋 Assignment Overview

This project implements a **pure prompt-driven AI Judge** for a Rock-Paper-Scissors Plus game. The system evaluates user inputs against game rules and provides structured decisions with clear explanations.

## 🏗️ System Architecture
    User Input (free text)
    ↓
    [Layer 1: Intent Extractor]
    ↓
    Structured Intent (JSON)
    ↓
    [Layer 2: Game Judge]
    ↓
    Structured Decision (JSON)
    ↓
    [Layer 3: Response Generator]
    ↓
    User-Friendly Output

## 🎮 Game Rules

- **Valid moves**: rock, paper, scissors, bomb
- **Bomb constraint**: Can be used only ONCE per player per game
- **Bomb power**: Beats everything (rock, paper, scissors)
- **Draw condition**: Bomb vs bomb = draw
- **Turn penalty**: Unclear or invalid moves waste the turn (bot wins)
- **Winning condition**: First to 3 wins takes the match

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key (free tier from [makersuite.google.com](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone or create project directory
mkdir ai-judge-rps-plus
cd ai-judge-rps-plus

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install google-genai python-dotenv

# Create .env file with your API key
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env 
```

### 🎮 How to Play
In-Game Commands

    Enter moves: Natural language like "I throw a rock", "paper please", "bomb explosion"
    summary: Show current game statistics
    reset: Start a new game
    quit: Exit the game

## 🛠️ Technical Implementation
Prompt Design Philosophy

    Self-contained logic: Each prompt contains all necessary rules
    Structured output: Enforced JSON formats between layers
    Error handling: No fallback logic - pure prompt-driven system
    Extensibility: New rules can be added by editing prompts only

## Minimal State Management

    Only tracks bomb_used (as permitted by assignment)
    No database, no external APIs
    Simple scoring: first to 3 wins

## Robust Intent Extraction

    Handles typos: "ruck" → rock, "scisor" → scissors
    Recognizes synonyms: "stone" → rock, "blast" → bomb
    Properly marks ambiguous inputs as "unclear"

## Edge Cases Handled

    Bomb reuse: Second bomb attempt marked INVALID
    Unclear moves: Gibberish or ambiguous inputs waste turn
    Synonyms: Natural language variations recognized
    Typos: Minor spelling mistakes still understood
    Bomb vs bomb: Correctly results in draw
    Game end: Proper winner announcement and reset flow

## 🤔 Design Trade-offs

    Bot bomb usage: Simplified (once per game, low probability)
    Minimal UI: Command-line interface meets requirements

## 📫 Connect

    LinkedIn: https://linkedin.com/in/shreeharini-s

Note: This project uses Google Gemini API (free tier). Ensure you have an API key from makersuite.google.com before running.
text

