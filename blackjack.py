import numpy as np
from typing import List

class Hand():
    """
    Represents a single hand in blackjack.
    Immutable and hashable - perfect for use in state representations.
    """
    cards: List[int]  # Cards as numbers (e.g., 1=Ace, 11=Jack, 12=Queen, 13=King)
    doubled: bool = False   # Whether this hand has been doubled down
    can_double: bool = True # Wheter this hand can be doubled
    done: bool = False       # Whether this hand is finished

    def __init__(self, cards: List[int] = None, dealer: bool = False, can_double: bool = True):
        """Initialize a hand with given cards, or draw two if none provided"""

        self.cards = []
        if cards is not None:
            self.cards = cards
        elif dealer:
            self.draw()
        else:
            self.draw()
            self.draw()
        
        self.can_double = can_double

    def __le__(self, other: 'Hand') -> bool:
        """Compare hands for sorting (used in strategy)"""
        return self.__repr__() <= other.__repr__()
    
    def __lt__(self, other: 'Hand') -> bool:
        """Compare hands for sorting (used in strategy)"""
        return self.__repr__() < other.__repr__()

    def __repr__(self) -> str:
        """Return a readable string representation of the hand"""
        return f"Hand(cards={self.cards}, total={self.total()}, doubled={self.doubled})"
    
    def __str__(self) -> str:
        """Return a string representation of the hand"""
        return f"{self.cards} {'(Doubled)' if self.doubled else ''} ({self.total()})"

    def total(self) -> int:
        """Calculate the total value of the hand, handling Aces properly"""
        total = 0
        aces = 0
        
        for card in self.cards:
            if card == 1:  # Ace
                aces += 1
                total += 11
            elif card > 10:  # Face cards
                total += 10
            else:
                total += card
        
        # Adjust for Aces if total > 21
        while total > 21 and aces > 0:
            total -= 10  # Convert Ace from 11 to 1
            aces -= 1
            
        return total

    def is_bust(self) -> bool:
        """Returns True if hand is bust (total > 21)"""
        return self.total() > 21
    
    def can_split(self) -> bool:
        """Returns True if hand can be split"""
        return len(self.cards) == 2 and self.cards[0] == self.cards[1]

    def is_soft(self) -> bool:
        """Returns True if hand contains an Ace counted as 11"""
        total = sum(11 if card == 1 else min(card, 10) for card in self.cards)
        return any(card == 1 for card in self.cards) and total <= 21
    
    def is_blackjack(self) -> bool:
        """Returns True if hand is a natural blackjack (21 with 2 cards)"""
        return len(self.cards) == 2 and self.total() == 21

    def possible_actions(self) -> List[str]:
        """Returns a list of possible actions for the current hand"""
        if self.done:
            return []
        actions = ["hit", "stand"]
        if self.can_double and not self.doubled:
            actions.append("double")
        if self.can_split():
            actions.append("split")
        return actions

    def draw(self) -> None:
        """Draw a card"""
        self.cards += [np.random.randint(1, 14)]
        self.cards.sort()
        self.done = self.total() >= 21
        if self.can_double:
            self.can_double = False


class BlackjackState:
    """
    Improved blackjack state using Hand objects.
    Each player hand now bundles cards with its doubled status.
    """
    player_hands: List[Hand]  # List of Hand objects
    dealer_hand: Hand
    double_after_split: bool = False

    def __init__(self, player_hands: List[Hand] = None, dealer_hand: Hand = None, double_after_split: bool = False):
        if player_hands is None:
            player_hands = [Hand()]
        
        if dealer_hand is None:
            dealer_hand = Hand(dealer=True)

        self.player_hands = player_hands
        self.dealer_hand = dealer_hand
        self.double_after_split = double_after_split

    def __repr__(self) -> str:
        """Return a readable string representation of the game state"""
        hands_str = ", ".join(str(hand) for hand in self.player_hands)
        return f"BlackjackState(player_hands=[{hands_str}], dealer_hand={self.dealer_hand})"
    
    def __str__(self) -> str:
        """Return a string representation of the game state"""
        hands_str = "\n    ".join(f"{hand}" for hand in self.player_hands)
        return f"BlackjackState:\n  Player Hands:\n    {hands_str}\n  Dealer Hand: {self.dealer_hand}"

    def terminal_state(self) -> bool:
        """Check if the game is in a terminal state (all hands done)"""
        return all(hand.done for hand in self.player_hands)

    def make_step(self, actions):
        """
        Make a step in the game based on the action.
        This function would handle the logic for hitting, standing, doubling down, etc.
        """
        reward = 0

        for hand, action in zip(self.player_hands, actions):
            if not action or action not in hand.possible_actions():
                continue
            if action == "hit":
                hand.draw()
            elif action == "stand":
                hand.done = True
            elif action == "double":
                hand.draw()
                hand.doubled = True
                hand.done = True
            elif action == "split":
                hand1 = Hand(cards=[hand.cards[0]], can_double=self.double_after_split)
                hand2 = Hand(cards=[hand.cards[1]], can_double=self.double_after_split)
                hand1.draw()
                hand2.draw()
                self.player_hands.remove(hand)
                self.player_hands.extend([hand1, hand2])

            # order hands to avoid repetition
            self.player_hands.sort()

        if self.terminal_state():
            while self.dealer_hand.total() < 17:
                self.dealer_hand.draw()
            for hand in self.player_hands:
                if hand.is_bust():
                    reward -= (2 if hand.doubled else 1)
                elif self.dealer_hand.is_bust() or hand.total() > self.dealer_hand.total():
                    reward += (2 if hand.doubled else 1)
                elif hand.total() < self.dealer_hand.total():
                    reward -= (2 if hand.doubled else 1)
        return reward


state1 = BlackjackState()
reward = None
print(state1)
print()

while not state1.terminal_state():
    actions = []
    for hand in state1.player_hands:
        if hand.done:
            actions.append(None)
            continue
        print(f"Current hand: {hand}")
        print(f"Possible actions: {hand.possible_actions()}")
        action = input("Choose an action: ")
        print()
        actions.append(action)
    reward = state1.make_step(actions)
    print(state1)
    print(f"Reward: {reward}")
    print()
    print()

