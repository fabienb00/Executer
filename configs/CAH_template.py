class Player:
    def __init__(self, p_name):
        pass
    
    def play(self, p_cards):
        # Called, if the player plays a card
        # p_cards is a list of strings
        pass
    
    @property
    def points(self):
        # Returns the points of the player (int)
        return 0
        
    @property
    def cards(self):
        # Returns the cards, the player already has (list of string)
        return []
     
     
class Game:
    def __init__(self, p_packs):
        # (Optional) p_packs (list of strings) is the packs with which to play
        
        # list of players
        self.player_list = []
        # dictionnary player -> list of strings
        # Cards, that are on the table
        self.table = {}
        # Current black card
        self.current_black = "__(1)__"
        
    def join(self, p_player):
        # Called, if a player joins
        pass
        
    def close_joining(self):
        # Nobody can join after this and the game starts
        pass
        
    def finish(self):
        # Finishes the game
        pass
        
    def show(self):
        # Returns a string, with all the player_cards in it 
        return ""
        
    def choose(self, p_num):
        # Chooses the player number
        pass
        
    def _new_round(self):
        # Commances a new round
        pass
        
