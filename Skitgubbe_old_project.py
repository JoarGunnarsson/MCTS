import os
import tty
import random
import sys
import traceback
import math
import time
sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=32, cols=170))
os.system('clear')
tty.setcbreak(sys.stdin)

"""
To do:

Lite konstig ordning av meddelanden när ai:n chansar. Kanske borde ta bort alla textmeddelanden och göra någon notis på bättre sätt.

Brädet ser lite konstigt ut när man updaterar brädet mot ain, det är ett stort mellanrum mellan brädet och 'continue'.

Merga playCard och aiPlay.

Ain måste kunna spela flera av samma kort.

UBC1 för alla drag blir typ samma.

Lista ut ett sätt att använda determinize

Datorn tyckte att spela 3S var bra, men 3C dåligt, men de borde vara ekvivalenta. Händer detta fortfarande?

Poängsättningen kan vara sämst också

Det står att det är spelarens tur medan datorn tänker. Uppdatera brädet när turen är slut.

Gör så att MCTS kan spela mot 'lowest', och se vilken som är bäst.

Datorn tänker tills den med högst score också är den med flest visits, så att den hinner utforska klart. Den borde dock få en sekund på sig varje gång den ändrar sig, så att det
inte blir att 4 st kort har samma score och visits.

Ett alternativt sätt är att göra en funktion för att bestämma hur "säker" ai:n är i sitt val, t.ex att det bästa draget måste ha 2 ggr så många besökningar som det näst bästa
eller något. Fick ett drag där det fanns 12 kort, så varje drag hade bara 70 visited. Detta är inte jättebra. Eller öka tillåten tänktetid beroende på hur många kort ain har.
T.ex 1 sekund per action, så 12 kort ger 14 sekunder. Problemet är att det blir super segt då. Om det inte går att optimera på något sätt.
Ett exempel är att göra rollout snabbare, genom att t.ex simulera rollout med att använda 'lowest' strategin. Direkt ai:n får runt 10 kort spelar den
jättedåligt.


"""

class Board():
    """Class for saving board info."""
    def __init__(self):
        self.name = "Game Board"
        self.state = ""
        self.player1 = None
        self.player2 = None
        self.turnPlayer = None
        self.nonTurnPlayer = None
        self.ai = False
        self.heap = [Card("", 0, "")]
        self.deck = self.newDeck()

    def newDeck(self):
        """Generates a new deck. Contains 52 cards, 13 per suit."""
        deck = [
        Card("Two of Hearts", 2, "Hearts"),
        Card("Three of Hearts", 3, "Hearts"),
        Card("Four of Hearts", 4, "Hearts"),
        Card("Five of Hearts", 5, "Hearts"),
        Card("Six of Hearts", 6, "Hearts"),
        Card("Seven of Hearts", 7, "Hearts"),
        Card("Eight of Hearts", 8, "Hearts"),
        Card("Nine of Hearts", 9, "Hearts"),
        Card("Ten of Hearts", 10, "Hearts"),
        Card("Jack of Hearts", 11, "Hearts"),
        Card("Queen of Hearts", 12, "Hearts"),
        Card("King of Hearts", 13, "Hearts"),
        Card("Ace of Hearts", 14, "Hearts"),

        Card("Two of Spades", 2, "Spades"),
        Card("Three of Spades", 3, "Spades"),
        Card("Four of Spades", 4, "Spades"),
        Card("Five of Spades", 5, "Spades"),
        Card("Six of Spades", 6, "Spades"),
        Card("Seven of Spades", 7, "Spades"),
        Card("Eight of Spades", 8, "Spades"),
        Card("Nine of Spades", 9, "Spades"),
        Card("Ten of Spades", 10, "Spades"),
        Card("Jack of Spades", 11, "Spades"),
        Card("Queen of Spades", 12, "Spades"),
        Card("King of Spades", 13, "Spades"),
        Card("Ace of Spades", 14, "Spades"),

        Card("Two of Clubs", 2, "Hearts"),
        Card("Three of Clubs", 3, "Clubs"),
        Card("Four of Clubs", 4, "Clubs"),
        Card("Five of Clubs", 5, "Clubs"),
        Card("Six of Clubs", 6, "Clubs"),
        Card("Seven of Clubs", 7, "Clubs"),
        Card("Eight of Clubs", 8, "Clubs"),
        Card("Nine of Clubs", 9, "Clubs"),
        Card("Ten of Clubs", 10, "Clubs"),
        Card("Jack of Clubs", 11, "Clubs"),
        Card("Queen of Clubs", 12, "Clubs"),
        Card("King of Clubs", 13, "Clubs"),
        Card("Ace of Clubs", 14, "Clubs"),

        Card("Two of Diamonds", 2, "Diamonds"),
        Card("Three of Diamonds", 3, "Diamonds"),
        Card("Four of Diamonds", 4, "Diamonds"),
        Card("Five of Diamonds", 5, "Diamonds"),
        Card("Six of Diamonds", 6, "Diamonds"),
        Card("Seven of Diamonds", 7, "Diamonds"),
        Card("Eight of Diamonds", 8, "Diamonds"),
        Card("Nine of Diamonds", 9, "Diamonds"),
        Card("Ten of Diamonds", 10, "Diamonds"),
        Card("Jack of Diamonds", 11, "Diamonds"),
        Card("Queen of Diamonds", 12, "Diamonds"),
        Card("King of Diamonds", 13, "Diamonds"),
        Card("Ace of Diamonds", 14, "Diamonds")
        ]

        return deck

    def playCard(self, card, player):
        """Plays the given card."""
        isHuman = not (self.ai and player == self.player2)
        playString = ""
        if ((player.hasPlayed == True) and (self.heap[-1].owner != player or self.heap[-1].value != card.value) and self.heap[-1].value != 10):
            return
        player.hasPlayed = True
        if (card.value >= self.heap[-1].value or card.value == 2 or card.value == 10):
            card.owner = player
            self.heap.append(card)
            player.hand.remove(card)
            if (len(player.hand) < 3 and len(self.deck) != 0):
                player.hand.append(self.deck[0])
                del self.deck[0]
            if (card.value == 10 or ([x.value for x in self.heap[-4:]]).count(card.value) == 4):
                self.updateBoard(isHuman)
                playString += "    The entire heap is now cleared, and you may play again.\n"
                del self.heap[1:]
                player.hasPlayed = False


        else:
            self.heap.append(card)
            player.hand.remove(card)
            self.updateBoard(isHuman)
            player.hand.extend(self.heap[1:])
            del self.heap[1:]
            playString += "    You played a lower card than the top card in the heap. Pick up the entire heap.\n"
        sort(player.hand)

    def aiPlay(self, card, player):
        """Plays the given card. But for MCTS"""
        if ((player.hasPlayed == True) and (self.heap[-1].owner != player or self.heap[-1].value != card.value) and self.heap[-1].value != 10):
            return
        player.hasPlayed = True
        if (card.value >= self.heap[-1].value or card.value == 2 or card.value == 10):
            card.owner = player
            self.heap.append(card)
            player.hand.remove(card)
            if (len(player.hand) < 3 and len(self.deck) != 0):
                player.hand.append(self.deck[0])
                del self.deck[0]
            if (card.value == 10 or ([x.value for x in self.heap[-4:]]).count(card.value) == 4):
                del self.heap[1:]
                player.hasPlayed = False


        else:
            player.hand.extend(self.heap[1:])
            del self.heap[1:]
        sort(player.hand)

    def aiHeap(self, player):
        if (player.hasPlayed):
            return
        if (len(self.heap) <= 1):
            return
        player.hand.extend(self.heap[1:])
        del self.heap[1:]
        player.hasPlayed = True
        sort(player.hand)

    def selectHeap(self, player):
        selected = 0
        row = 0
        showStart = 0
        showEnd = 5
        heapContents = ""
        row1Marker = ""
        while True:
            trueHeap = [x for x in reversed(self.heap[1:])]
            heapContents = "..." * (showStart != 0) + ("[" + (", ").join([card.name for card in trueHeap[showStart:showEnd]]) + "]") + "..." * (showEnd != len(trueHeap) and len(trueHeap) > showEnd)
            if (row == 1):
                row1Marker = " " * (len("[" + ", ".join([x.name for x in trueHeap[showStart:selected]])) + 2 * (selected != 0) + 3 * (showStart != 0)) + "-"*len(trueHeap[selected].name)
            else:
                row1Marker = ""
            heapString = """
    You take a closer look at the heap.

    Heap: {} (Cards in heap: {})\t
          {}

    |Pick Up|\t\t|Go Back|
    {}
            """.format(heapContents, len(self.heap) - 1,
            row1Marker,
            (" " * 20 * (selected != 0) + "---------") * (row == 0))

            printScreen(heapString)
            command = keyPress()
            if (command == "left"):
                selected = max(0, selected - 1)
                if (selected < showStart):
                    showStart -= 1
                    showEnd -= 1

            elif (command == "right"):
                if (row == 0):
                    selected = min(1, selected + 1)
                elif (row == 1):
                    selected = min(len(self.heap) - 2, selected + 1)
                    if (selected == showEnd):
                        showStart += 1
                        showEnd += 1

            elif (command == "down"):
                row = max(0, row - 1)
                selected = 0

            elif (command == "up"):
                row = min(1 * (len(trueHeap) > 5) , row + 1)
                selected = 0

            elif (command == "enter"):
                if (row == 0):
                    if (selected == 0):
                        self.pickHeap(player)
                    return

            elif (command == "quit"):
                return "end"

    def pickHeap(self, player):
        if (player.hasPlayed):
            return
        if (len(self.heap) <= 1):
            return
        player.hand.extend(self.heap[1:])
        del self.heap[1:]
        player.hasPlayed = True
        sort(player.hand)

    def chance(self, player):
        if (not player.hasPlayed and len(self.deck) > 0):
            card = self.deck[0]
            del self.deck[0]
            player.hand.append(card)
            self.playCard(card, player)

    def aiChance(self, player):
        if (not player.hasPlayed):
            card = self.deck[0]
            del self.deck[0]
            player.hand.append(card)
            self.aiPlay(card, player)

    def updateBoard(self, isHuman):
        if (isHuman):
            self.printBoard(self.turnPlayer, self.nonTurnPlayer, True)
        else:
            self.printBoard(self.player1, self.player2, True)
        continueButton("UpdateBoard")

    def printBoard(self, currentPlayer, otherPlayer, update = False, selected = 0, row = 0, showStart = 0, showEnd = 4):
        if (update):
            btn = ""
        else:
            btn = "|End Turn|"
        maxDisplay = 5
        heapDisplay = 4

        if (update):
            selectString = ""
        elif (row == 0):
            selectString = "----------"

        elif (row == 1):
            selectString = " " * (3 + 5 * min(selected - showStart, maxDisplay - 1) + len(("").join([("[" + card.name + "]") for card in currentPlayer.hand[showStart:selected]]))) + "-" * (len(currentPlayer.hand[selected].name) + 2)

        elif (row == 2):
            selectString = "-"*5


        opponentsCards = (" "*5).join([("[Hidden]") for card in otherPlayer.hand[:maxDisplay]])
        heapContents = "[" + ", ".join([x.name for x in (reversed(self.heap[-heapDisplay:])) if x.name != ""]) + "]"
        row2Marker = ((" "*len("Heap: " + heapContents + " (Cards in heap: " + str(len(self.heap)) + ")") + "\t")*(selected != 0) + "----" )*(row == 2)
        row1Marker = "..." * (showStart != 0) + "   " * (showStart == 0) + (" "*5).join([("[" + card.name + "]") for card in currentPlayer.hand[showStart:showEnd]]) + "..." * (currentPlayer.hand[-1] != currentPlayer.hand[showStart:showEnd][-1])
        boardString = """
    It is currently player {}'s turn.


    Opponent's cards:\t{}\t({} cards)


    Heap: {} (Cards in heap: {})\tDeck: {} cards left.
    {}

    Your cards:\t{}     ({} cards)
               \t{}

    {} {}
    {}
        """.format(self.turnPlayer.name,
        opponentsCards, len(self.nonTurnPlayer.hand),
        heapContents, len(self.heap) - 1, len(self.deck),
        row2Marker,
        row1Marker, len(self.turnPlayer.hand),
        selectString * (row == 1),
        btn, "(You cannot end your turn right now.)" * (not self.turnPlayer.hasPlayed and not update),
        selectString * (row == 0))
        printScreen(boardString)

    def switchTurns(self):
        self.turnPlayer, self.nonTurnPlayer = self.nonTurnPlayer, self.turnPlayer

    def copy(self):
        newBoard = Board()
        newBoard.deck = self.deck.copy()
        newBoard.heap = self.heap.copy()
        newBoard.turnPlayer = self.turnPlayer.copy()
        newBoard.nonTurnPlayer = self.nonTurnPlayer.copy()
        newBoard.player1 = self.player1.copy()
        newBoard.player2 = self.player2.copy()
        return newBoard

    def determinize(self):
        """Determinizes the given board."""
        return
        newBoard = Board()
        newBoard = self.copy()
        unknownCards = []
        unknownCards.extend(self.deck)
        unknownCards.extend(self.nonTurnPlayer.hand)
        random.shuffle(unknownCards)
        newBoard.nonTurnPlayer.hand = unknownCards[:len(self.nonTurnPlayer.hand)]
        del unknownCards[:len(self.nonTurnPlayer.hand)]
        newBoard.deck = unknownCards
        self.nonTurnPlayer.hand = newBoard.nonTurnPlayer.hand
        self.deck = newBoard.deck

class Player():
    """Class for players."""
    def __init__(self):
        self.name = ""
        self.hand = []
        self.hasPlayed = False

    def setName(self, number):
        """Generates the name for a player."""
        forbiddenNames = ["", "orch"]
        while True:
            name = input("\n    Player {}: Please enter your name.\n    ".format(number))
            if (name.lower() not in forbiddenNames):
                print ("    Your name has been accepted.")
                self.name = name
                return
            else:
                print("    That name is not allowed. Please pick another.")

    def copy(self):
        newPlayer = Player()
        newPlayer.name = self.name
        newPlayer.hand = self.hand.copy()
        newPlayer.hasPlayed = self.hasPlayed
        return newPlayer

class Card():
    """Class for cards,"""
    def __init__(self, name, value, suit):
        self.name = name
        self.value = value
        self.suit = suit
        self.owner = ""

    def setOwner(self, owner):
        self.owner = owner

class Node():
    def __init__(self, board, parent, depth, action):
        self.board = board
        self.parent = parent
        self.depth = depth
        self.action = action
        self.score = 0
        self.visited = 0
        self.children = []
        self.value = 10**12 #This is the UCB1 score. Börjar på 10**12, eftersom den inte är besökt.

    def updateValue(self, change, changeNothing = False):
        if (not changeNothing):
            self.visited += 1
        self.score += change
        if (self.visited == 0):
            self.value = 10**12

        elif (self.depth == 0 or self.parent.visited == 0):
            self.value = self.score / self.visited
        else:
            self.value = self.score / self.visited + 4 * math.sqrt(math.log(self.parent.visited) / self.visited) # Fixa detta bättre när en korrect 'score' är fixad.

    def bestChild(self):
        for child in self.children:
            child.updateValue(0, True)

        sortedChildren = self.children.copy()
        sort(sortedChildren)
        return sortedChildren[-1]

    def copy(self):
        newNode = Node(self.board.copy(), self.parent, self.depth, self.action)
        return newNode

    def selection(self):
        if (len(self.children) == 0):
            self.expand()
            return self.children[0]
        elif (self.depth > 800):
            print("MAXDEPTHREACHED")
            continueButton()
            return self.bestChild()

        return self.bestChild().selection()

    def expand(self):
        """Expands the current node and adds one child per card, plus one for picking up the heap and one for taking a chance."""
        for card in self.board.turnPlayer.hand:
            newBoard = self.board.copy()
            newBoard.aiPlay(card, newBoard.turnPlayer)
            newBoard.switchTurns()
            self.children.append(Node(newBoard, self, self.depth + 1, card))

        if (len(self.board.deck) > 0):
            chanceBoard = self.board.copy()
            chanceBoard.aiChance(chanceBoard.turnPlayer)
            chanceBoard.switchTurns()
            self.children.append(Node(chanceBoard, self, self.depth + 1, "chance"))

        if (len(self.board.heap) > 1):
            heapBoard = self.board.copy()
            heapBoard.aiHeap(heapBoard.turnPlayer)
            heapBoard.switchTurns()
            self.children.append(Node(heapBoard, self, self.depth + 1, "heap"))

    def backpropagate(self, change):
        self.updateValue(change)
        for child in self.children:
            child.updateValue(0, True)

        if (self.depth != 0):
            self.parent.backpropagate(-change)

    def rollout(self):
        trialNode = self.copy()
        i = 0
        iter = 100
        while (i < iter):
            trialNode.board.turnPlayer.hasPlayed = False
            actions = [card for card in trialNode.board.turnPlayer.hand]
            if (len(trialNode.board.deck) > 0):
                actions.append("chance")

            if (len(trialNode.board.heap) > 1):
                actions.append("heap")

            if (len(actions) == 0):
                print("actions is zero")
                points = sigmoid(20)
                if (trialNode.board.turnPlayer == trialNode.board.player1):
                    points *= -1
                self.backpropagate(points)
                return

            chosen = random.choice(actions)

            card = Card("",0,"")
            allSame = False

            if (chosen == "chance"):
                card = trialNode.board.deck[0]
                allSame = [x.value == card.value for x in trialNode.board.heap[-3:]] == [True for x in trialNode.board.heap[-3:]] and len(trialNode.board.heap[-3:]) == 3
                trialNode.board.aiChance(trialNode.board.turnPlayer)

            elif (chosen == "heap"):
                trialNode.board.pickHeap(trialNode.board.turnPlayer)

            else:
                card = chosen
                allSame = [x.value == card.value for x in trialNode.board.heap[-3:]] == [True for x in trialNode.board.heap[-3:]] and len(trialNode.board.heap[-3:]) == 3
                trialNode.board.aiPlay(chosen, trialNode.board.turnPlayer)

            if not (card.value == 10 or allSame):
                trialNode.board.switchTurns()

            if (len(trialNode.board.turnPlayer.hand) == 0):
                break

            i += 1
        score1 = sum([x.value for x in trialNode.board.player1.hand]) / len(trialNode.board.player1.hand) - len(trialNode.board.player1.hand)
        score2 = sum([x.value for x in trialNode.board.player2.hand]) / len(trialNode.board.player2.hand) - len(trialNode.board.player2.hand)
        points = score2 - score1

        if (trialNode.board.turnPlayer == trialNode.board.player1):
            points *= -1
        points = sigmoid(points)
        self.backpropagate(points)

def dealCards(board):
    random.shuffle(board.deck)
    board.player1.hand = board.deck[:3]
    sort(board.player1.hand)
    del board.deck[:3]
    board.player2.hand = board.deck[:3]
    sort(board.player2.hand)
    del board.deck[:3]

def printScreen(string):
    """Clears window and prints the provided string."""
    os.system('clear')
    print(string)

def keyPress():
    """Uses stdin to get a keypress. Returns what that keypress means. Pauses until key is pressed."""
    key = ord(sys.stdin.read(1))

    if (key == 97):
        return "left"

    elif (key == 100):
        return "right"

    elif (key == 115):
        return "down"

    elif (key == 119):
        return "up"

    elif (key == 224):
        secondKey = ord(sys.stdin.read(1))
        if (secondKey == 75):
            return "left"
        elif (secondKey == 77):
            return "right"
        elif (secondKey == 80):
            return "down"
        elif (secondKey == 72):
            return "up"

    elif (key == 10):
        return "enter"

    elif (key == 13):
        return "quit"

def continueButton(message = ""):
    """Creates a '|Continue|' button. Freezes screen until 'Enter' is pressed."""
    print("\n\n" + "|Continue|", end = "")
    while True:
        key = ord(sys.stdin.read(1))
        if (key == 10):
            break
        elif (key == 224):
            sys.stdin.read(1)
        elif (key == 13):
            sys.exit()

def buttonMenu(string, buttons):
    """Creates a menu for any number of buttons, and places them in a row."""
    buttons = ["|" + btn + "|" for btn in buttons]
    selected = 0
    while True:
        menuString = """
    {}

    {}
    {}
        """.format(string,
        (" "* 10).join(buttons),
        " " * (len("".join(buttons[:selected])) + 10 * len(buttons[:selected])) + "-" * (len(buttons[selected])))
        printScreen(menuString)
        command = keyPress()
        if (command == "left"):
            selected -= 1

        elif (command == "right"):
            selected += 1

        elif (command == "enter"):
            return selected

        elif (command == "quit"):
            return "end"

        selected = clamp(selected, 0, len(buttons) - 1)

def sort(myList):
    """Sorts myList and returns it. Based on property 'value'"""
    for x in range(len(myList)):
        for y in range(len(myList)):
            if (myList[x].value < myList[y].value):
                temp = myList[x]
                myList[x] = myList[y]
                myList[y] = temp

def sortVisited(myList):
    """Sorts myList and returns it. Based on how many visits a node has"""
    for x in range(len(myList)):
        for y in range(len(myList)):
            if (myList[x].visited < myList[y].visited):
                temp = myList[x]
                myList[x] = myList[y]
                myList[y] = temp

def clamp(x, lowerBound = 0, upperBound = 1):
    """Clamps a number between an upper and lower bound. Default bounds are [0,1]."""
    if (lowerBound > upperBound):
        lowerBound, upperBound = upperBound, lowerBound
    return max(min(x, upperBound), lowerBound)

def sigmoid(x):
    return 10 * (1 / (1 + math.exp(-x / 52)))

def game(board):
    state = board.state
    if (state == "mainmenu"):
        menuString = "Skitgubbe - Main Menu"
        buttons = ["Start Game", "Quit Game"]
        selected = buttonMenu(menuString, buttons)
        if (selected == 0):
            return "gamemode"

        else:
            return "end"

    elif (state == "gamemode"):
        menuString = "Do you want to play against a player or against the computer?"

        buttons = ["Player", "Computer"]

        select = buttonMenu(menuString, buttons)

        if (select == 0):
            print("You chose to play against a player.")
        else:
            print ("You chose to play against the computer.")
            board.ai = True

        continueButton()
        return "start"

    elif (state == "start"):
        printScreen("    Starting the game. The starting player will be chosen at random.")

        board.player1 = Player()
        board.player1.name = "JoarDEV"
        board.player1.setName(1)
        if (board.ai):
            board.player2 = Player()
            board.player2.name = "The Computer"
            board.player2.strategy = "MCTS" #Ändra detta eventuellt.
        else:
            board.player2 = Player()
            board.player2.setName(2)
        continueButton()

        startingPlayer = random.choice([board.player1, board.player2])
        if (startingPlayer == board.player1):
            nonstartingPlayer = board.player2
        else:
            nonstartingPlayer = board.player1

        string = """

    Alright. {} will go first.


    Shuffling the deck...
    The deck has been shuffled. Each player will now be given three cards.
        """.format(startingPlayer.name)
        printScreen(string)

        continueButton()

        board.turnPlayer = startingPlayer
        board.nonTurnPlayer = nonstartingPlayer

        dealCards(board)

        if (board.ai and board.turnPlayer == board.player2):
            board.printBoard(board.player1, board.player2, True)
            return "aiTurn"
        return "playerTurn"

    elif (state == "playerTurn"):
        board.turnPlayer.hasPlayed = False
        selected = 0
        row = 1
        numberOfRows = 3
        showStart = 0
        showEnd = 5
        selectString = ""
        while True:
            board.printBoard(board.turnPlayer, board.nonTurnPlayer, False, selected, row, showStart, showEnd)
            command = keyPress()
            if (command == "left"):
                selected = max(0, selected - 1)
                if (selected < showStart):
                    showStart -= 1
                    showEnd -= 1

            elif (command == "right"):
                if (row == 1):
                    selected = min(len(board.turnPlayer.hand) - 1, selected + 1)
                    if (selected == showEnd):
                        showStart += 1
                        showEnd += 1
                elif (row == 2):
                    selected = min(1, selected + 1)

            elif (command == "up"):
                row = min(row + 1, numberOfRows - 1)
                selected = 0

            elif (command == "down"):
                row = max(row - 1, 0)
                if (row == 0 and board.turnPlayer.hasPlayed == False):
                    row = 1
                selected = 0

            elif (command == "enter"):
                if (row == 0):
                    board.turnPlayer, board.nonTurnPlayer = board.nonTurnPlayer, board.turnPlayer
                    if (board.ai):
                        return "aiTurn"
                    else:
                        return "playerTurn"
                elif (row == 1):
                    board.playCard(board.turnPlayer.hand[selected], board.turnPlayer)
                    if (selected >= len(board.turnPlayer.hand)):
                        selected -= 1
                    if (len(board.turnPlayer.hand) == 0 and len(board.deck) == 0):
                        return "win"
                elif (row == 2):
                    if (selected == 0):
                        board.selectHeap(board.turnPlayer)

                    elif (selected == 1):
                        board.chance(board.turnPlayer)
            elif (command == "quit"):
                return "end"

    elif (state == "aiTurn"):
        board.turnPlayer.hasPlayed = False
        if (board.turnPlayer.strategy == "lowest"):
            lowestCard = None
            card2 = None
            card10 = None
            for card in board.turnPlayer.hand:
                if (card.value == 2):
                    card2 = card
                elif (card.value == 10):
                    card10 = card
                elif (card.value >= board.heap[-1].value):
                    lowestCard = card
                    break

            if (lowestCard != None):
                card = lowestCard
            elif (card2 != None):
                card = card2
            elif (card10 != None):
                card = card10
            else:
                board.chance(board.turnPlayer)
                print ("The ai took a chance and played the card...?")
                board.turnPlayer, board.nonTurnPlayer = board.nonTurnPlayer, board.turnPlayer
                return "playerTurn"
            allSame = [x.value == card.value for x in board.heap[-3:]] == [True for x in board.heap[-3:]] and len(board.heap[-3:]) == 3
            playAgain = card.value == 10 or allSame
            board.playCard(card, board.turnPlayer)
            if (playAgain):
                return "aiTurn"
            else:
                board.turnPlayer, board.nonTurnPlayer = board.nonTurnPlayer, board.turnPlayer
                return "playerTurn"

        elif (board.turnPlayer.strategy == "MCTS"):
            rootNode = Node(board.copy(), None, 0, None)
            start = time.time()
            timeAllowed = (len(board.turnPlayer.hand) + 2)
            while (True):
                rootNode.board.determinize()
                currentNode = rootNode.selection()
                currentNode.rollout()
                sortedChildren = rootNode.children.copy()
                sortVisited(sortedChildren)
                timePassed = time.time() - start
                if (timePassed > timeAllowed and (sortedChildren[-1].action == rootNode.bestChild().action)):
                    break

            playCard = Card("",0,"")
            sortVisited(rootNode.children)
            bestAction = rootNode.children[-1].action

            if (bestAction == "heap"):
                print ("The best play for the ai is: 'heap'.")
                allSame = False
                board.pickHeap(board.turnPlayer)

            elif (bestAction == "chance"):
                print ("The best play for the ai is: 'chance'.")
                playCard = board.deck[0]
                allSame = [x.value == playCard.value for x in board.heap[-3:]] == [True for x in board.heap[-3:]] and len(board.heap[-3:]) == 3
                board.chance(board.turnPlayer)

            else:
                print ("The best play for the ai is:", bestAction.name)
                playCard = bestAction
                allSame = [x.value == playCard.value for x in board.heap[-3:]] == [True for x in board.heap[-3:]] and len(board.heap[-3:]) == 3
                board.playCard(bestAction, board.turnPlayer)

            continueButton()
            if (playCard.value == 10 or allSame):
                return "aiTurn"
            board.turnPlayer, board.nonTurnPlayer = board.nonTurnPlayer, board.turnPlayer
            return "playerTurn"

        print ("Something went wrong... You're not supposed to be here...")
        continueButton("SomethingWrong")

    elif (state == "win"):
        winString = """
    Player {} won the game. Congratulations!
    The other player had {} left.""".format(board.turnPlayer.name, str(len(board.nonTurnPlayer.hand)) + " card" + "s" * (len(board.nonTurnPlayer.hand) != 1))
        printScreen(winString)
        continueButton("Win")
        board = Board()
        board.state = "win"
        return "mainmenu"

def main():
    board = Board()
    board.state = "mainmenu"
    while (board.state != "end"):
        try:
            board.state = game(board)
        except Exception as e:
            print (traceback.format_exc())
            continueButton("ErrorHandle")
    pass

main()
