import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.title("🎮 Steam Games Explorer")

# This is Connection 3 (Streamlit -> FastAPI): protocol is HTTP, no auth needed (both run locally)

tab1, tab2, tab3 = st.tabs(["Browse games", "Search by name", "Details by ID"])

def render_game_list(games):
    """Shared helper to render a list of games — avoids repeating this code in every tab."""
    if not games:
        st.info("No games matched.")
        return
    for game in games:
        col1, col2 = st.columns([1, 2])
        with col1:
            if game.get("header_image"):
                st.image(game["header_image"])
        with col2:
            st.subheader(game["name"])
            price_text = "Free" if game["is_free"] else f"${game['price']}"
            st.write(f"Price: {price_text} | Metacritic: {game.get('metacritic_score', 'N/A')}")
        st.divider()

with tab1:
    st.subheader("Browse game list")

    filter_option = st.selectbox(
        "Filter by",
        ["All", "Free", "Windows", "Mac", "Linux"]
    )

    limit = st.slider("Number of games to show", min_value=5, max_value=100, value=20)
    offset = st.number_input("How many games to skip (offset)", min_value=0, value=0, step=20)

    # Map the UI selection to the matching FastAPI endpoint
    endpoint_map = {
        "All": "/games",
        "Free": "/games/free",
        "Windows": "/games/platform/windows",
        "Mac": "/games/platform/mac",
        "Linux": "/games/platform/linux",
    }

    if st.button("Load list"):
        endpoint = endpoint_map[filter_option]
        response = requests.get(f"{API_URL}{endpoint}", params={"limit": limit, "offset": offset})

        if response.status_code == 200:
            render_game_list(response.json())
        else:
            st.error(f"Failed to load data: {response.status_code}")

with tab2:
    st.subheader("Search games by name")

    search_name = st.text_input("Enter game name")

    if st.button("Search") and search_name:
        response = requests.get(f"{API_URL}/games/search", params={"name": search_name})

        if response.status_code == 200:
            render_game_list(response.json())
        elif response.status_code == 404:
            st.warning("No matching games found.")
        else:
            st.error(f"Search failed: {response.status_code}")

with tab3:
    st.subheader("View details by App ID")

    appid = st.number_input("Enter App ID", min_value=0, step=1)

    if st.button("View details"):
        response = requests.get(f"{API_URL}/games/{appid}")

        if response.status_code == 200:
            game = response.json()  # giờ đã là dict trực tiếp, không cần unwrap list nữa

            st.subheader(game["name"])
            if game.get("header_image"):
                st.image(game["header_image"])

            price_text = "Free" if game["is_free"] else f"${game['price']}"
            st.write(f"Price: {price_text} | Metacritic: {game.get('metacritic_score', 'N/A')}")

            # Release date + achievements
            st.write(f"Release date: {game.get('release_date') or 'TBA'} | Achievements: {game.get('achievements', 0)}")

            # Supported languages
            if game.get("interface_languages"):
                st.write(f"Interface languages: {game['interface_languages']}")
            if game.get("audio_languages"):
                st.write(f"Audio languages: {game['audio_languages']}")

            # Full description
            with st.expander("Full description"):
                st.write(game.get("detailed_description", "No description available."))

            # Trailer — link only, since it's HLS/DASH streaming format, not a plain mp4
            if game.get("trailer_url"):
                st.markdown(f"🎬 [Watch trailer]({game['trailer_url']})")
            else:
                st.caption("No trailer available for this game.")

        elif response.status_code == 404:
            st.warning("No game found with this ID.")
        else:
            st.error(f"Error: {response.status_code}")