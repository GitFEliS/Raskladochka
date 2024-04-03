import json
import random

with open('tarot-images.json', 'r') as f:
    data = json.load(f)


def random_choice(n: int = 3):
    sample = random.sample(data["cards"], n)
    return [i["name"] for i in sample], [i["img"] for i in sample]


if __name__ == '__main__':
    print(random_choice(5))
