# Cards are numbered 1-52
# They are dived as 1-13/14-27 ...

# A: 5 Top cards in each suit
# B: Bottom 8 in each suit
# C: Still remaining best 5 for each suit in B

from bitstring import BitArray
from double_dummy import hash_state

TOP_CARDS = 5
BOTTOM_CARDS = 8
SUITS = 4
RANKS = 13


class HashTable:

    def __init__(self, top, bottom, suits, ranks):
        self.table = {}
        self.top_cards = top
        self.bottom_cards = bottom
        self.suits = suits
        self.ranks = ranks

    def encodeCards(self, card_set):
        """Given a card set represented as a list of booleans, 
        True meaning 'card already played', and cards ordered as consecutive sets representing
        suits (e.g 1-2-3-1-2-3 for two suits and three ranks),
        the method returns a tuple (a,b,c) containing the three encoded card sets"""

        code_a = BitArray(self.suits * self.top_cards)
        code_b = BitArray(self.suits * self.bottom_cards)
        code_c = BitArray(self.suits * self.top_cards)

        for i in range(self.suits):
            for j in range(self.ranks):
                if card_set[i * self.ranks + j]:
                    if(j >= (self.ranks - self.top_cards)):
                        # Put into A
                        index = i * (self.ranks-self.top_cards) + j - self.bottom_cards
                        code_a[index] = True
                    else:
                        index = i * (self.bottom_cards) + j
                        code_b[index] = True
                        if (j > (self.bottom_cards - self.top_cards)):
                            index = i * (self.bottom_cards) + j - (self.bottom_cards - self.top_cards)
                            code_c[index] = True
        return code_a, code_b, code_c

    def computeHash(self, A, C):
        """The method computes the hashtable index"""

        C.rol(5)    # Perform 5-positions left shift with rotation
        return A ^ C    # XOR

    def store_state(self, state):
        """The method stores the B identifier and a HashState object in the hash table. B is used to 
        quickly detect already visited states"""

        a,b,c = self.encodeCards(state.get_cards())
        index = self.computeHash(a,c).bin
        self.table[index] = (b, state)

    def check_hit(self, state):
        """The method checks if the current state is already present in the hash table
        returning a dictionary containing the previously stored state, setting the 'collision' value
        to true if the found state differs from the currently inquired one.
        The method returns a None object if no hit is found"""
        
        a, b, c = self.encodeCards(state.get_cards())
        index = self.computeHash(a,c).bin

        if index in self.table:
            hit = self.table[index]
            if hit[0] == b:
                return ({"collision" : False, "state": hit[1]})
            else:
                return ({"collision" : True, "state": hit[1]})
        else:
            return None


# if __name__ == "__main__":

#     htable = HashTable(TOP_CARDS, BOTTOM_CARDS, SUITS, RANKS)

#     cset = [False, True, True, False, False, False, True, True, False, False, True, True, True]
#     cset1 = [False, True, True, False, False, False, True, True, False, False, True, True, False]
#     htable.store_state(cset ,1)
#     print(htable.already_visited(cset,1))
#     print(htable.already_visited(cset1,1))
