import streamlit as st
import requests
import math
import random
from datetime import datetime


# ============================================================
# MOODMATCH
# AI COMPANION + REAL WORLD EXPERIENCE ENGINE
# ============================================================

st.set_page_config(
    page_title="MoodMatch",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state():

    defaults = {
        "page": "Home",

        "messages": [
            {
                "role": "assistant",
                "content": (
                    "Hey 👋 I'm your MoodMatch companion. "
                    "Tell me how you're feeling, and I'll figure out "
                    "whether you need someone to talk to or a change of scene."
                )
            }
        ],

        "mood": "Normal",
        "mood_intensity": 5,

        "user_name": "Friend",

        "companion_name": "Momo",
        "companion_style": "Caring Friend",
        "companion_language": "English",
        "companion_slang": "",
        "companion_call_name": "Friend",

        "location": "",
        "latitude": None,
        "longitude": None,

        "budget": 1000,
        "travel_time": 30,
        "people": 1,

        "selected_place": None,
        "journey_started": False,
        "arrived": False,
        "journey_completed": False,

        "before_mood": None,
        "after_mood": None,

        "saved_experiences": [],

        "voice_uploaded": False,
        "voice_type": "My own / authorized voice",

        "last_recommendations": []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 19px;
        color: #777;
        margin-bottom: 30px;
    }

    .mood-card {
        padding: 25px;
        border-radius: 20px;
        background: rgba(100, 120, 255, 0.08);
        border: 1px solid rgba(100, 120, 255, 0.15);
        margin-bottom: 15px;
    }

    .place-card {
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }

    .big-button {
        font-size: 20px !important;
        padding: 20px !important;
    }

    .journey-box {
        padding: 25px;
        border-radius: 20px;
        background: rgba(0, 180, 120, 0.08);
        border: 1px solid rgba(0, 180, 120, 0.2);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MOOD ENGINE
# ============================================================

def detect_mood(text):

    text = text.lower()

    mood_keywords = {
        "Happy": [
            "happy", "great", "awesome", "good",
            "excited", "amazing", "joy", "fun"
        ],

        "Sad": [
            "sad", "down", "cry", "crying",
            "upset", "hurt", "unhappy"
        ],

        "Lonely": [
            "lonely", "alone", "nobody",
            "isolated", "miss someone"
        ],

        "Angry": [
            "angry", "mad", "furious",
            "annoyed", "irritated"
        ],

        "Anxious": [
            "anxious", "anxiety", "worried",
            "nervous", "stress", "stressed"
        ],

        "Tired": [
            "tired", "exhausted", "sleepy",
            "drained", "energyless"
        ],

        "Bored": [
            "bored", "boring", "nothing to do"
        ]
    }

    scores = {}

    for mood, words in mood_keywords.items():

        scores[mood] = sum(
            1 for word in words if word in text
        )

    if max(scores.values()) == 0:
        return "Normal"

    return max(scores, key=scores.get)


# ============================================================
# AI COMPANION RESPONSE ENGINE
# ============================================================

def companion_response(user_text):

    mood = detect_mood(user_text)

    st.session_state.mood = mood

    name = st.session_state.companion_call_name
    style = st.session_state.companion_style

    slang = st.session_state.companion_slang

    if mood == "Happy":

        response = (
            f"That's nice to hear, {name}! 😄 "
            "You sound like you're in a good mood. "
            "We can keep chatting or make the most of it and plan something fun."
        )

    elif mood == "Sad":

        response = (
            f"I'm here with you, {name}. "
            "You don't have to figure everything out right now. "
            "We can talk, or if you'd rather get out for a while, "
            "I can find something that might feel better."
        )

    elif mood == "Lonely":

        response = (
            f"Hey {name}, you're not alone here. "
            "We can stay and talk for as long as you want. "
            "Or, if you feel like getting around people, "
            "I can find somewhere that isn't too overwhelming."
        )

    elif mood == "Angry":

        response = (
            f"Okay {name}, I won't give you fake-positive advice. "
            "If you want, tell me what happened. "
            "And if you need to burn off some energy, "
            "I can find an activity for that too."
        )

    elif mood == "Anxious":

        response = (
            f"Take it easy, {name}. "
            "We don't have to rush into anything. "
            "We can talk here, or I can find somewhere calm and comfortable."
        )

    elif mood == "Tired":

        response = (
            f"You sound exhausted, {name}. "
            "Maybe going somewhere isn't the answer right now. "
            "We can stay here and keep things quiet."
        )

    elif mood == "Bored":

        response = (
            f"Alright {name}, let's fix that 😄. "
            "We can talk, play around with ideas, "
            "or I can find something interesting for you to do nearby."
        )

    else:

        response = (
            f"Got you, {name}. "
            "Tell me a little more about what's going on, "
            "or choose what you want from me below."
        )

    if slang.strip():
        response += f"\n\n*Communication style: {slang}*"

    return mood, response


# ============================================================
# PLACE SEARCH
# OpenStreetMap / Nominatim
# ============================================================

def search_places(location, keyword):

    if not location:
        return []

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{keyword}, {location}",
        "format": "json",
        "limit": 6
    }

    headers = {
        "User-Agent": "MoodMatch/1.0"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        places = []

        for item in data:

            places.append({
                "name": item.get("display_name", "Unknown place"),
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
                "type": item.get("type", keyword)
            })

        return places

    except Exception:
        return []


# ============================================================
# MOOD → EXPERIENCE
# ============================================================

def get_experience_keywords(mood):

    experiences = {

        "Happy": [
            "amusement park",
            "restaurant",
            "cafe",
            "bowling"
        ],

        "Sad": [
            "library",
            "cafe",
            "park",
            "bookstore"
        ],

        "Lonely": [
            "cafe",
            "park",
            "community centre",
            "restaurant"
        ],

        "Angry": [
            "gym",
            "sports centre",
            "bowling",
            "park"
        ],

        "Anxious": [
            "park",
            "library",
            "cafe",
            "bookstore"
        ],

        "Tired": [
            "cafe",
            "park",
            "library"
        ],

        "Bored": [
            "bowling",
            "cinema",
            "arcade",
            "cafe"
        ],

        "Normal": [
            "cafe",
            "restaurant",
            "park",
            "cinema"
        ]
    }

    return experiences.get(
        mood,
        ["cafe", "park"]
    )


# ============================================================
# DISTANCE
# ============================================================

def calculate_distance(lat1, lon1, lat2, lon2):

    if None in [lat1, lon1, lat2, lon2]:
        return None

    R = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ============================================================
# ESTIMATE COST
# ============================================================

def estimate_cost(distance_km, people, mood):

    if distance_km is None:
        distance_km = 5

    # Simple demo travel estimate
    travel_cost = max(
        40,
        distance_km * 15
    )

    activity_costs = {
        "Happy": 350,
        "Sad": 150,
        "Lonely": 200,
        "Angry": 300,
        "Anxious": 150,
        "Tired": 100,
        "Bored": 300,
        "Normal": 200
    }

    activity_cost = activity_costs.get(
        mood,
        200
    )

    food_cost = 150 * people

    total = (
        travel_cost
        + activity_cost
        + food_cost
    )

    return {
        "travel": round(travel_cost),
        "activity": round(activity_cost),
        "food": round(food_cost),
        "total": round(total),
        "per_person": round(total / max(people, 1))
    }


# ============================================================
# OUTFIT ENGINE
# ============================================================

def outfit_recommendation(mood):

    outfits = {

        "Happy": {
            "clothing": "Casual colorful outfit",
            "color": "Bright or energetic colors",
            "shoes": "Sneakers",
            "hair": "Relaxed everyday hairstyle",
            "accessories": "Minimal accessories"
        },

        "Sad": {
            "clothing": "Comfortable casual outfit",
            "color": "Soft neutral colors",
            "shoes": "Comfortable sneakers",
            "hair": "Simple comfortable hairstyle",
            "accessories": "Minimal accessories"
        },

        "Lonely": {
            "clothing": "Comfortable social-casual outfit",
            "color": "Warm colors",
            "shoes": "Casual sneakers",
            "hair": "Natural hairstyle",
            "accessories": "Simple watch or bracelet"
        },

        "Angry": {
            "clothing": "Comfortable activewear",
            "color": "Dark or strong colors",
            "shoes": "Sports shoes",
            "hair": "Practical hairstyle",
            "accessories": "Keep it minimal"
        },

        "Anxious": {
            "clothing": "Loose comfortable clothing",
            "color": "Calm neutral colors",
            "shoes": "Comfortable shoes",
            "hair": "Simple hairstyle",
            "accessories": "Minimal"
        },

        "Tired": {
            "clothing": "Very comfortable casual outfit",
            "color": "Soft neutral colors",
            "shoes": "Comfortable footwear",
            "hair": "Simple hairstyle",
            "accessories": "Minimal"
        },

        "Bored": {
            "clothing": "Fun casual outfit",
            "color": "Something that makes you feel energetic",
            "shoes": "Sneakers",
            "hair": "Your preferred casual style",
            "accessories": "One statement accessory"
        },

        "Normal": {
            "clothing": "Smart casual outfit",
            "color": "Neutral or favorite color",
            "shoes": "Casual shoes",
            "hair": "Your normal style",
            "accessories": "Simple accessories"
        }
    }

    return outfits.get(
        mood,
        outfits["Normal"]
    )


# ============================================================
# MOOD MISSION
# ============================================================

def create_mood_mission(mood, place_name):

    missions = {

        "Happy": [
            "Travel to the destination",
            "Try something fun",
            "Take a few photos",
            "Enjoy your time without rushing",
            "Return home when you're ready"
        ],

        "Sad": [
            "Take a comfortable trip there",
            "Get something you enjoy",
            "Spend some quiet time",
            "Do one small activity",
            "Return home and check in with yourself"
        ],

        "Lonely": [
            "Travel somewhere comfortable",
            "Spend some time around people",
            "Try one small social activity",
            "Message or talk to someone you trust if you want",
            "Return home when you're ready"
        ],

        "Angry": [
            "Travel safely",
            "Do something physical or distracting",
            "Give yourself time to cool down",
            "Avoid making major decisions while angry",
            "Return home when you're ready"
        ],

        "Anxious": [
            "Take the easiest comfortable route",
            "Spend a few minutes settling in",
            "Do something familiar",
            "Take your time",
            "Return home when you feel ready"
        ],

        "Tired": [
            "Travel only if you feel comfortable",
            "Choose a quiet place",
            "Rest and recharge",
            "Avoid over-planning",
            "Head home and rest"
        ],

        "Bored": [
            "Travel to the destination",
            "Try something you've never done",
            "Spend time enjoying the activity",
            "Take a short break",
            "Return home with a new experience"
        ],

        "Normal": [
            "Travel to the destination",
            "Explore the place",
            "Try something you enjoy",
            "Take a break",
            "Return home"
        ]
    }

    return missions.get(
        mood,
        missions["Normal"]
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# 💙 MoodMatch")

    st.caption(
        "Your mood. Your companion. Your world."
    )

    st.divider()

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"

    if st.button("💬 AI Companion", use_container_width=True):
        st.session_state.page = "Chat"

    if st.button("🌎 Find an Experience", use_container_width=True):
        st.session_state.page = "Places"

    if st.button("🚀 My Journey", use_container_width=True):
        st.session_state.page = "Journey"

    if st.button("👤 Companion Profile", use_container_width=True):
        st.session_state.page = "Profile"

    st.divider()

    st.markdown("### Current mood")

    st.info(
        f"**{st.session_state.mood}**"
    )


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "Home":

    st.markdown(
        '<div class="main-title">💙 MoodMatch</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Your AI companion that connects how you feel '
        'with what you can experience in the real world.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        ### What do you need right now?
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💬 Talk to Me",
            use_container_width=True
        ):

            st.session_state.page = "Chat"

            st.rerun()

        st.caption(
            "Talk, vent, ask for advice, or just have someone there."
        )

    with col2:

        if st.button(
            "🌎 Take Me Somewhere",
            use_container_width=True
        ):

            st.session_state.page = "Places"

            st.rerun()

        st.caption(
            "Let MoodMatch create a real-world experience for you."
        )

    st.divider()

    st.markdown("### 🧠 Your companion understands")

    cards = st.columns(4)

    cards[0].metric(
        "Mood",
        st.session_state.mood
    )

    cards[1].metric(
        "People",
        st.session_state.people
    )

    cards[2].metric(
        "Budget",
        f"₹{st.session_state.budget}"
    )

    cards[3].metric(
        "Travel",
        f"{st.session_state.travel_time} min"
    )

    st.markdown(
        """
        <div class="mood-card">

        <h3>✨ MoodMatch is not just a chatbot</h3>

        <p>
        Talk to your companion. Let it understand your situation.
        If you want to go somewhere, it can turn that conversation
        into a personalized experience.
        </p>

        <p>
        <b>Talk → Understand → Plan → Go → Accompany → Learn</b>
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# AI CHAT
# ============================================================

elif st.session_state.page == "Chat":

    st.title("💬 Your AI Companion")

    st.caption(
        f"{st.session_state.companion_name} • "
        f"{st.session_state.companion_style}"
    )

    # Display conversation

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    st.divider()

    # Quick actions

    st.markdown("### What do you want from me?")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "🫂 Just listen",
            use_container_width=True
        ):

            response = (
                "Okay. I won't try to fix everything. "
                "I'm listening. Tell me what's going on."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    with col2:

        if st.button(
            "🌎 Get me out",
            use_container_width=True
        ):

            st.session_state.page = "Places"

            st.rerun()

    with col3:

        if st.button(
            "😶 Stay with me",
            use_container_width=True
        ):

            response = (
                "I'm here. You don't have to talk. "
                "We can just stay here for a while."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    # Chat input

    user_message = st.chat_input(
        "Tell me how you're feeling..."
    )

    if user_message:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        mood, response = companion_response(
            user_message
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.rerun()


# ============================================================
# PLACES / EXPERIENCE ENGINE
# ============================================================

elif st.session_state.page == "Places":

    st.title("🌎 Create My Experience")

    st.write(
        "I'll use your mood, location, travel comfort, "
        "group size and budget to create an experience."
    )

    st.divider()

    # Mood

    mood = st.selectbox(
        "How are you feeling?",
        [
            "Happy",
            "Normal",
            "Sad",
            "Lonely",
            "Angry",
            "Anxious",
            "Tired",
            "Bored"
        ],
        index=[
            "Happy",
            "Normal",
            "Sad",
            "Lonely",
            "Angry",
            "Anxious",
            "Tired",
            "Bored"
        ].index(st.session_state.mood)
        if st.session_state.mood in [
            "Happy",
            "Normal",
            "Sad",
            "Lonely",
            "Angry",
            "Anxious",
            "Tired",
            "Bored"
        ]
        else 1
    )

    st.session_state.mood = mood

    # Location

    location = st.text_input(
        "📍 Where are you?",
        value=st.session_state.location,
        placeholder="Example: Hyderabad, Telangana"
    )

    st.session_state.location = location

    col1, col2, col3 = st.columns(3)

    with col1:

        budget = st.number_input(
            "💰 Maximum budget (₹)",
            min_value=100,
            max_value=100000,
            value=st.session_state.budget,
            step=100
        )

        st.session_state.budget = budget

    with col2:

        travel_time = st.slider(
            "🚗 Maximum travel time",
            min_value=5,
            max_value=120,
            value=st.session_state.travel_time,
            step=5
        )

        st.session_state.travel_time = travel_time

    with col3:

        people = st.number_input(
            "👥 Number of people",
            min_value=1,
            max_value=20,
            value=st.session_state.people
        )

        st.session_state.people = people

    st.divider()

    if st.button(
        "✨ Find My Experience",
        type="primary",
        use_container_width=True
    ):

        if not location:

            st.warning(
                "Please enter your location first."
            )

        else:

            keywords = get_experience_keywords(
                mood
            )

            all_places = []

            progress = st.progress(0)

            for i, keyword in enumerate(keywords):

                places = search_places(
                    location,
                    keyword
                )

                all_places.extend(
                    places
                )

                progress.progress(
                    (i + 1) / len(keywords)
                )

            # Remove duplicate names

            unique = {}

            for place in all_places:

                unique[
                    place["name"]
                ] = place

            recommendations = list(
                unique.values()
            )

            # Demo distance estimate
            for place in recommendations:

                place["distance"] = round(
                    random.uniform(
                        1,
                        max(
                            2,
                            travel_time / 3
                        )
                    ),
                    1
                )

                place["cost"] = estimate_cost(
                    place["distance"],
                    people,
                    mood
                )

            recommendations = [
                p for p in recommendations
                if p["cost"]["total"] <= budget
            ]

            st.session_state.last_recommendations = (
                recommendations
            )

    recommendations = (
        st.session_state.last_recommendations
    )

    if recommendations:

        st.success(
            f"I found {len(recommendations)} "
            "possible experiences for you."
        )

        for index, place in enumerate(
            recommendations[:6]
        ):

            with st.container():

                st.markdown(
                    '<div class="place-card">',
                    unsafe_allow_html=True
                )

                st.subheader(
                    f"{index + 1}. "
                    + place["name"].split(",")[0]
                )

                st.write(
                    f"📍 Approx. {place['distance']} km away"
                )

                st.write(
                    f"💰 Estimated total: "
                    f"₹{place['cost']['total']}"
                )

                st.write(
                    f"👤 Per person: "
                    f"₹{place['cost']['per_person']}"
                )

                st.caption(
                    f"Travel ₹{place['cost']['travel']} "
                    f"+ Activity ₹{place['cost']['activity']} "
                    f"+ Food ₹{place['cost']['food']}"
                )

                if st.button(
                    "Choose this experience",
                    key=f"choose_{index}"
                ):

                    st.session_state.selected_place = place

                    st.session_state.page = "Journey"

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

    else:

        if location:

            st.info(
                "No suitable places found within "
                "the current budget. Try increasing "
                "your budget or travel time."
            )


# ============================================================
# JOURNEY
# ============================================================

elif st.session_state.page == "Journey":

    st.title("🚀 Your Mood Mission")

    place = st.session_state.selected_place

    if not place:

        st.info(
            "You haven't selected an experience yet."
        )

        if st.button("Find an experience"):

            st.session_state.page = "Places"

            st.rerun()

    else:

        place_name = place["name"].split(",")[0]

        st.success(
            f"Your selected destination: **{place_name}**"
        )

        st.markdown(
            "### 🧠 Why MoodMatch chose this"
        )

        st.write(
            f"You're feeling **{st.session_state.mood}**. "
            "This experience was selected based on your "
            "current mood, travel preference, group size "
            "and budget."
        )

        # Mission

        st.markdown("### 🎯 Your Mood Mission")

        mission = create_mood_mission(
            st.session_state.mood,
            place_name
        )

        for i, step in enumerate(
            mission,
            start=1
        ):

            st.write(
                f"**{i}.** {step}"
            )

        st.divider()

        # Cost

        st.markdown("### 💰 Estimated cost")

        cost = place["cost"]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Travel",
            f"₹{cost['travel']}"
        )

        c2.metric(
            "Activity",
            f"₹{cost['activity']}"
        )

        c3.metric(
            "Food",
            f"₹{cost['food']}"
        )

        c4.metric(
            "Total",
            f"₹{cost['total']}"
        )

        st.divider()

        # Outfit

        st.markdown("### 👕 Your AI Style Suggestion")

        outfit = outfit_recommendation(
            st.session_state.mood
        )

        o1, o2 = st.columns(2)

        with o1:

            st.write(
                f"👕 **Clothing:** {outfit['clothing']}"
            )

            st.write(
                f"🎨 **Color:** {outfit['color']}"
            )

            st.write(
                f"👟 **Shoes:** {outfit['shoes']}"
            )

        with o2:

            st.write(
                f"💇 **Hair:** {outfit['hair']}"
            )

            st.write(
                f"✨ **Accessories:** {outfit['accessories']}"
            )

        st.divider()

        # Before mood

        if not st.session_state.journey_started:

            st.markdown(
                "### ❤️ Before you go"
            )

            before_mood = st.slider(
                "How do you feel right now?",
                1,
                10,
                5
            )

            st.session_state.before_mood = (
                before_mood
            )

            if st.button(
                "🚀 START MY JOURNEY",
                type="primary",
                use_container_width=True
            ):

                st.session_state.journey_started = True

                st.success(
                    "Journey started. Your companion "
                    "is with you."
                )

                st.rerun()

        else:

            st.markdown(
                '<div class="journey-box">',
                unsafe_allow_html=True
            )

            st.subheader(
                "🚗 Journey in progress"
            )

            if not st.session_state.arrived:

                st.write(
                    "Your AI companion is available "
                    "during the journey."
                )

                st.info(
                    "💬 You can return to AI Chat "
                    "and talk while travelling."
                )

                if st.button(
                    "📍 I'M HERE",
                    type="primary",
                    use_container_width=True
                ):

                    st.session_state.arrived = True

                    st.rerun()

            else:

                st.success(
                    "📍 You've marked yourself as arrived."
                )

                st.write(
                    "Enjoy your experience. "
                    "I'll be here when you need me."
                )

                if st.button(
                    "🏠 I'M HOME",
                    use_container_width=True
                ):

                    st.session_state.journey_completed = True

                    st.rerun()

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        # Feedback

        if st.session_state.journey_completed:

            st.divider()

            st.markdown(
                "## 💙 How did it go?"
            )

            after_mood = st.slider(
                "How do you feel now?",
                1,
                10,
                7,
                key="after_mood_slider"
            )

            st.session_state.after_mood = (
                after_mood
            )

            if st.button(
                "Save my experience",
                type="primary"
            ):

                experience = {

                    "date": datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),

                    "place": place_name,

                    "mood": st.session_state.mood,

                    "before": st.session_state.before_mood,

                    "after": after_mood,

                    "improvement":
                        after_mood
                        - st.session_state.before_mood
                }

                st.session_state.saved_experiences.append(
                    experience
                )

                st.success(
                    "Saved. MoodMatch will use this "
                    "to personalize future experiences."
                )


# ============================================================
# PROFILE / COMPANION CUSTOMIZATION
# ============================================================

elif st.session_state.page == "Profile":

    st.title("👤 Your Companion")

    st.write(
        "Customize how your AI companion talks, "
        "sounds and behaves."
    )

    st.divider()

    st.markdown(
        "### 🧠 Companion Identity"
    )

    companion_name = st.text_input(
        "Companion name",
        value=st.session_state.companion_name
    )

    st.session_state.companion_name = (
        companion_name
    )

    call_name = st.text_input(
        "What should your companion call you?",
        value=st.session_state.companion_call_name
    )

    st.session_state.companion_call_name = (
        call_name
    )

    style = st.selectbox(
        "Personality",
        [
            "Caring Friend",
            "Funny Friend",
            "Older Sibling",
            "Calm Companion",
            "Motivator",
            "Playful Friend",
            "Custom"
        ]
    )

    st.session_state.companion_style = style

    language = st.selectbox(
        "Language",
        [
            "English",
            "Telugu",
            "Telugu + English",
            "Hindi",
            "Hindi + English"
        ]
    )

    st.session_state.companion_language = language

    slang = st.text_area(
        "How should your companion talk?",
        value=st.session_state.companion_slang,
        placeholder=(
            "Example: Talk casually. "
            "Use ra, rey, babai sometimes. "
            "Don't sound like a formal AI."
        )
    )

    st.session_state.companion_slang = slang

    st.divider()

    st.markdown(
        "### 🎙️ Voice Companion"
    )

    st.info(
        "Voice cloning is reserved for an authorized "
        "voice in this prototype. A production version "
        "should include explicit consent verification."
    )

    voice_type = st.selectbox(
        "Voice type",
        [
            "My own / authorized voice",
            "Living person's authorized voice",
            "Memory Companion"
        ]
    )

    st.session_state.voice_type = voice_type

    uploaded_voice = st.file_uploader(
        "Upload a voice recording",
        type=[
            "wav",
            "mp3",
            "m4a",
            "ogg"
        ]
    )

    if uploaded_voice:

        st.session_state.voice_uploaded = True

        st.success(
            "Voice recording uploaded."
        )

        st.audio(
            uploaded_voice
        )

    st.divider()

    if st.button(
        "💾 Save Companion Settings",
        type="primary"
    ):

        st.success(
            "Your companion settings have been saved."
        )


# ============================================================
# FALLBACK
# ============================================================

else:

    st.session_state.page = "Home"

    st.rerun()