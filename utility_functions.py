def get_card_value(card):
    value_str = card.split(" of ")[0]
    value_dict = {
        "Pile": 0,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
        "Six": 6,
        "Seven": 7,
        "Eight": 8,
        "Nine": 9,
        "Ten": 10,
        "Jack": 11,
        "Queen": 12,
        "King": 13,
        "Ace": 14,
    }
    return value_dict[value_str]


def get_card_suit(card):
    suit = card.split(" of ")[1]
    return suit


def card_names(card_list):
    return [card.name for card in card_list]
