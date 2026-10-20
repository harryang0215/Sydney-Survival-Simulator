"""Sydney Survival Simulator: game rules and city-life events.

COMP9001 concepts: classes, dictionaries, functions, random events,
advanced flow control, and modular program design.
"""

from dataclasses import dataclass, field
import random

TOTAL_DAYS = 30
WEEKLY_RENT = 410

DESTINATIONS = {
    "1": ("Bondi Beach", 22, 18, 8, 0),
    "2": ("Circular Quay", 35, 16, 7, 3),
    "3": ("Newtown", 18, 14, 6, 0),
}

# Each event is a Sydney student-life dilemma, not an automatic random penalty.
# effects: (money, energy, happiness, study, meals)
EVENTS = [
    {
        "title": "Sydney Rainstorm",
        "story": "It starts pouring just as you leave campus.",
        "options": [
            ("Buy a sturdy umbrella (-$20, +3 energy)", (-20, 3, 0, 0, 0)),
            ("Run through the rain (-12 energy)", (0, -12, 0, 0, 0)),
        ],
    },
    {
        "title": "Student Society Night",
        "story": "A campus society invites you to a social event.",
        "options": [
            ("Go along (-$15, +15 happiness)", (-15, -2, 15, 0, 0)),
            ("Stay and revise (+10 study, -4 happiness)", (0, -6, -4, 10, 0)),
        ],
    },
    {
        "title": "Extra Cafe Shift",
        "story": "Your manager asks if you can cover a short evening shift.",
        "options": [
            ("Accept (+$90, -13 energy)", (90, -13, -3, 0, 0)),
            ("Decline and recharge (+8 energy)", (0, 8, 2, 0, 0)),
        ],
    },
    {
        "title": "Surprise Class Quiz",
        "story": "You hear there is a short quiz tomorrow morning.",
        "options": [
            ("Cram tonight (+12 study, -10 energy)", (0, -10, -3, 12, 0)),
            ("Sleep early (+13 energy, -5 study)", (0, 13, 0, -5, 0)),
        ],
    },
    {
        "title": "Flatmate Dinner",
        "story": "Your flatmates are planning a shared dinner.",
        "options": [
            ("Contribute $25 (+16 happiness, +2 meals)", (-25, 0, 16, 0, 2)),
            ("Cook something simple (-$8, +2 meals)", (-8, -3, 3, 0, 2)),
        ],
    },
    {
        "title": "Light Rail Delay",
        "story": "The light rail stops unexpectedly on your way home.",
        "options": [
            ("Take a rideshare (-$28, +4 energy)", (-28, 4, 0, 0, 0)),
            ("Wait for the next service (-9 energy)", (0, -9, 0, 0, 0)),
        ],
    },
    {
        "title": "Free Campus Workshop",
        "story": "An interesting practical workshop has one place left.",
        "options": [
            ("Join (+9 study, -5 energy)", (0, -5, 3, 9, 0)),
            ("Take personal time (+9 happiness)", (0, 2, 9, 0, 0)),
        ],
    },
    {
        "title": "Market Bargain",
        "story": "A nearby market has discounted food bundles today.",
        "options": [
            ("Buy supplies (-$40, +4 meals)", (-40, -2, 2, 0, 4)),
            ("Save your cash (+3 happiness)", (0, 0, 3, 0, 0)),
        ],
    },
]


@dataclass
class Player:
    """Data for one international student."""

    name: str
    money: int = 1350
    energy: int = 85
    happiness: int = 68
    study: int = 10
    meals: int = 4

    def change(self, money=0, energy=0, happiness=0, study=0, meals=0):
        """Apply an action or event without going above attribute limits."""
        self.money += money
        self.energy = max(0, min(100, self.energy + energy))
        self.happiness = max(0, min(100, self.happiness + happiness))
        self.study = max(0, min(100, self.study + study))
        self.meals = max(0, min(12, self.meals + meals))


@dataclass
class Game:
    """Thirty days of decisions, consequences and student life."""

    player: Player
    day: int = 1
    seed: int = field(default_factory=lambda: random.SystemRandom().randint(1, 9999999))
    history: list = field(default_factory=list)
    finished: bool = False
    ending: str = ""

    def status(self):
        """Show information used to decide what to do next."""
        p = self.player
        return (
            "\n" + "=" * 51 + "\n"
            + f" SYDNEY SURVIVAL SIMULATOR | DAY {self.day:02d}/{TOTAL_DAYS}\n"
            + "=" * 51 + "\n"
            + f" Student: {p.name}\n"
            + f" Money: ${p.money:<7} Energy: {p.energy:3}/100\n"
            + f" Happiness: {p.happiness:3}/100  Study: {p.study:3}/100\n"
            + f" Meals in pantry: {p.meals}\n"
            + f" Next rent: ${WEEKLY_RENT} on day {min(((self.day - 1) // 7 + 1) * 7, 28)}\n"
            + "=" * 51
        )

    def perform_action(self, choice, destination=None):
        """Apply one action. Raise ValueError for an impossible choice."""
        if self.finished:
            raise ValueError("This game has already ended.")

        p = self.player
        if choice == "1":
            p.change(energy=-11, happiness=-5, study=14)
            message = "You studied at Fisher Library. Study +14."
        elif choice == "2":
            p.change(money=180, energy=-16, happiness=-8)
            message = "You worked a cafe shift. Earned $180."
        elif choice == "3":
            if p.money < 65:
                raise ValueError("Groceries cost $65. You need more money.")
            p.change(money=-65, energy=-3, happiness=3, meals=6)
            message = "You stocked up at the supermarket: +6 meals, -$65."
        elif choice == "4":
            p.change(energy=30, happiness=7)
            message = "You rested at home. Energy +30, Happiness +7."
        elif choice == "5":
            if destination not in DESTINATIONS:
                raise ValueError("Choose a destination numbered 1, 2 or 3.")
            place, price, joy, energy_cost, learning = DESTINATIONS[destination]
            if p.money < price:
                raise ValueError(f"A visit to {place} costs ${price}.")
            p.change(money=-price, energy=-energy_cost,
                     happiness=joy, study=learning)
            message = f"You explored {place}! -${price}, +{joy} happiness."
        else:
            raise ValueError("Choose an action from 1 to 5.")

        self.history.append(f"Day {self.day}: {message}")
        return message

    def todays_event(self):
        """Select an event deterministically using saved seed + day.

        Saved games do not need unsafe pickle or global random state.
        """
        rng = random.Random(self.seed + self.day * 9973)
        if rng.random() >= 0.52:
            return None
        return EVENTS[rng.randrange(len(EVENTS))]

    def apply_event(self, event, answer):
        """The player chooses how to respond to the day's event."""
        if answer not in ("1", "2"):
            raise ValueError("Please choose event option 1 or 2.")
        description, effects = event["options"][int(answer) - 1]
        self.player.change(*effects)
        message = f"{event['title']}: {description}"
        self.history.append(f"Day {self.day}: {message}")
        return message

    def end_day(self):
        """Eat, pay rent if due, check endings, and move to tomorrow."""
        p = self.player
        updates = []

        if p.meals > 0:
            p.change(meals=-1, energy=-2)
            updates.append("You ate one meal (-1 pantry meal).")
        else:
            p.change(energy=-13, happiness=-9)
            updates.append("No food! Energy -13, Happiness -9.")

        if self.day % 7 == 0:
            p.change(money=-WEEKLY_RENT)
            updates.append(f"Weekly rent paid: -${WEEKLY_RENT}.")

        if p.money < 0:
            p.change(happiness=-3)
            updates.append("Being in debt is stressful: Happiness -3.")

        self.history.extend(f"Day {self.day}: {item}" for item in updates)

        if p.energy <= 0:
            self.finished = True
            self.ending = "BURNOUT: You ran out of energy. Better rest next time."
        elif p.money < -450:
            self.finished = True
            self.ending = "EVICTION: Debt exceeded $450. Balance work and rent."
        elif self.day == TOTAL_DAYS:
            self.finished = True
            self.ending = self.final_ending()
        else:
            self.day += 1
        return updates

    def final_ending(self):
        """Multiple endings reward balancing study, well-being and money."""
        p = self.player
        if p.study >= 85 and p.happiness >= 60 and p.money >= 400:
            return "THRIVING IN SYDNEY! You balanced study, money and fun."
        if p.study >= 65 and p.energy >= 20 and p.happiness >= 20 and p.money >= 0:
            return "SYDNEY SURVIVOR! You finished 30 days successfully."
        return ("TOUGH SEMESTER: You lasted 30 days, but need a better "
                "balance of study, money and wellbeing.")

    def report(self):
        """A concise final report for the tutorial demonstration."""
        p = self.player
        recent = "\n".join(" - " + entry for entry in self.history[-5:])
        return (
            "\n" + "=" * 51 + "\n"
            + " YOUR 30-DAY SYDNEY STORY\n" + "=" * 51 + "\n"
            + self.ending + "\n"
            + f"Money: ${p.money} | Energy: {p.energy} | "
            + f"Happiness: {p.happiness} | Study: {p.study}\n"
            + "Recent diary entries:\n" + (recent or " - No entries yet.")
            + "\n" + "=" * 51
        )

    def to_dict(self):
        """Only ordinary JSON types are stored; never execute save content."""
        return {
            "version": 1,
            "day": self.day,
            "seed": self.seed,
            "finished": self.finished,
            "ending": self.ending,
            "history": self.history,
            "player": {
                "name": self.player.name,
                "money": self.player.money,
                "energy": self.player.energy,
                "happiness": self.player.happiness,
                "study": self.player.study,
                "meals": self.player.meals,
            },
        }

    @classmethod
    def from_dict(cls, data):
        """Reject corrupt/unsafe saves with clear feedback."""
        if not isinstance(data, dict) or data.get("version") != 1:
            raise ValueError("Unknown or invalid save file version.")
        try:
            p = data["player"]
            name = p["name"]
            if not isinstance(name, str) or not (1 <= len(name) <= 32):
                raise ValueError("Player name is invalid.")
            stats = {}
            for key, low, high in (
                ("money", -100000, 1000000),
                ("energy", 0, 100),
                ("happiness", 0, 100),
                ("study", 0, 100),
                ("meals", 0, 12),
            ):
                value = p[key]
                if type(value) is not int or not (low <= value <= high):
                    raise ValueError(f"Invalid {key} value in save file.")
                stats[key] = value
            day, seed = data["day"], data["seed"]
            if type(day) is not int or not 1 <= day <= TOTAL_DAYS:
                raise ValueError("Saved day is invalid.")
            if type(seed) is not int or not 1 <= seed <= 9999999:
                raise ValueError("Saved random seed is invalid.")
            history = data["history"]
            if (not isinstance(history, list) or len(history) > 500
                    or any(not isinstance(item, str) or len(item) > 300
                           for item in history)):
                raise ValueError("Saved diary is invalid.")
            finished, ending = data["finished"], data["ending"]
            if type(finished) is not bool or not isinstance(ending, str):
                raise ValueError("Saved ending is invalid.")
            return cls(Player(name, **stats), day, seed, history,
                       finished, ending)
        except (KeyError, TypeError) as error:
            raise ValueError("The save file has missing or invalid fields.") from error
