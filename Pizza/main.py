import json
import string
import random
import os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

SERVER_ADDRESS = ("localhost", 8000)
 
# Szándékok és a hozzájuk tartozó kulcsszavak
intent_keywords = {
    "size": ["small", "medium", "large"],
    "order_pizza": ["pizza"],
    "pizza_type": ["margherita", "veggie", "hawaiian"],
    "pizza_topping": ["pepperoni", "cheese", "mushrooms", "onions", "sausage", "pineapple", "spinach"],
    "drink_type": ["coke", "sprite", "water", "tea"],
}

# A pizzák árai
pizza_prices = {
    "hawaiian": 11.99,
    "margherita": 10.99,
    "veggie": 8.99,
}

# A méretek árai
size_prices = {
    "small": 0.0,
    "medium": 2.0,
    "large": 4.0,
}

# Italok árai
drink_prices = {
    "tea": 1.99,
    "coke": 1.99,
    "sprite": 1.75,
    "water": 0.99,
}

# Feltétek árai
topping_prices = {
    "pepperoni": 1.5,
    "cheese": 1.0,
    "mushrooms": 0.75,
    "onions": 0.75,
    "sausage": 0.75,
    "pineapple": 0.5,
    "spinach": 0.5,
}

# Különböző válaszok az ismert szándékokra
responses = {
    "positive_affirmations": [
        "Absolutely!",
        "Sure thing!",
        "Excellent choice!",
        "Fantastic!",
        "Great decision!",
    ],
    "order_status": [
        "Your current order includes a",
        "In your order so far, you have a",
        "Currently, your order consists of a",
        "As of now, your order includes a",
    ],
    "confused": [
        "Sorry, I don't understand. Can you rephrase that?",
        "I'm sorry, could you clarify what you mean?",
        "Oops! I'm having trouble understanding. Can you try saying it differently?",
        "My apologies, I cannot understand your message. Can you rephrase, please?",
        "Sorry, I'm having difficulty understanding. Could you rephrase your message?",
    ],
}

# Az üzenet előfeldolgozása
def preprocess_input(text):
    # A szöveg kisbetűssé alakítása
    text = text.lower()
    
    # Az írásjelek eltávolítása
    for char in string.punctuation:
        text = text.replace(char, '')
        
    # A szöveg feldarabolás szavanként
    return text.split()

# Szándékok észlelése az üzenetben
def detect_intents(user_input):
    # A felhasználú üzenetének előfeldolgozása
    user_input = preprocess_input(user_input)
    
    # Szándékok keresése az üzenetben
    detected_intents = []
    for intent, keywords in intent_keywords.items():
        for word in user_input:
            if word in keywords:
                detected_intents.append((intent, word))
    
    return detected_intents

# Véletlenszerű válasz generálása megadott szándék alapján
def select_respone(intent):
    return random.choice(responses[intent]) 

# A beszélgetéssel kapcsolatos információk tárolása
context = {
    "intent_index": 0,
    "detected_intents": [],
    "current_keyword": None
}

# Az osztály alapvető funkciókat biztosít a pizza objektum létrehozásához és kezeléséhez
class Pizza:
    def __init__(self, size = None, type_ = None):
        self.size = size
        self.type_ = type_
        self.toppings = []
    
    def add_topping(self, topping):
        self.toppings.append(topping)
        
    def has_topping(self, topping):
        return topping in self.toppings
    
    def is_completed(self):
        return self.size is not None and self.type_ is not None and len(self.toppings) > 0
    
    def calculate_price(self):
        price = pizza_prices[self.type_] + size_prices[self.size]
        
        for topping in self.toppings:
            price += topping_prices[topping]
        
        return price
    
    def get_receipt(self):
        return {
            "name": get_pizza_order_summary(),
            "price": self.calculate_price(),
        }

# Az osztály alapvető funkciókat biztosít az ital objektum létrehozásához és kezeléséhez
class Drink:
    def __init__(self, type_ = None):
        self.type_ = type_
    
    def is_completed(self):
        return self.type_ is not None
    
    def get_receipt(self):
        return {
            "name": self.type_,
            "price": drink_prices[self.type_],
        }

# A jelenlegi rendelés
pizza_order = None
drink_order = None

# Meghatározza, hogy van-e rendelési szándék a lista aktuális pozíciójához képest
def has_order_intent_relative_position(position):
    detected_intents = context["detected_intents"]
    current_index = context["intent_index"]
    
    # Összegyűjti a szándékokat a megadott irányban
    if position == "after":
        intents_to_check = detected_intents[current_index + 1:]
    elif position == "before":
        intents_to_check = detected_intents[:current_index]
    else:
        raise ValueError("Invalid position. Must be 'after' or 'before'.")
    
    # Ha talál rendeléssel kapcsolatos szándékot, akkor igazzal tér vissza
    for (intent, _) in intents_to_check:
        if intent in ["order_pizza", "order_drink"]:
            return True
    
    # Ha nem talál rendeléssel kapcsolatos szándékot, akkor hamissal tér vissza
    return False

# Feldolgozza a méretre vonatkozó szándékot
def process_intent_size(size):
    global pizza_order
    
    # Ellenőrzi, hogy a felhasználó rendelt-e már pizzát.
    if pizza_order == None:
        # Ellenőrzi, hogy található-e rendeléssel kapcsolatos szándék a jelenlegi szánék után
        if has_order_intent_relative_position("after"):
            # Létrehozza a rendelést a megadott mérettel
            pizza_order = Pizza(size=size)
            return
        
        # Visszatér a megfelelő üzenettel
        return "Let's start by choosing a pizza. Once you've decided on the pizza, we can proceed with selecting the size"
    
    # Ha a pizza már rendelkezik mérettek, akkor a megfelelő üzenettel tér vissza
    if pizza_order.size != None:
        return "We already have the size for your pizza."
    
    # Beállítja a pizza méretét
    pizza_order.size = size

# Feldolgozza a feltétre vonatkozó szándékot
def process_intent_pizza_topping(topping):
    global pizza_order
    
    # Ellenőrzi, hogy a felhasználó rendelt-e már pizzát.
    if pizza_order == None:
        # Ellenőrzi, hogy található-e rendeléssel kapcsolatos szándék a jelenlegi szánék előtt
        if has_order_intent_relative_position("before"):
            # Létrehozza a rendelést és hozzáadja a megadott feltétet
            pizza_order = Pizza()
            pizza_order.add_topping(topping)
            return
        
        # Visszatér a megfelelő üzenettel
        return "Before adding toppings, let's make sure we have a pizza order first."
    
    # Ha a megadott feltét szerepel már a pizzán, akkor a megfelelő üzenettel tér vissza
    if pizza_order.has_topping(topping):
        return "We already have this topping on your pizza."
    
    # Hozzáadja a feltétet a pizzához
    pizza_order.add_topping(topping)

# Feldolgozza a pizza típusára vonatkozó szándékot
def process_intent_pizza_type(pizza_type):
    global pizza_order
    # Ellenőrzi, hogy a felhasználó rendelt-e már pizzát.
    if pizza_order == None:
        # Ellenőrzi, hogy található-e rendeléssel kapcsolatos szándék a jelenlegi szánék előtt
        if has_order_intent_relative_position("before"):
            # Létrehozza a rendelést a megadott típussal
            pizza_order = Pizza(type_=pizza_type)
            return
        
        # Visszatér a megfelelő üzenettel
        return "Before choosing the type, let's make sure we have a pizza order first."
     
    # Ha a pizza már rendelkezik típussal, akkor a megfelelő üzenettel tér vissza
    if pizza_order.type_ != None:
        return "We already have the type for your pizza."
    
    pizza_order.type_ = pizza_type

# Feldolgozza a ital típusára vonatkozó szándékot
def process_intent_drink_type(drink_type):
    global drink_order
    
    # Ellenőrzi, hogy a felhasználó rendelt-e már italt.
    if drink_order == None:
        # Létrehozza a rendelést a megadott típussal
        drink_order = Drink(type_=drink_type)
        return None
    
    # Ha az ital már rendelkezik típussal, akkor a megfelelő üzenettel tér vissza
    return "We already have the type for your drink."

# Feldolgozza a szándékokat és visszatérhet egy hibaüzenettel
def process_intent(intent, keyword):
    global pizza_order, drink_order
    
    # A szándék feldolgozása
    if intent == "order_pizza":
        # Ha a felhasználó rendelt már pizzát, akkor figyelmen kívül hagyja a szándékot
        if pizza_order:
            return None
        
        # Létrehozza a rendelést
        pizza_order = Pizza()
    elif intent == "size":
        return process_intent_size(keyword)
    elif intent == "pizza_topping":
        return process_intent_pizza_topping(keyword)
    elif intent == "pizza_type":
        return process_intent_pizza_type(keyword)
    elif intent == "drink_type":
        return process_intent_drink_type(keyword)

# Ellenőrzi a rendelés állapotát és ha szükséges, akkor visszatér egy megfelelő üzenettel
def check_order():
    # Ellenőrzi, hogy a felhasználó rendelt-e már pizzát
    if pizza_order is None:
        return "What type of pizza do you want?"
    else:
        if pizza_order.type_ is None:
            return "What type of pizza do you want?"
        if pizza_order.size is None:
            return "What size pizza do you want?"
        if len(pizza_order.toppings) == 0:
            return "What toppings do you want on your pizza?"
    
    # Ellenőrzi, hogy a felhasználó rendelt-e már italt
    if drink_order is None or drink_order.type_ is None:
        return "What kind of drink do you want?"
    
    return

# Megállapítja, hogy a rendelés véget ért-e
def is_order_completed():
    if pizza_order is None or drink_order is None: 
        return False
    
    return pizza_order.is_completed() and drink_order.is_completed()

# A pizza összefoglalóját adja vissza a rendelkezésre álló adatok alapján.
def get_pizza_order_summary():
    if pizza_order == None:
        return
    
    order_summary = ""
    
    # Méret hozzáadása ha van
    if pizza_order.size is not None:
        order_summary += f"{pizza_order.size} "
        
    # Típus hozzáadása ha van
    if pizza_order.type_ is not None:
        order_summary += f"{pizza_order.type_} "
    
    order_summary += "pizza"
    
    # Feltétek hozzáadása ha vannak
    if len(pizza_order.toppings) > 0:
            # Ha több mint egy van, akkor felsorolás szerűen adja hozzá,
            if len(pizza_order.toppings) > 1:
                toppings_string = ", ".join(pizza_order.toppings[:-1]) + " and " + pizza_order.toppings[-1]
            else:
                toppings_string = pizza_order.toppings[0]
                
            order_summary += f" with {toppings_string}"
    
    return order_summary 

# Az ital összefoglalóját adja vissza a rendelkezésre álló adatok alapján.
def get_drink_order_summary():
    if drink_order is None or drink_order.type_ is None:
        return None
    
    return drink_order.type_

# A metódus visszaigazoló üzenetet generál a rendelésről. 
# A `use_positive_affirmation` meghatározza, hogy a visszaigazolás tartalmazzon-e pozitív megerősítést.
def acknowledge_order(use_positive_affirmation=True):
    order_summary = ""
    
    # Pozitív megerősítés hozzáadása ha szükséges
    if use_positive_affirmation:
        order_summary += select_respone("positive_affirmations") + " "
    
    order_summary += select_respone("order_status") + " "
    
    # A jelenlegi rendelés összegzését lekérdezi
    pizza_summary = get_pizza_order_summary()
    drink_summary = get_drink_order_summary()
    
    # Ha még nincs rendelés, akkor nem generál üzenetet
    if pizza_summary is None and drink_summary is None:
        return
    
    # Ha van pizza rendelés, akkor hozzáadja az üzenethez
    if pizza_summary:
        order_summary += pizza_summary
    
    # Ha van ital rendelés, akkor hozzádja az üzenethez
    if drink_summary:
        # Ha van pizza rendelés, akkor a két rendelés közé beszúr egy összekötő szöveget
        if pizza_summary: order_summary += " and a "
        order_summary += drink_summary
    
    # Visszatér az üzenettel
    return order_summary + "."

def generate_response(user_input):
    # A felismert szándékok eltárolása
    context["detected_intents"] = detect_intents(user_input)

    # Ha az üzenet nem tartalmaz szándékot, akkor a válasz legyen
    if len(context["detected_intents"]) == 0:
        return select_respone("confused")
    
    responses = []
    # Az üzenetben talált szándékokat feldolgozza
    for idx, (intent, keyword) in enumerate(context["detected_intents"]):
        # A jelenlegi szándék index-ét eltárolja, 
        # ez a "has_order_intent_relative_position()" függvény számára szükséges
        context["intent_index"] = idx
        
        error_message = process_intent(intent, keyword)
        
        # Ha a feldolgozás közben hiba történt
        # és még nincs hibaüzenet a válaszok között, 
        # akkor hozzáadja a válaszokhoz az üzenetet
        if error_message and len(responses) == 0:
            responses.append(error_message)
    
    
    # Ha van visszaigazoló üzenetet akkor a válaszokhoz hozzáadja
    # Pozitív megerősítést csak akkor használ ha a visszaigazoló
    # üzenet a legelső mondat a válaszok között
    acknowledgement_result = acknowledge_order(len(responses) == 0)
    if acknowledgement_result:
        responses.append(acknowledgement_result)
    
    # Ellenőrzi a rendelés állapotát
    order_result = check_order()
    
    # Ha visszatért üzenettel, akkor hozzáadja a válaszokhoz,
    # ha nem akkor ellenőrzi, hogy a rendelés teljesítve van-e
    if order_result:
        responses.append(order_result)
    elif is_order_completed():
        responses.append("We are done!")
    
    # A válaszokat egyetlen karakterlánccá egyesíti, 
    # szóközöket használva elválasztóként.
    return " ".join(responses)

# A nyugta lekérése
def get_receipt():
    if not is_order_completed(): return None
    
    pizza_receipt = pizza_order.get_receipt()
    drink_receipt = drink_order.get_receipt()
    total = pizza_receipt["price"] + drink_receipt["price"]
    
    return {
        "pizza": pizza_receipt,
        "drink": drink_receipt,
        "total": total,
    }

# A "WebServer" osztály kezeli a beérkező kéréseket
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global context, pizza_order, drink_order
        # A rendelés visszaállítása
        context = {
            "intent_index": 0,
            "detected_intents": [],
            "current_keyword": None
        }
        pizza_order = None
        drink_order = None
        
        # A gyökérútvonal ("/") kérés átirányítása a "index.html" címre.
        if self.path == "/":
            self.path = "index.html"
        
        file_path = f"./static/{self.path}"
        if os.path.isfile(file_path):
            # Fájl tartalmának beolvasása
            with open(file_path, encoding="utf-8") as f:
                content = f.read().encode("utf-8")
            
            # Válasz küldése a kérésre
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content)
            
            return
            
        # Nem létező fájl esetén 404-es hiba
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<h1>404: page not found</h1>".encode("utf-8"))
        
    def do_POST(self):
        # "/chat" kérés kezelése
        if self.path == "/chat":
            # Beérkezett üzenet beolvasása
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # A válasz
            response_data = {
                "message": generate_response(post_data.decode()),
                "receipt": get_receipt()
            }
            response_json = json.dumps(response_data)
            
            # Válasz visszaküldése
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response_json.encode())
            
            return
        
        # Ha a kért útvonal nem "/chat", akkor 404-es hibát küld vissza
        self.send_response_only(404)

if __name__ == "__main__":
    # Létrehozza a http szervert a megadott kiszolgálócím és a "WebServer" osztály, mint kezelő használatával
    httpd = ThreadingHTTPServer(SERVER_ADDRESS, WebServer)
    
    # Szerverrel kapcsolatos információ kiírása
    print(f"Server started on `{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}`!")
    print(f"Press CTRL+C to stop the server.")
    
    try:
        # Kérések kiszolgálása korlátlan ideig
        httpd.serve_forever()
    except KeyboardInterrupt:
        # CTRL+C lenyomásakor a szerver leállítása
        print("Stopping server...")
        httpd.shutdown()