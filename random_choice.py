import json
import random

REVERSED_CARD_CHANCE = 0.25


class TarotCard:

    def __init__(self, name, number, img_path):
        self.name = name
        self.number = number
        self.img_path = img_path
        self.is_reversed = False

    def __str__(self):
        reversed_remark = " (Перевернутая)" if self.is_reversed else ""
        return f"{self.name}{reversed_remark}"


class TarotDeck:
    def __init__(self, json_path: str = 'tarot-images.json'):
        self.deck = []

        if json_path is not None:
            with open(json_path, 'r', encoding='utf8') as f:
                data = json.load(f)
                for card_data in data["cards"]:
                    card = TarotCard(card_data["name"], card_data["number"], card_data["img"])
                    self.deck.append(card)

    def shuffle_deck(self):
        for card in self.deck:
            if random.uniform(0, 1) < REVERSED_CARD_CHANCE:
                card.is_reversed = not card.is_reversed  # переворачиваем карты
        random.shuffle(self.deck)

    def random_choice(self, n: int = 3):
        self.shuffle_deck()
        sample = self.deck[:n]
        return [card.__str__() for card in sample]


tarot_deck = TarotDeck("tarot-images.json")

if __name__ == '__main__':
    print(f"Три случайные карты: {tarot_deck.random_choice()}")
    print(f"Пять случайных карт: {tarot_deck.random_choice(5)}")
