import random
from typing import List, Dict

Suit = ['clubs','spades','hearts','diamonds']
Rank = [2,3,4,5,6,7,8,9,10,'J','Q','K','A']

def rank_power(r)->int:
    if isinstance(r,int): return r
    return {'J':11,'Q':12,'K':13,'A':14}[r]

def new_deck(seed:str)->List[Dict]:
    rng = random.Random(seed)
    deck = [{"id": f"{s}-{r}", "suit": s, "rank": r} for s in Suit for r in Rank]
    rng.shuffle(deck)
    return deck

def classify_card(card)->str:
    s = card['suit']
    if s in ('clubs','spades'): return 'enemy'
    if s == 'hearts': return 'heal'
    return 'weapon'  # diamonds

def enemy_power(card)->int:
    return rank_power(card['rank'])
