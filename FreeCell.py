import random
import sys
sys.path.append('aima-python')
from aima.games import *
import math

def newDeck():
    """Creates a new deck of cards."""
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [(rank, suit) for suit in suits for rank in ranks]

def shuffleDeck(deck):
    """Shuffles the deck of cards."""
    import random
    random.shuffle(deck)
    return deck

def initGameState():
    """Initializes the game state for FreeCell."""
    deck = newDeck()
    shuffled_deck = shuffleDeck(deck)
    # Deal cards into 8 columns (4 columns with 7 cards and 4 columns with 6 cards)
    columns = [shuffled_deck[i:i + 7] for i in range(0, 28, 7)] + [shuffled_deck[i:i + 6] for i in range(28, 52, 6)]
    foundations = {suit: [] for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']}
    free_cells = [None] * 4  # 4 free cells
    return columns, foundations, free_cells

def actions(columns, foundations, free_cells):
        """Return a list of the allowable moves at this point."""
        list_of_moves = []

        # what cards can be moved to the foundations
        for i, col in enumerate(columns):
            if col:  # If the column is not empty
                card = col[-1]  # Get the top card of the column
                rank, suit = card
                # Check if the card can be moved to the foundation
                if foundations[suit] == [] and rank == 'A':
                    list_of_moves.append(('move_to_foundation', i))
                elif foundations[suit] and foundations[suit][-1][0] == str(int(rank) - 1):
                    list_of_moves.append(('move_to_foundation', i))

        # each card can be moved to a open free cell
        for i, col in enumerate(columns):
            if col:  # If the column is not empty
                card = col[-1]  # Get the top card of the column
                for j in range(len(free_cells)):
                    if free_cells[j] is None:  # If the free cell is empty
                        list_of_moves.append(('move_to_free_cell', i, j))
                        break  # Only one free cell can be used at a time

        # each card can be moved to another column
        for i, col in enumerate(columns):
            if col:  # If the column is not empty
                card = col[-1]  # Get the top card of the column
                rank, suit = card
                for j, target_col in enumerate(columns):
                    if i != j:  # Can't move to the same column
                        if target_col:  # If the target column is not empty
                            target_card = target_col[-1]
                            target_rank, target_suit = target_card
                            # Check if the card can be moved to the target column
                            if (int(rank) + 1 == int(target_rank)) and (suit != target_suit):
                                list_of_moves.append(('move_to_column', i, j))
                        else:  # If the target column is empty, any card can be moved there
                            list_of_moves.append(('move_to_column', i, j))

        return list_of_moves

def result(columns, foundations, free_cells, move):
    """Return the state that results from making a move from a state."""
    # move is a tuple of the form (source_index, target_index)
    # where the columns are numbered from 1 to 8, free cells are 9 to 12, and foundations are 13 to 16
    source_index, target_index = move

    # from a column
    if source_index < 8:
        card = columns[source_index].pop()  # Remove the top card from the source column
        if target_index < 8:  # Moving to another column
            columns[target_index].append(card)  # Add the card to the target column
        elif target_index < 12:  # Moving to a free cell
            free_cells[target_index - 8] = card  # Place the card in the free cell
        else:  # Moving to a foundation
            foundations[card[1]].append(card)  # Add the card to the appropriate foundation

    # from a free cell
    elif source_index < 12:
        card = free_cells[source_index - 8]  # Get the card from the free cell
        free_cells[source_index - 8] = None  # Empty the free cell
        if target_index < 8:  # Moving to a column
            columns[target_index].append(card)  # Add the card to the target column
        else:  # Moving to a foundation
            foundations[card[1]].append(card)  # Add the card to the appropriate foundation

    # from a foundation [NOT ALLOWED IN SOME IMPLEMENTATIONS]
    else:
        card = foundations[card[1]].pop()  # Remove the top card from the foundation
        if target_index < 8:  # Moving to a column
            columns[target_index].append(card)  # Add the card to the target column
        else:  # Moving to a free cell
            free_cells[target_index - 8] = card  # Place the card in the free cell

    return columns, foundations, free_cells

def utility(columns, foundations, free_cells, player):
    """Return the value of this final state to player."""
    raise NotImplementedError

def terminal_test(columns, foundations, free_cells):
    """Return True if this is a final state for the game."""
    # If all cards are in the foundations, the game is won, but there's a shortcut
    # if every column is decending, then game is also won, because you just move every 
    # card into the foundations with no columns needing to be moved again.
    for i, col in enumerate(columns):
        if col:  # If the column is not empty
            for j in range(len(col) - 1):
                rank1, suit1 = col[j]
                rank2, suit2 = col[j + 1]
                if (int(rank1) > int(rank2)):
                    continue
                else:
                    return False
        else:
            continue
        break
    return not actions(columns, foundations, free_cells)

def display(columns, foundations, free_cells):
    """Print or otherwise display the state."""
    print("Columns:")
    for i, col in enumerate(columns):
        print(f"Column {i + 1}: {col}")
    print("\nFoundations:", foundations)
    print("Free Cells:", free_cells)

def testTerminalTest():
    """Test the terminal_test function."""
    # Create a winning state
    columns = [[], [], [], [], [], [], [], []]
    foundations = {suit: [(rank, suit) for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']] for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']}
    free_cells = [None] * 4
    assert terminal_test(columns, foundations, free_cells) == True

    # Create a non-winning state
    columns = [[('A', 'Hearts')], [('2', 'Hearts')], [('3', 'Hearts')], [('4', 'Hearts')], [('5', 'Hearts')], [('6', 'Hearts')], [('7', 'Hearts')], [('8', 'Hearts')]]
    foundations = {suit: [] for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']}
    free_cells = [None] * 4
    assert terminal_test(columns, foundations, free_cells) == False

def main():
    columns, foundations, free_cells = initGameState()
    print("Initial Columns:")
    for i, col in enumerate(columns):
        print(f"Column {i + 1}: {col}")
    print("\nFoundations:", foundations)
    print("Free Cells:", free_cells)

if __name__ == "__main__":
    main()
    testTerminalTest()