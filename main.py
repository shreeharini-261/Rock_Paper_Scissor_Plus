import os
import json
import random
import google.genai as genai
from dotenv import load_dotenv
from prompts import INTENT_EXTRACTOR_PROMPT, GAME_JUDGE_PROMPT, RESPONSE_GENERATOR_PROMPT

# Load environment variables
load_dotenv()

class PurePromptAIJudge:
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file.\n"
                "Please create .env file with: GEMINI_API_KEY=your_key_here"
            )
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
        # Reset game state
        self.reset_game()
        
        print(f"🤖 Pure Prompt-Driven AI Judge Initialized")
        print(f"   Model: {model_name}")
        print(f"   State: Minimal (bomb_used: {self.bomb_used})")
        print("=" * 50)
    
    def reset_game(self):
        """Reset all game state to start fresh."""
        self.round_number = 1
        self.bomb_used = False       # User's bomb usage
        self.bot_bomb_used = False   # Bot's bomb usage
        self.user_score = 0
        self.bot_score = 0
        self.game_over = False
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        # Combine prompts as per Gemini's expected format
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Make API call
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt
        )
        
        return response.text.strip()
    
    def extract_intent(self, user_input: str) -> dict:
        
        print(f"[Intent Extraction] Processing: '{user_input}'")
        
        # Pure prompt call - no fallback
        response_text = self._call_gemini(
            system_prompt=INTENT_EXTRACTOR_PROMPT,
            user_prompt=f"User input: {user_input}\n\nExtract intent as JSON:"
        )
        
        # Clean and parse
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
        
        print(f"[Intent Extraction] Result: {result}")
        return result
    
    def judge_round(self, user_move: str, bot_move: str) -> dict:
        
        print(f"[Game Judge] Evaluating: {user_move} vs {bot_move}")
        
        # Prepare context for the judge
        context = {
            "user_move": user_move,
            "bot_move": bot_move,
            "bomb_used_by_user": self.bomb_used,
            "round": self.round_number
        }
        
        # Pure prompt call - no fallback
        response_text = self._call_gemini(
            system_prompt=GAME_JUDGE_PROMPT,
            user_prompt=f"Game context: {json.dumps(context, indent=2)}\n\nJudge the round:"
        )
        
        # Clean and parse
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        decision = json.loads(clean_text)
        
        # Update bomb usage based on prompt's decision
        if decision.get("bomb_now_used"):
            self.bomb_used = True
        
        print(f"[Game Judge] Decision: {decision}")
        return decision
    
    def generate_response(self, round_data: dict) -> str:
        
        print("[Response Generator] Creating user output")
        
        # Pure prompt call - no fallback
        response_text = self._call_gemini(
            system_prompt=RESPONSE_GENERATOR_PROMPT,
            user_prompt=f"Game data: {json.dumps(round_data, indent=2)}\n\nGenerate response:"
        )
        
        clean_text = response_text.replace("```", "").strip()
        print(f"[Response Generator] Output length: {len(clean_text)} chars")
        return clean_text
    
    def get_bot_move(self) -> str:
        
        # Bot can use bomb once per game with 12% probability
        if not self.bot_bomb_used and random.random() < 0.12:
            self.bot_bomb_used = True
            print(f"[System] Bot chose: bomb (bot bomb now used)")
            return "bomb"
        
        move = random.choice(["rock", "paper", "scissors"])
        print(f"[System] Bot chose: {move}")
        return move
    
    def update_scores(self, winner: str) -> bool:
        
        if winner == "USER":
            self.user_score += 1
        elif winner == "BOT":
            self.bot_score += 1
        
        # Check if game is over (first to 3 wins)
        if self.user_score >= 3 or self.bot_score >= 3:
            self.game_over = True
            return True
        return False
    
    def get_winner_announcement(self) -> str:
        
        if self.user_score >= 3:
            return "\n" + "🎉" * 12 + "\n🎉 YOU WIN THE GAME! 🎉\n" + "🎉" * 12
        elif self.bot_score >= 3:
            return "\n" + "🤖" * 12 + "\n🤖 BOT WINS THE GAME! 🤖\n" + "🤖" * 12
        return ""
    
    def execute_round(self, user_input: str) -> tuple[str, bool]:
        
        print(f"\n{'='*50}")
        print(f"ROUND {self.round_number}")
        print(f"{'='*50}")
        
        #LAYER 1: INTENT EXTRACTION 
        intent_data = self.extract_intent(user_input)
        user_move = intent_data.get("intent", "unclear")
        
        #BOT MOVE (only hardcoded part)
        bot_move = self.get_bot_move()
        print(f"[System] Bot randomly chose: {bot_move}")
        
        #LAYER 2: GAME JUDGING 
        judgment = self.judge_round(user_move, bot_move)
        
        # Complete round data
        round_data = {
            "round": self.round_number,
            "user_move": user_move,
            "bot_move": bot_move,
            "status": judgment.get("status", "UNCLEAR"),
            "winner": judgment.get("winner", "NONE"),
            "reason": judgment.get("reason", "No explanation provided"),
            "bomb_now_used": judgment.get("bomb_now_used", False)
        }
        
        #UPDATE STATE
        game_over = self.update_scores(judgment.get("winner", "NONE"))
        self.round_number += 1
        
        # LAYER 3: RESPONSE GENERATION 
        round_result = self.generate_response(round_data)
        
        return round_result, game_over
    
    def get_game_summary(self) -> dict:
        
        return {
            "rounds_played": self.round_number - 1,
            "user_score": self.user_score,
            "bot_score": self.bot_score,
            "bomb_used": self.bomb_used,
            "game_over": self.game_over
        }


def main():
    
    
    print("🤖 ROCK-PAPER-SCISSORS PLUS - AI JUDGE")
    print("=" * 50)
    print("ASSIGNMENT: Pure Prompt-Driven System")
    print("=" * 50)
    print("RULES:")
    print("  • Valid moves: rock, paper, scissors, bomb")
    print("  • Bomb beats everything")
    print("  • Bomb can be used only ONCE per game")
    print("  • Unclear/invalid moves waste your turn")
    print("  • First to 3 wins takes the match!")
    print("=" * 50)
    print("COMMANDS:")
    print("  • Enter your move in natural language")
    print("  • Type 'summary' to see game stats")
    print("  • Type 'reset' to start new game")
    print("  • Type 'quit' to exit")
    print("=" * 50)
    print("⚠️  SYSTEM DESIGN:")
    print("  • 3-layer architecture (Intent → Judge → Response)")
    print("  • All game rules in prompts")
    print("  • Minimal state management")
    print("=" * 50)
    
    # Initialize judge
    try:
        judge = PurePromptAIJudge(model_name="gemini-2.0-flash")
    except ValueError as e:
        print(f"\n {e}")
        return
    except Exception as e:
        print(f"\n Failed to initialize: {e}")
        return
    
    # Game loop
    while True:
        try:
            if judge.game_over:
                print(judge.get_winner_announcement())
                print(f"\n🏆 Game complete in {judge.round_number - 1} rounds!")
                print("Commands: 'reset' (new game), 'summary' (stats), 'quit' (exit)")
                
                # Post-game command loop
                while True:
                    command = input("\nEnter command: ").strip().lower()
                    
                    if command == 'quit':
                        break
                    elif command == 'summary':
                        summary = judge.get_game_summary()
                        print(f"\n📊 FINAL GAME SUMMARY:")
                        print(f"   Rounds: {summary['rounds_played']}")
                        print(f"   Your wins: {summary['user_score']}")
                        print(f"   Bot wins: {summary['bot_score']}")
                        print(f"   Bomb used: {summary['bomb_used']}")
                    elif command == 'reset':
                        judge = PurePromptAIJudge(model_name="gemini-2.0-flash")
                        print("\n🔄 New game started!")
                        break  # Exit post-game loop
                    else:
                        print("Invalid. Use: reset, summary, or quit")
                        continue
                
                if command == 'quit':
                    break  # Exit main game loop
                else:
                    continue  # New game started, skip to next iteration
            
            # Get user input for move
            prompt = f"\n[Round {judge.round_number}] Enter your move: "
            user_input = input(prompt).strip()
            
            # Handle commands
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'summary':
                summary = judge.get_game_summary()
                print(f"\n📊 GAME SUMMARY:")
                print(f"   Rounds played: {summary['rounds_played']}")
                print(f"   Your score: {summary['user_score']}")
                print(f"   Bot score: {summary['bot_score']}")
                print(f"   Bomb used: {summary['bomb_used']}")
                continue
            elif user_input.lower() == 'reset':
                judge = PurePromptAIJudge(model_name="gemini-2.0-flash")
                print("\n🔄 Game reset. New game started!")
                continue
            elif not user_input:
                print("Please enter a move!")
                continue
            
            # Play round
            round_result, game_over = judge.execute_round(user_input)
            
            # Display round result
            print(f"\n{'='*30}")
            print("ROUND RESULT:")
            print(f"{'='*30}")
            print(round_result)
            
            # Show score
            print(f"\n📈 SCORE: You {judge.user_score} - {judge.bot_score} Bot")
            
            # Set game over flag if round ended game
            if game_over:
                judge.game_over = True
        
        except json.JSONDecodeError as e:
            print(f"\n❌ ERROR: Gemini returned invalid JSON")
            print(f"   This demonstrates pure system - no fallback!")
            print(f"   Error: {str(e)[:100]}...")
            continue
        except KeyboardInterrupt:
            print("\n\n👋 Game interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ SYSTEM FAILURE: {type(e).__name__}: {e}")
            print("   Pure prompt-driven system failed - as designed!")
            print("   No fallback logic to recover.")
            break


if __name__ == "__main__":
    main()