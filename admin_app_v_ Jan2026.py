import streamlit as st
import json
import gpxpy
from typing import List, Dict, Any

# Constants for media item styling
FRAME_COLORS = ["#FFDCDC", "#DCF7FF", "#DCFFDC", "#FFFBDC", "#FFEDDC", "#E6E6FA", "#D4EDDA"]
BORDER_COLORS = ["#FF6347", "#00BFFF", "#32CD32", "#FFD700", "#FF8C00", "#9370DB", "#20B2AA"]


def build_trail_json(trail_id: str, name: str, description: str, 
                     media_list: List[Dict], lang_suffix: str) -> Dict[str, Any]:
    """Build trail JSON for a specific language."""
    return {
        "trailId": trail_id,
        "name": name,
        "description": description,
        "media": [
            {
                "id": m.get("id"),
                "type": m.get("type"),
                "url": m.get("url"),
                "description": m.get(f"description_{lang_suffix}")
            } for m in media_list
        ]
    }


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

        # Media fields
        for i, media_item in enumerate(st.session_state.media_list):
            with st.container():
                # Cycle through the colors for each media item's frame
                bg_color = FRAME_COLORS[i % len(FRAME_COLORS)]
                b_color = BORDER_COLORS[i % len(BORDER_COLORS)]
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
        # Validation
        if not trail_id.strip():
            st.error("⚠️ Trail ID is required!")
            return
        
        if not st.session_state.media_list:
            st.warning("⚠️ No media items added.")

        # Build JSON using helper function
        trail_data_en = build_trail_json(trail_id, trail_name_en, trail_description_en,
                                         st.session_state.media_list, "en")
        trail_data_he = build_trail_json(trail_id, trail_name_he, trail_description_he,
                                         st.session_state.media_list, "he")

        # English JSON Preview and Download
        st.subheader("English JSON Preview")
        st.json(trail_data_en)
        st.download_button(
            label="📥 Download English JSON",
            data=json.dumps(trail_data_en, ensure_ascii=False, indent=4),
            file_name=f"{trail_id}_en.json",
            mime="application/json",
            key="download_en"
        )

        # Hebrew JSON Preview and Download
        st.subheader("Hebrew JSON Preview")
        st.json(trail_data_he)
        st.download_button(
            label="📥 Download Hebrew JSON",
            data=json.dumps(trail_data_he, ensure_ascii=False, indent=4),
            file_name=f"{trail_id}_he.json",
            mime="application/json",
            key="download_he"
        )


# GPX graph
def display_gpx_graph():
    """
    Displays a graph of a GPX file with track map and elevation profile.

    This function allows uploading a GPX file and displays:
    - Track map (latitude vs longitude)
    - Elevation profile (elevation vs distance)
    - Key statistics (distance, min/max elevation)
    """
    import matplotlib.pyplot as plt  # Lazy import for faster app startup
    
    st.header("GPX Graph")
    uploaded_file = st.file_uploader("Upload GPX file", type=["gpx"])
    
    if uploaded_file is not None:
        try:
            gpx = gpxpy.parse(uploaded_file)
            data = {"lat": [], "lon": [], "ele": [], "dist": []}
            total_dist = 0
            prev_point = None
            
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        data["lat"].append(point.latitude)
                        data["lon"].append(point.longitude)
                        data["ele"].append(point.elevation if point.elevation else 0)
                        if prev_point:
                            total_dist += point.distance_2d(prev_point)
                        data["dist"].append(total_dist / 1000)  # Convert to km
                        prev_point = point

            if not data["lat"]:
                st.warning("No track points found in the GPX file.")
                return

            # Create two plots side by side
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Track map
            ax1.plot(data["lon"], data["lat"], 'b-', linewidth=2)
            ax1.plot(data["lon"][0], data["lat"][0], 'go', markersize=10, label='Start')
            ax1.plot(data["lon"][-1], data["lat"][-1], 'ro', markersize=10, label='End')
            ax1.set_title("Track Map")
            ax1.set_xlabel("Longitude")
            ax1.set_ylabel("Latitude")
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            # Elevation profile
            ax2.fill_between(data["dist"], data["ele"], alpha=0.3, color='green')
            ax2.plot(data["dist"], data["ele"], 'g-', linewidth=2)
            ax2.set_title("Elevation Profile")
            ax2.set_xlabel("Distance (km)")
            ax2.set_ylabel("Elevation (m)")
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Display statistics
            col1, col2, col3 = st.columns(3)
            col1.metric("📏 Total Distance", f"{total_dist/1000:.2f} km")
            col2.metric("⬇️ Min Elevation", f"{min(data['ele']):.0f} m")
            col3.metric("⬆️ Max Elevation", f"{max(data['ele']):.0f} m")
            
        except Exception as e:
            st.error(f"An error occurred while parsing the GPX file: {e}")


# App layout
st.title("Admin Task Management App")
tab1, tab2 = st.tabs(["Trail Description JSON", "GPX Graph"])
with tab1:
    create_or_edit_trail_description()
with tab2:
    display_gpx_graph()