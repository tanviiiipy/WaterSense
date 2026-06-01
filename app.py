import streamlit as st
import pandas as pd
import numpy as np
import random

# ------------------- GLOBAL CONFIG -------------------
APP_NAME = "💧 WaterSense"
TEAM_NAME = "Pseudocoders"
WATER_FACTS = [
    "A single leaky faucet can waste over 3,000 gallons per year.",
    "97% of the earth’s water is salt water.",
    "Freshwater makes up only about 2.5% of all water on Earth.",
    "It takes about 2,000 gallons of water to produce one pound of beef.",
    "Turning off the tap while brushing teeth saves up to 8 gallons a day."
]

TEAM_MEMBERS = [
    {"name": "Tanvi"},
    {"name": "Neha"},
    {"name": "Riya"},
    {"name": "Nikhita"}
]

# ------------------- STATE INIT -------------------
if "sensors" not in st.session_state:
    st.session_state["sensors"] = []
if "notifications" not in st.session_state:
    st.session_state["notifications"] = []
if "settings" not in st.session_state:
    st.session_state["settings"] = {"theme": "Light", "refresh": 15, "enable_notif": True}
if "game_score_history" not in st.session_state:
    st.session_state["game_score_history"] = []
if "challenge_checklist" not in st.session_state:
    st.session_state["challenge_checklist"] = {
        "Fix a leak": False,
        "Turn off tap while brushing": False,
        "Take a short shower": False,
        "Install water-saving aerator": False,
        "Water plants early morning": False,
        "Share a water fact": False
    }
if "game_score" not in st.session_state:
    st.session_state["game_score"] = 0
if "game_missed" not in st.session_state:
    st.session_state["game_missed"] = 0
if "game_bucket" not in st.session_state:
    st.session_state["game_bucket"] = "middle"
if "game_drop_col" not in st.session_state:
    st.session_state["game_drop_col"] = np.random.choice(["left", "middle", "right"])
if "game_playing" not in st.session_state:
    st.session_state["game_playing"] = True
if "game_feedback" not in st.session_state:
    st.session_state["game_feedback"] = ""

# ------------------- SENSOR SIMULATION -------------------
def simulate_data(sensor, days=30):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    usage = np.random.randint(10, 100, size=days)
    leak_day = random.choice(range(days))
    usage[leak_day] = random.randint(100, 160)
    sensor["data"] = pd.DataFrame({"date": dates.strftime('%Y-%m-%d'), "usage": usage})

def simulate_all_sensors():
    for sensor in st.session_state["sensors"]:
        simulate_data(sensor)

def get_sensors():
    simulate_all_sensors()
    return st.session_state["sensors"]

# ------------------- SENSORS TAB -------------------
def sensors_page():
    st.title("🛠️ Manage Sensors")
    sensors = get_sensors()
    st.info("Add sensors for different rooms or fixtures!")
    if sensors:
        st.write("### Your Sensors")
        df = pd.DataFrame([{
            "Name": s["name"],
            "Room": s["room"],
            "Active": "✅" if s.get("active") else "❌",
            "Last Update": s["data"]["date"].iloc[-1] if "data" in s else "N/A"
        } for s in sensors])
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No sensors yet. Add one below.")

    with st.expander("➕ Add Sensor", expanded=True):
        with st.form("add_sensor_form"):
            new_name = st.text_input("Sensor Name", placeholder="e.g. Kitchen Tap")
            room = st.text_input("Room", placeholder="e.g. Kitchen")
            active = st.checkbox("Active", value=True)
            submit = st.form_submit_button("Add Sensor")
            if submit and new_name:
                sensor = {"name": new_name, "room": room, "active": active}
                simulate_data(sensor)
                st.session_state["sensors"].append(sensor)
                st.success(f"Sensor '{new_name}' added!")

    if sensors:
        with st.expander("📝 Edit or Delete Sensor"):
            idx = st.selectbox(
                "Select Sensor", list(range(len(sensors))),
                format_func=lambda i: sensors[i]["name"] if "name" in sensors[i] else f"Sensor {i+1}"
            )
            sensor = sensors[idx]
            new_room = st.text_input("Edit Room", value=sensor["room"], key=f"edit_room_{idx}")
            sensor["room"] = new_room
            new_active = st.checkbox("Edit Active", value=sensor.get("active", True), key=f"edit_active_{idx}")
            sensor["active"] = new_active
            if st.button("Update Sensor", key=f"update_{idx}"):
                st.success("Sensor updated.")
            if st.button("Delete Sensor", key=f"delete_{idx}"):
                sensors.pop(idx)
                st.success("Sensor deleted.")
                st.rerun()
            st.divider()
            if "data" in sensor:
                st.write("### Sensor Data")
                st.dataframe(sensor["data"], use_container_width=True)
                if st.button("Resimulate Data", key=f"resim_{idx}"):
                    simulate_data(sensor)
                    st.success("Simulated data updated.")
            uploaded = st.file_uploader("Upload Data CSV", type="csv", key=f"csv_{idx}")
            if uploaded:
                df = pd.read_csv(uploaded)
                sensor["data"] = df
                st.success("Sensor data updated from CSV.")

# ------------------- DASHBOARD TAB -------------------
def dashboard_page():
    st.title("📊 Water Usage Dashboard")
    sensors = get_sensors()
    st.info("Your analytics update every time you visit!")
    if not sensors:
        st.warning("No sensors yet. Go to **Sensors** to add one.")
        st.image("https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        return
    st.write(f"### You have **{len(sensors)}** sensors")
    total_usage = 0
    chart_df = pd.DataFrame()
    for sensor in sensors:
        if "data" in sensor:
            s = sensor["data"]
            total_usage += s["usage"].sum()
            chart_df[sensor["name"]] = s["usage"].values
    if not chart_df.empty:
        st.subheader("Usage Trends")
        st.line_chart(chart_df)
        st.metric("Total Water Usage (Liters)", total_usage)
        st.metric("Average Daily Usage (Liters)", round(total_usage / len(chart_df), 2))
        st.subheader("🔥 Sensor Highlights")
        cols = st.columns(len(chart_df.columns))
        for i, name in enumerate(chart_df.columns):
            cols[i].metric(
                label=f"{name}",
                value=f"{chart_df[name].sum()} L",
                delta=f"Peak {chart_df[name].max()} L",
            )
        st.subheader("Heatmap")
        st.dataframe(chart_df, use_container_width=True)
        st.info("All readings are randomly simulated for prototype.")
    else:
        st.warning("No data yet. Simulate or upload sensor data.")

    st.divider()
    st.subheader("💡 Tips to Reduce Water Usage")
    st.markdown("""
    - Fix leaks immediately
    - Turn off taps when not needed
    - Use water-saving fixtures
    """)
    st.success("Check out Water Saving Challenge in the sidebar!")

    st.subheader("🤖 AI Suggestions")
    if total_usage > 2000:
        st.warning("AI Suggests: High usage detected! Consider checking for leaks or reducing consumption.")
    else:
        st.info("AI Suggests: Great job! Keep up the water saving.")

    st.divider()
    st.markdown(f"**Fun Water Fact:** {random.choice(WATER_FACTS)}")

# ------------------- ANALYTICS TAB -------------------
def analytics_page():
    st.title("📈 Analytics & Reports")
    sensors = get_sensors()
    for sensor in sensors:
        with st.expander(f"{sensor['name']} ({sensor['room']})"):
            if "data" in sensor:
                df = sensor["data"]
                st.line_chart(df.set_index("date")["usage"])
                st.write("Peak Usage:", df["usage"].max())
                st.write("Lowest Usage:", df["usage"].min())
                leak_days = df[df["usage"] > 95]["date"].tolist()
                if leak_days:
                    st.warning(f"Possible leaks on: {', '.join(leak_days)}")
                st.write("---")
            else:
                st.warning("No data yet. Simulate or upload sensor data.")

    st.subheader("🔄 Compare Sensors")
    comp_df = pd.DataFrame()
    for sensor in sensors:
        if "data" in sensor:
            comp_df[sensor["name"]] = sensor["data"]["usage"]
    if not comp_df.empty:
        st.bar_chart(comp_df)

    st.subheader("📥 Export Data")
    if sensors and st.button("Download CSV"):
        csv = pd.concat([s["data"] for s in sensors if "data" in s]).to_csv(index=False)
        st.download_button("Download all sensor data as CSV", csv, "sensor_data.csv")

    st.subheader("Historical Comparison")
    if sensors:
        for sensor in sensors:
            if "data" in sensor:
                df = sensor["data"]
                avg = df["usage"].mean()
                st.write(f"Sensor {sensor['name']} average usage: {avg:.2f} L")
    st.subheader("Wastage Peaks")
    for sensor in sensors:
        if "data" in sensor:
            df = sensor["data"]
            peaks = df[df["usage"] > df["usage"].mean() + 2 * df["usage"].std()]
            if not peaks.empty:
                st.warning(f"Wastage peaks detected for {sensor['name']} on: {', '.join(peaks['date'])}")

    st.subheader("🤖 AI-powered Suggestions")
    for sensor in sensors:
        if "data" in sensor:
            df = sensor["data"]
            if df["usage"].mean() > 70:
                st.info(f"AI: Try reducing usage on {sensor['name']} by checking fixtures and appliances.")

# ------------------- GAMIFICATION TAB -------------------
BADGES = {
    "water_saver": "Saved < 1000L",
    "sensor_master": "Added 3+ sensors",
    "leak_fixer": "Fixed a leak"
}

def gamification_page():
    st.title("🏅 Achievements & Leaderboard")
    sensors = get_sensors()
    total_usage = sum([s["data"]["usage"].sum() for s in sensors if "data" in s])
    badges = []
    if total_usage < 1000:
        badges.append(BADGES["water_saver"])
    if len(sensors) >= 3:
        badges.append(BADGES["sensor_master"])
    if any("data" in s and (s["data"]["usage"] > 95).any() for s in sensors):
        badges.append(BADGES["leak_fixer"])
    st.write("Your Badges:", badges or "No badges yet.")
    st.progress(min(len(badges) / len(BADGES), 1.0), text=f"{len(badges)} badges earned")
    st.subheader("Leaderboard")
    leaderboard = [
        {"user": "alice", "usage": 800, "badges": ["water_saver"]},
        {"user": "bob", "usage": 1100, "badges": ["sensor_master"]},
        {"user": "You", "usage": total_usage, "badges": badges}
    ]
    st.table(leaderboard)
    st.subheader("🎯 Gamified Goals")
    st.markdown("""
    - Save more water to earn "Water Saver"
    - Add more sensors for "Sensor Master"
    - Fix leaks for "Leak Fixer"
    """)
    if st.button("Check for new badges"):
        st.success(f"Checked! You currently have {len(badges)} badges.")

# ------------------- NOTIFICATIONS TAB -------------------
def notifications_page():
    st.title("🔔 Notifications & Alerts")
    notifs = st.session_state["notifications"]
    st.write("Your notifications:")
    for n in notifs:
        st.info(n)
    if st.button("Send test alert"):
        notifs.append("Test alert: Water usage update!")
        st.success("Alert sent.")
    if st.button("Send leak alert"):
        notifs.append("🚨 Leak detected in one of your sensors!")
        st.warning("Leak alert sent!")
    if st.button("Clear notifications"):
        notifs.clear()
        st.info("Notifications cleared.")

# ------------------- COMMUNITY TAB -------------------
def community_page():
    st.title("🌐 Community")
    st.write("Share your achievements:")
    st.button("Share on social (simulated)")
    st.write("Compare stats with others (simulated leaderboard)")
    leaderboard = [
        {"user": "alice", "usage": 800},
        {"user": "bob", "usage": 1100},
        {"user": "You", "usage": sum([s["data"]["usage"].sum() for s in get_sensors() if "data" in s])}
    ]
    st.table(leaderboard)
    st.subheader("Community Challenges")
    st.markdown("""
    - Save the most water this week!
    - Fix leaks fastest!
    - Add the most sensors!
    """)
    st.write("Invite friends and compete for badges!")

# ------------------- SETTINGS TAB -------------------
def settings_page():
    st.title("⚙️ App Settings")
    settings = st.session_state["settings"]
    theme = st.selectbox("Theme", ["Light", "Dark"], key="theme", index=["Light", "Dark"].index(settings.get("theme", "Light")))
    refresh = st.slider("Sensor refresh interval (mins)", 1, 60, settings.get("refresh", 15), key="refresh")
    enable_notif = st.checkbox("Enable notifications", value=settings.get("enable_notif", True), key="enable_notif")
    st.session_state["settings"] = {
        "theme": theme,
        "refresh": refresh,
        "enable_notif": enable_notif
    }
    st.success("Settings updated.")
    st.write("Current settings:", st.session_state["settings"])
    st.write("Note: Theme is simulated for demo purposes.")

# ------------------- DATA MANAGEMENT TAB -------------------
def data_page():
    st.title("🗂️ Data Management")
    st.write("Upload sensor data (CSV):")
    uploaded = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded:
        st.success("File uploaded.")
    if st.button("Reset all data (simulated)"):
        st.session_state["sensors"] = []
        st.success("All sensor data reset (demo only).")
    st.write("Download demo data, upload new sensor readings, or reset everything for a new hackathon run!")
    if st.button("Download sample data"):
        sample_df = pd.DataFrame({
            "date": pd.date_range(end=pd.Timestamp.today(), periods=10).strftime('%Y-%m-%d'),
            "usage": np.random.randint(10, 80, size=10)
        })
        st.download_button("Download sample CSV", sample_df.to_csv(index=False), "sample_sensor.csv")

# ------------------- WATER SAVING CHALLENGE TAB -------------------
def challenge_page():
    st.title("🏆 Water Saving Challenge")
    st.markdown("Tick off as you complete each water-saving action. Try to complete all!")
    checklist = st.session_state["challenge_checklist"]
    changed = False
    for task in checklist.keys():
        value = st.checkbox(task, value=checklist[task], key=f"challenge_{task}")
        if value != checklist[task]:
            changed = True
        checklist[task] = value
    if changed:
        st.success("Progress updated!")
    completed = sum(checklist.values())
    st.progress(completed / len(checklist), text=f"{completed} of {len(checklist)} tips completed")
    if completed == len(checklist):
        st.balloons()
        st.success("Congratulations! You completed the Water Saving Challenge.")

# ------------------- HELP TAB -------------------
def help_page():
    st.title("❓ Help & About")
    st.markdown(f"""
    ## Welcome to {APP_NAME}!
    Built for Hackathon by Team **{TEAM_NAME}**.

    ### What does WaterSense do?
    - **Track water usage** with sensors in any room.
    - **Detect leaks and wastage** with smart analytics.
    - **Earn badges** for water saving and leak fixing!
    - **Compete and share** with your friends.
    - **Export reports** for your home or project.

    ### Quick Start
    1. Go to **Sensors** tab and add at least one sensor.
    2. Visit **Dashboard** for instant analytics.
    3. Try out all tabs for badges, notifications, and more!

    ### Water Facts
    """)
    for fact in WATER_FACTS:
        st.info(f"💡 {fact}")

    st.markdown("""
    ### Credits
    Built for Hackathon by Team Pseudocoders.  
    [Contact us](mailto:team.pseudocoders@example.com)

    ### Team Members
    """)
    for member in TEAM_MEMBERS:
        st.write(f"👤 {member['name']}")

    st.markdown("""
    ### FAQ
    **Q:** How do I add a sensor?  
    **A:** Go to Sensors, fill out the form, and click Add Sensor.

    **Q:** Can I upload real data?  
    **A:** Yes, upload CSV files in Sensors or Data Management tabs.

    **Q:** How do I earn badges?  
    **A:** Save water, add sensors, and fix leaks!
    """)

# ------------------- HOME / LANDING TAB -------------------
def home_page():
    st.title(f"{APP_NAME} 🚰")
    st.markdown(f"""
    <div style="text-align: center;">
        <img src="https://cdn.pixabay.com/photo/2016/04/01/09/24/water-1296123_960_720.png" width="180"/>
        <h2>Welcome to {APP_NAME}!</h2>
        <h4>Smart Water Management for Everyone</h4>
        <p>
        <span style="font-size:1.2em;">Track, analyze, save, and gamify your water usage.<br>
        Built with 💙 by <b>{TEAM_NAME}</b> for Hackathon.
        </span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    ### What can you do here?
    - **Add sensors** for different rooms
    - **Monitor water usage** trends
    - **Detect leaks & wastage**
    - **Earn and show off badges**
    - **Export reports, join community challenges**
    """)
    st.success("👉 Use the sidebar to get started! Begin by adding a sensor.")
    st.info(f"Fun Fact: {random.choice(WATER_FACTS)}")
    st.divider()
    st.subheader("Meet Team Pseudocoders")
    cols = st.columns(len(TEAM_MEMBERS))
    for i, member in enumerate(TEAM_MEMBERS):
        cols[i].markdown(f"**{member['name']}**", unsafe_allow_html=True)

# ------------------- GAME TAB -------------------
def game_page():
    st.title("🎮 Catch the Water Drops!")
    st.markdown("""
    <div style="text-align:center;">
      <img src="https://cdn.pixabay.com/photo/2016/04/01/09/24/water-1296123_960_720.png" width="60"/>
    </div>
    """, unsafe_allow_html=True)
    st.write("Move your bucket to catch the falling drops. If you waste more than **10 drops**, you lose. Catch **20 drops** to win!")

    # Show current status and feedback
    st.write(f"🌊 **Caught:** {st.session_state['game_score']}    ❌ **Missed:** {st.session_state['game_missed']}/10")
    if st.session_state["game_feedback"]:
        st.info(st.session_state["game_feedback"])

    # Draw game board
    cols = st.columns(3)
    for i, pos in enumerate(["left", "middle", "right"]):
        drop_here = (st.session_state["game_drop_col"] == pos)
        bucket_here = (st.session_state["game_bucket"] == pos)
        if drop_here and bucket_here:
            cols[i].markdown("💧<br>🪣", unsafe_allow_html=True)
        elif drop_here:
            cols[i].markdown("💧", unsafe_allow_html=True)
        elif bucket_here:
            cols[i].markdown("🪣", unsafe_allow_html=True)
        else:
            cols[i].markdown("&nbsp;", unsafe_allow_html=True)

    st.write("Move your bucket:")
    bucket_pos = st.radio(
        "Bucket Position", ["left", "middle", "right"],
        index=["left", "middle", "right"].index(st.session_state["game_bucket"]), horizontal=True
    )

    # Change bucket position triggers a turn
    if st.session_state["game_playing"]:
        if bucket_pos != st.session_state["game_bucket"] or st.session_state["game_feedback"]:
            # New move, play a turn
            st.session_state["game_bucket"] = bucket_pos
            if st.session_state["game_bucket"] == st.session_state["game_drop_col"]:
                st.session_state["game_score"] += 1
                st.session_state["game_feedback"] = "Caught the drop! 💧"
            else:
                st.session_state["game_missed"] += 1
                st.session_state["game_feedback"] = "Missed! The drop was wasted 💦"
            st.session_state["game_drop_col"] = np.random.choice(["left", "middle", "right"])
    else:
        st.session_state["game_feedback"] = ""

    # Win/lose logic
    if st.session_state["game_score"] >= 20:
        st.balloons()
        st.success("🏆 You win! Water saved!")
        st.session_state["game_playing"] = False
        st.session_state["game_score_history"].append(st.session_state["game_score"])
        st.session_state["game_feedback"] = ""
    elif st.session_state["game_missed"] > 10:
        st.error("Game over! Too much water wasted. Try again.")
        st.session_state["game_playing"] = False
        st.session_state["game_score_history"].append(st.session_state["game_score"])
        st.session_state["game_feedback"] = ""

    # Restart option always available if game ended
    if not st.session_state["game_playing"]:
        if st.button("Restart"):
            st.session_state["game_score"] = 0
            st.session_state["game_missed"] = 0
            st.session_state["game_bucket"] = "middle"
            st.session_state["game_drop_col"] = np.random.choice(["left", "middle", "right"])
            st.session_state["game_playing"] = True
            st.session_state["game_feedback"] = ""

    if st.session_state["game_score_history"]:
        st.write("### Your Game History")
        st.bar_chart(pd.Series(st.session_state["game_score_history"], name="Score"))
        st.write(f"Total games played: {len(st.session_state['game_score_history'])}")

    st.write("💧 Water Drop Fun Fact:")
    st.info(random.choice(WATER_FACTS))

# ------------------- SIDEBAR & MAIN ROUTER -------------------
st.set_page_config(page_title=APP_NAME, layout="wide", initial_sidebar_state="expanded")
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2016/04/01/09/24/water-1296123_960_720.png", width=80)
    st.title(APP_NAME)
    st.caption(f"by Team {TEAM_NAME}")
    choices = [
        "🏠 Home", "📊 Dashboard", "🛠️ Sensors", "📈 Analytics", "🏅 Gamification",
        "🔔 Notifications", "🌐 Community", "⚙️ Settings", "🗂️ Data", "🏆 Water Saving Challenge", "🎮 Water Drop Game", "❓ Help"
    ]
    page = st.radio("Navigate", choices)
    st.markdown("---")
    st.caption("Hackathon Project | Team Pseudocoders")

if page == "🏠 Home":
    home_page()
elif page == "📊 Dashboard":
    dashboard_page()
elif page == "🛠️ Sensors":
    sensors_page()
elif page == "📈 Analytics":
    analytics_page()
elif page == "🏅 Gamification":
    gamification_page()
elif page == "🔔 Notifications":
    notifications_page()
elif page == "🌐 Community":
    community_page()
elif page == "⚙️ Settings":
    settings_page()
elif page == "🗂️ Data":
    data_page()
elif page == "🏆 Water Saving Challenge":
    challenge_page()
elif page == "🎮 Water Drop Game":
    game_page()
elif page == "❓ Help":
    help_page()