import streamlit as st
import json
import matplotlib.pyplot as plt
import gpxpy
import base64


# Function to create or edit trail description JSON
def create_or_edit_trail_description():
    """
    Creates a user interface for creating and editing trail description JSON files.

    This function allows uploading existing English and Hebrew JSON files, modifying their content,
    adding or removing media items at any position, and downloading the updated JSON files.
    """
    st.header("Trail Description JSON Creation/Editing")

    # Use session state to store media list
    if 'media_list' not in st.session_state:
        st.session_state.media_list = []

    # Upload existing JSON files
    uploaded_file_en = st.file_uploader("Upload English JSON file", type=["json"], key="en")
    uploaded_file_he = st.file_uploader("Upload Hebrew JSON file", type=["json"], key="he")

    # Initialize variables
    trail_id = ""
    trail_name_en = ""
    trail_description_en = ""
    trail_name_he = ""
    trail_description_he = ""
    media_dict = {}

    # Load English JSON
    if uploaded_file_en is not None:
        try:
            trail_data_en = json.load(uploaded_file_en)
            trail_id = trail_data_en.get("trailId", "")
            trail_name_en = trail_data_en.get("name", "")
            trail_description_en = trail_data_en.get("description", "")
            for media in trail_data_en.get("media", []):
                media_id = media.get("id", "")
                if media_id not in media_dict:
                    media_dict[media_id] = {}
                media_dict[media_id].update({
                    "id": media_id,
                    "type": media.get("type", ""),
                    "url": media.get("url", ""),
                    "description_en": media.get("description", "")
                })
        except json.JSONDecodeError:
            st.error("Invalid English JSON file.")
            return

    # Load Hebrew JSON
    if uploaded_file_he is not None:
        try:
            trail_data_he = json.load(uploaded_file_he)
            trail_id = trail_data_he.get("trailId", trail_id)
            trail_name_he = trail_data_he.get("name", "")
            trail_description_he = trail_data_he.get("description", "")
            for media in trail_data_he.get("media", []):
                media_id = media.get("id", "")
                if media_id not in media_dict:
                    media_dict[media_id] = {}
                media_dict[media_id].update({
                    "id": media_id,
                    "type": media.get("type", ""),
                    "url": media.get("url", ""),
                    "description_he": media.get("description", "")
                })
        except json.JSONDecodeError:
            st.error("Invalid Hebrew JSON file.")
            return

    if not st.session_state.media_list and media_dict:
        st.session_state.media_list = list(media_dict.values())

    # Trail fields
    trail_id = st.text_input("Trail ID", value=trail_id)
    st.subheader("English Version")
    trail_name_en = st.text_input("Trail Name (English)", value=trail_name_en)
    trail_description_en = st.text_area("Trail Description (English)", value=trail_description_en)

    st.subheader("Hebrew Version")
    trail_name_he = st.text_input("Trail Name (Hebrew)", value=trail_name_he)
    trail_description_he = st.text_area("Trail Description (Hebrew)", value=trail_description_he)

    # --- Container for the entire Media Items section (less dominant frame) ---
    with st.container():
        st.markdown(
            """
            <div style="background-color: #f8f8f8; border: 1px dashed #cccccc; padding: 20px; border-radius: 8px; margin-top: 25px;">
            """,
            unsafe_allow_html=True
        )

        st.subheader("Media Items")

        if st.button("➕ Add Media Item at the Top"):
            st.session_state.media_list.insert(0, {})
            st.rerun()

        # Define a list of colors for the individual media item frames (distinct and vibrant)
        frame_colors = [
            "#FFDCDC",  # Light Red
            "#DCF7FF",  # Light Blue
            "#DCFFDC",  # Light Green
            "#FFFBDC",  # Light Yellow
            "#FFEDDC",  # Light Orange
            "#E6E6FA",  # Lavender
            "#D4EDDA"   # Mint Green
        ]
        border_colors = [
            "#FF6347",  # Tomato
            "#00BFFF",  # Deep Sky Blue
            "#32CD32",  # Lime Green
            "#FFD700",  # Gold
            "#FF8C00",  # Dark Orange
            "#9370DB",  # Medium Purple
            "#20B2AA"   # Light Sea Green
        ]


        # Media fields
        for i, media_item in enumerate(st.session_state.media_list):
            with st.container():
                # Cycle through the colors for each media item's frame
                bg_color = frame_colors[i % len(frame_colors)]
                b_color = border_colors[i % len(border_colors)] # Use a distinct border color
                st.markdown(
                    f"""
                    <div style="background-color: {bg_color}; border: 3px solid {b_color}; padding: 18px; border-radius: 10px; margin-bottom: 12px; margin-top: 12px;">
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(f"#### 🖼️ Media Item {i + 1}")

                media_item["id"] = st.text_input(f"Media ID", value=media_item.get("id", ""), key=f"id_{i}")
                media_item["type"] = st.selectbox(f"Media Type", ["image", "video"],
                                                  index=["image", "video"].index(media_item.get("type", "image")),
                                                  key=f"type_{i}")
                media_item["url"] = st.text_input(f"Media URL", value=media_item.get("url", ""), key=f"url_{i}")

                if media_item["type"] == "image" and media_item["url"]:
                    st.image(media_item["url"], caption=f"Media {i + 1}", use_container_width=True)
                elif media_item["type"] == "video" and media_item["url"]:
                    st.video(media_item["url"])

                media_item["description_en"] = st.text_area(f"Media Description (English)",
                                                            value=media_item.get("description_en", ""),
                                                            key=f"desc_en_{i}")
                media_item["description_he"] = st.text_area(f"Media Description (Hebrew)",
                                                            value=media_item.get("description_he", ""),
                                                            key=f"desc_he_{i}")

                if st.button(f"Remove Media Item {i + 1}", key=f"remove_{i}"):
                    st.session_state.media_list.pop(i)
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

            if st.button(f"➕ Add Media Item Below Item {i + 1}", key=f"add_after_{i}"):
                st.session_state.media_list.insert(i + 1, {})
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True) # Closing the outer div for the media section

    # Preview and download
    if st.button("Preview and Download JSONs"):
        # English JSON
        trail_data_en = {
            "trailId": trail_id,
            "name": trail_name_en,
            "description": trail_description_en,
            "media": [
                {
                    "id": media.get("id"),
                    "type": media.get("type"),
                    "url": media.get("url"),
                    "description": media.get("description_en")
                } for media in st.session_state.media_list
            ]
        }
        st.subheader("English JSON Preview")
        st.json(trail_data_en)
        json_data_en = json.dumps(trail_data_en, ensure_ascii=False, indent=4)
        b64_en = base64.b64encode(json_data_en.encode()).decode()
        href_en = f'<a href="data:file/json;base64,{b64_en}" download="{trail_id}_en.json">Download English JSON File</a>'
        st.markdown(href_en, unsafe_allow_html=True)

        # Hebrew JSON
        trail_data_he = {
            "trailId": trail_id,
            "name": trail_name_he,
            "description": trail_description_he,
            "media": [
                {
                    "id": media.get("id"),
                    "type": media.get("type"),
                    "url": media.get("url"),
                    "description": media.get("description_he")
                } for media in st.session_state.media_list
            ]
        }
        st.subheader("Hebrew JSON Preview")
        st.json(trail_data_he)
        json_data_he = json.dumps(trail_data_he, ensure_ascii=False, indent=4)
        b64_he = base64.b64encode(json_data_he.encode()).decode()
        href_he = f'<a href="data:file/json;base64,{b64_he}" download="{trail_id}_he.json">Download Hebrew JSON File</a>'
        st.markdown(href_he, unsafe_allow_html=True)


# GPX graph
def display_gpx_graph():
    """
    Displays a graph of a GPX file.

    This function allows uploading a GPX file and displays a plot of the track.
    """
    st.header("GPX Graph")
    uploaded_file = st.file_uploader("Upload GPX file", type=["gpx"])
    if uploaded_file is not None:
        try:
            gpx = gpxpy.parse(uploaded_file)
            latitudes, longitudes = [], []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        latitudes.append(point.latitude)
                        longitudes.append(point.longitude)

            if not latitudes or not longitudes:
                st.warning("No track points found in the GPX file.")
                return

            fig, ax = plt.subplots()
            ax.plot(longitudes, latitudes, marker='o', linestyle='-')
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.set_title("GPX Track")
            ax.grid(True)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"An error occurred while parsing the GPX file: {e}")


# App layout
st.title("Admin Task Management App")
tab1, tab2 = st.tabs(["Trail Description JSON", "GPX Graph"])
with tab1:
    create_or_edit_trail_description()
with tab2:
    display_gpx_graph()
