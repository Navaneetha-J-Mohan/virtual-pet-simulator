import streamlit as st
import random
import time
import base64

from PIL import Image
import base64

def set_background(animal):
    """Set a custom background image based on the pet type."""
    image_path = f"images/{animal.lower()}_bg.jpg"
    try:
        with open(image_path, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
        bg_style = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(bg_style, unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # fallback if image missing

# --- Animal emojis ---
ANIMAL_EMOJIS = {
    "Dog": "🐶",
    "Cat": "🐱",
    "Rabbit": "🐰",
    "Bird": "🐦",
    "Fish": "🐠",
    "Hamster": "🐹"
}

# --- Initialize session state ---
if "pets" not in st.session_state:
    st.session_state.pets = {}
if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = None
if "event_message" not in st.session_state:
    st.session_state.event_message = ""

# --- Utility functions ---
def color_progress(value):
    """Return color based on percentage value."""
    if value > 70:
        return "🟩"
    elif value > 40:
        return "🟨"
    else:
        return "🟥"

def create_pet(name, animal):
    pet = {
        "name": name,
        "animal": animal,
        "emoji": ANIMAL_EMOJIS[animal],
        "happiness": 50,
        "hunger": 50,
        "health": 100,
        "actions": 0
    }
    st.session_state.pets[name] = pet
    st.session_state.selected_pet = name
    st.success(f"🎉 Welcome, {pet['emoji']} {pet['name']} the {animal.lower()}!")

def adjust_stats(pet):
    for key in ["happiness", "hunger", "health"]:
        pet[key] = max(0, min(100, pet[key]))

def automatic_changes(pet):
    if pet["actions"] % 3 == 0 and pet["actions"] > 0:
        pet["hunger"] += 5
        pet["happiness"] -= 5
        pet["health"] -= 2
        st.session_state.event_message = f"⏳ Time passes... {pet['name']} feels a bit hungrier and less happy."
        adjust_stats(pet)

def random_event(pet):
    events = [
        (f"{pet['name']} found a snack! 🍪 Hunger decreases.", -10, 0, 0),
        (f"{pet['name']} took a nap 😴 Happiness increases.", 0, +10, 0),
        (f"Oh no! {pet['name']} got sick 🤒 Health decreases.", 0, -5, -20),
        (f"{pet['name']} met a friend 🐕 Happiness increases!", 0, +15, 0),
        (f"{pet['name']} played too much and got tired 😓", +10, -10, -5)
    ]
    if random.random() < 0.3:
        event, hunger_change, happiness_change, health_change = random.choice(events)
        st.session_state.event_message = f"🎲 Random Event: {event}"
        pet["hunger"] += hunger_change
        pet["happiness"] += happiness_change
        pet["health"] += health_change
        adjust_stats(pet)

def perform_action(pet, action):
    st.session_state.event_message = ""
    if action == "Feed":
        pet["hunger"] -= 20
        pet["happiness"] -= 5
        msg = f"You fed {pet['emoji']} {pet['name']} 🍖"
    elif action == "Play":
        pet["happiness"] += 15
        pet["hunger"] += 10
        msg = f"You played with {pet['emoji']} {pet['name']} 🎾"
    elif action == "Give Toy":
        pet["happiness"] += 10
        pet["hunger"] += 5
        msg = f"You gave {pet['emoji']} {pet['name']} a toy 🧸"
    elif action == "Give Medicine":
        if pet["health"] < 100:
            pet["health"] += 20
            pet["happiness"] -= 5
            msg = f"You gave {pet['emoji']} {pet['name']} medicine 💊"
        else:
            msg = f"{pet['emoji']} {pet['name']} is already healthy!"
    else:
        msg = "Unknown action."

    pet["actions"] += 1
    adjust_stats(pet)
    automatic_changes(pet)
    random_event(pet)
    st.success(msg)

    # 🎉 Confetti when happiness maxes out
    if pet["happiness"] >= 100:
        st.balloons()
        st.toast(f"🎊 {pet['name']} is overjoyed! Happiness MAXED OUT!", icon="🎉")

def check_game_over(pet):
    if pet["hunger"] >= 100:
        st.error(f"💀 {pet['name']} became too hungry! Game over.")
        del st.session_state.pets[pet["name"]]
        st.session_state.selected_pet = None
        return True
    elif pet["happiness"] <= 0:
        st.error(f"💔 {pet['name']} became too sad and ran away.")
        del st.session_state.pets[pet["name"]]
        st.session_state.selected_pet = None
        return True
    elif pet["health"] <= 0:
        st.error(f"☠️ {pet['name']} got too sick. Game over.")
        del st.session_state.pets[pet["name"]]
        st.session_state.selected_pet = None
        return True
    return False

def play_ambient_sound(animal):
    """Play local ambient sound for the pet type."""
    sound_path = f"sounds/{animal.lower()}.mp3"
    try:
        with open(sound_path, "rb") as sound_file:
            sound_bytes = sound_file.read()
            encoded_sound = base64.b64encode(sound_bytes).decode()
        st.markdown(
            f"""
            <audio autoplay loop>
                <source src="data:audio/mp3;base64,{encoded_sound}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning(f"No sound found for {animal}. (Expected at: {sound_path})")

# --- Sidebar: Create or Select Pet ---
st.sidebar.header("🐾 Create or Select Pet")
name = st.sidebar.text_input("Enter pet name:")
animal = st.sidebar.selectbox("Choose animal:", list(ANIMAL_EMOJIS.keys()))
if st.sidebar.button("Create Pet"):
    if name.strip():
        create_pet(name.strip().capitalize(), animal)
    else:
        st.sidebar.warning("Please enter a valid pet name.")

if st.session_state.pets:
    selected = st.sidebar.selectbox(
        "Select a pet:",
        options=list(st.session_state.pets.keys()),
        index=list(st.session_state.pets.keys()).index(st.session_state.selected_pet)
        if st.session_state.selected_pet in st.session_state.pets else 0
    )
    st.session_state.selected_pet = selected

# --- Main Interface ---
st.title("🏡 Virtual Pet Simulator (Animated)")

if not st.session_state.pets:
    st.info("Create a pet using the sidebar to get started!")
else:
    pet = st.session_state.pets[st.session_state.selected_pet]
    st.subheader(f"{pet['emoji']} {pet['name']} the {pet['animal']}")

    # 🖼️ Set dynamic background based on pet type
    set_background(pet["animal"])

    # 🎵 Play matching ambient sound
    play_ambient_sound(pet["animal"])

    # 🐕 Show pet image (optional)
    image_path = f"images/{pet['animal'].lower()}_pic.png"
    try:
        st.image(image_path, width=200)
    except:
        st.write(f"{pet['emoji']} (no image found, but still adorable!)")

    # Display dynamic color bars using emojis
    st.write(f"😊 Happiness: {color_progress(pet['happiness'])} {pet['happiness']}")
    st.progress(pet["happiness"] / 100)

    st.write(f"🍽️ Hunger: {color_progress(100 - pet['hunger'])} {pet['hunger']}")
    st.progress(1 - (pet["hunger"] / 100))

    st.write(f"💊 Health: {color_progress(pet['health'])} {pet['health']}")
    st.progress(pet["health"] / 100)

    # --- Action Buttons ---
    cols = st.columns(4)
    actions = ["Feed", "Play", "Give Toy", "Give Medicine"]
    for i, action in enumerate(actions):
        if cols[i].button(action):
            perform_action(pet, action)
            if check_game_over(pet):
                break

    # --- Event Message ---
    if st.session_state.event_message:
        st.info(st.session_state.event_message)
        time.sleep(0.5)
