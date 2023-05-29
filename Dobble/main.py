import sys

def generate_cards(total_images):
    cards = []
    n = total_images - 1

    # Az első kártya generálása
    cards.append(list(range(1, n + 2)))

    # A többi kártya generálása a Dobble algoritmus alapján
    for j in range(n):
        set_of_image_ids = [n + 2 + n * j + k for k in range(n)]
        set_of_image_ids.append(1)
        cards.append(list(set_of_image_ids))

    for i in range(n):
        for j in range(n): 
            set_of_image_ids = [(n + 1 + n * k + (i * k + j) % n) + 1 for k in range(n)]
            set_of_image_ids.append(i + 2)
            cards.append(list(set_of_image_ids))

    return cards

if __name__ == "__main__":
    # Ha nincs megadva az "n" paraméter, akkor kiírja a használatot
    if len(sys.argv) != 2:
        print(f"Használat: python {sys.argv[0]} <n>")
    
    n = int(sys.argv[1])
    # Kártyák legenerálása
    cards = generate_cards(n)
    
    # Kártyák kiírása
    for card in cards:
        for image in card:
            print(image, end=" ")
        print()