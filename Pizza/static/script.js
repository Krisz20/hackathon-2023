// A chat üzenetek és a beviteli mező tároló eleme
const chat_container = document.querySelector(".chat-container");
const message_input = document.querySelector("input");

// A üzenetek feladójának nevét jelölő konstansok
const SENDER_USER = "User";
const SENDER_ASSISTANT = "Assistant";

let isOrderCompleted = false;
function completeOrder(){
    message_input.disabled = true
    isOrderCompleted = true;
}

// Az asszisztens által megjeleníthető üdvözletek tömbje
const greetings = [
    "Welcome! What can I get for you today?",
    "Hello! How may I assist you with your order?",
    "Greetings! What would you like to order?",
    "Hi there! What can I help you order?",
    "Hi! What can I add to your order to make it perfect?",
];

// Létrehozza és visszaadja a megadott feladóval rendelkező üzenet DOM-elemét.
function generateMessageDOM(sender, message) {
    const messageDiv = document.createElement("div");
    
    // A küldő szerint állítja be az üzenet osztályát
    if(sender == SENDER_ASSISTANT){
        messageDiv.classList.add("assistant-message");
    } else {
        messageDiv.classList.add("user-message");
    }

    const senderName = document.createElement("b");
    senderName.textContent = sender + ":";

    const lineBreak = document.createElement("br");
    const messageContent = document.createTextNode(message);

    messageDiv.appendChild(senderName);
    messageDiv.appendChild(lineBreak);
    messageDiv.appendChild(messageContent);

    return messageDiv;
}

// Létrehozza és beilleszti a nyugta DOM-elemét a beszélgetésbe.
function appendReceiptDOM(pizza, drink, total) {
    const assistantMessage = document.createElement("div");
    assistantMessage.className = "assistant-message";
  
    const assistantName = document.createElement("b");
    assistantName.textContent = SENDER_ASSISTANT + ":";
  
    const receipt = document.createElement("div");
    receipt.className = "receipt";
  
  
    function createItemDOM(label, details) {
        const item = document.createElement("div");
        item.className = "item";
    
        const itemLabel = document.createElement("span");
        itemLabel.className = "item-label";
        itemLabel.textContent = label;
    
        const itemDetails = document.createElement("span");
        itemDetails.className = "item-details";
        itemDetails.textContent = details;
    
        item.appendChild(itemLabel);
        item.appendChild(itemDetails);
    
        return item;
    }
    
    const pizzaItem = createItemDOM("Pizza:", `${pizza.name} - $${pizza.price}`);
    const drinkItem = createItemDOM("Drink:", `${drink.name} - $${drink.price}`);
    const totalItem = createItemDOM("Total:", `$${total}`);
    
    const separator = document.createElement("hr");

    receipt.appendChild(pizzaItem);
    receipt.appendChild(drinkItem);
    receipt.appendChild(separator);
    receipt.appendChild(totalItem);
  
    assistantMessage.appendChild(assistantName);
    assistantMessage.appendChild(receipt);
  
    chat_container.appendChild(assistantMessage);
}

// A chat konténerbe beszúrja az üzenetet
function appendMessage(sender, message){
    const message_element = generateMessageDOM(sender, message);
    chat_container.appendChild(message_element)

    // A chat aljára ugrik automatikusan
    chat_container.scrollTop = chat_container.scrollHeight;
}

// Üzenet küldése és fogadása
async function sendMessage(message){
    // Ha a rendelés már véget ért, akkor megakadályozza a további üzenetek küldését
    if(isOrderCompleted) return;

    appendMessage(SENDER_USER, message);

    // Elküldi az üzenetet a szervernek
    const request = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "text/plain"},
        body: message,
    });
    
    // A válasz fogadása és megjelenítése a felhasználó számára
    const response = await request.json();
    appendMessage(SENDER_ASSISTANT, response["message"]);

    // Ha a válasz tartalmazza a rendelési állományt, akkor a rendelés véget ért
    if(response["receipt"] != null){
        completeOrder();
        const receipt = response["receipt"];
        appendReceiptDOM(receipt["pizza"], receipt["drink"], receipt["total"]);
    }
}

document.querySelector("form").addEventListener("submit", async(e)=>{
    e.preventDefault();

    // A beviteli mező értékét lekérdezi
    const message = message_input.value;
    // Törli a beviteli mező értékét
    message_input.value = "";
    sendMessage(message);
});

window.addEventListener("load", ()=>{
    // Kiválaszt egy véletlenszerű üdvözlést és elküldi a felhasználónak
    const greeting = greetings[Math.floor(Math.random()*greetings.length)];
    appendMessage(SENDER_ASSISTANT, greeting);
});