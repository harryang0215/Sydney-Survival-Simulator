"""Sydney Survival Simulator - a 30-day student-life decision adventure.

Run: python3 main.py
Uses only the Python standard library (no installations needed).
"""

from game import Game, Player, DESTINATIONS
from storage import save_game, load_game, SaveError


def ask_option(prompt, valid_options):
    """Week 8 Advanced: try/except, raise, break, continue.

    Continues to ask until the user provides a valid response.
    """
    while True:
        try:
            answer = input(prompt).strip()
            if answer not in valid_options:
                raise ValueError("Please enter: " + ", ".join(valid_options))
            break
        except ValueError as error:
            print("Input error:", error)
            continue
    return answer


def start_new_game():
    """Ask for a name, then initialise a fresh city-life story."""
    while True:
        name = input("What is your name? ").strip()
        if 1 <= len(name) <= 32:
            return Game(Player(name))
        print("Please enter a name between 1 and 32 characters.")


def show_rules():
    print("\nHOW TO PLAY")
    print("Survive 30 days as a new international student in Sydney.")
    print("One main action per day. Events sometimes offer extra choices.")
    print("Study at Fisher Library, work shifts, buy food, rest and explore.")
    print("Every day uses one pantry meal. Rent is $410 every 7 days.")
    print("If you run out of energy or owe over $450, you lose early.")
    print("To win after 30 days, reach: Study 65+, Energy 20+,")
    print("Happiness 20+, and Money $0+. Aim higher for a special ending!")
    print("You can save and leave at any turn; resume from the main menu.\n")


def show_actions():
    print("\nTODAY'S PLAN")
    print("  1. Study at Fisher Library   (+14 study, -11 energy)")
    print("  2. Work a cafe shift        (+$180, -16 energy)")
    print("  3. Buy weekly groceries     (-$65, +6 meals)")
    print("  4. Rest at home             (+30 energy, +7 happiness)")
    print("  5. Explore Sydney           (choose a destination)")
    print("  6. Save and return to menu")
    print("  7. Read survival rules")


def choose_destination():
    print("\nWHERE TO GO?")
    for key, (place, price, joy, _, _) in DESTINATIONS.items():
        print(f"  {key}. {place}  (-${price}, +{joy} happiness)")
    return ask_option("Destination [1-3]: ", ("1", "2", "3"))


def play(game):
    """Main game loop. Each completed turn is automatically saved."""
    if game.finished:
        print(game.report())
        return

    while not game.finished:
        print(game.status())
        show_actions()
        choice = ask_option("Your choice [1-7]: ", tuple("1234567"))

        if choice == "7":
            show_rules()
            continue  # Don't use up a day to read the instructions.
        if choice == "6":
            try:
                save_game(game)
                print("Progress saved to sydney_save.json. See you soon!")
            except SaveError as error:
                print(error)
            return  # Premature return: go back to the main menu.

        destination = choose_destination() if choice == "5" else None
        try:
            message = game.perform_action(choice, destination)
        except ValueError as error:
            print("Action unavailable:", error)
            continue  # An impossible action never consumes a day.
        print("\n" + message)

        event = game.todays_event()
        if event is not None:
            print("\n*** RANDOM SYDNEY EVENT: " + event["title"] + " ***")
            print(event["story"])
            for index, (label, _) in enumerate(event["options"], start=1):
                print(f"  {index}. {label}")
            response = ask_option("What will you do? [1-2]: ", ("1", "2"))
            print("Result:", game.apply_event(event, response))

        for update in game.end_day():
            print("- " + update)

        try:
            save_game(game)
            print("[Autosaved]")
        except SaveError as error:
            print("Warning:", error)

    print(game.report())
    print("\nYour story is finished. Choose New Game to play again.")


def main():
    print("\nWELCOME TO SYDNEY SURVIVAL SIMULATOR!")
    print("Make choices. Manage your budget. Survive the semester.")
    while True:
        print("\nMAIN MENU")
        print("  1. New Game")
        print("  2. Continue Saved Game")
        print("  3. How to Play")
        print("  4. Quit")
        option = ask_option("Choose [1-4]: ", ("1", "2", "3", "4"))

        if option == "1":
            play(start_new_game())
        elif option == "2":
            try:
                play(load_game())
            except SaveError as error:
                print(error)
                print("You can start a new game instead.")
        elif option == "3":
            show_rules()
        else:
            print("Goodbye, and good luck in Sydney!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nSession closed. Your last completed day was autosaved.")
