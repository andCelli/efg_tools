class HashState:
    def __init__(self, player, cards, leading, upper, lower, tricks):
        self.current_player = player
        self.cards = cards
        self.upper_bound = upper
        self.lower_bound = lower
        self.leading_suite = leading
        self.tricks_left = tricks
    
    def get_current_player(self):
        return self.current_player
    
    def set_current_player(self, player):
        self.current_player = player

    def get_cards(self):
        return self.cards
    
    def set_cards(self, cards):
        self.cards = cards

    def get_upper_bound(self):
        return self.upper_bound
    
    def set_upper_bound(self, upper):
        self.upper_bound = upper

    def get_lower_bound(self):
        return self.lower_bound
    
    def set_lower_bound(self, lower):
        self.lower_bound = lower

    def get_leading_suite(self):
        return self.leading_suite
    
    def set_leading_suite(self, leading):
        self.leading_suite = leading

    def get_tricks_left(self):
        return self.tricks_left

    def set_tricks_left(self, tricks):
        self.tricks_left = tricks
