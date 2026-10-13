
import streamlit as st

from modules import database, gemini_service, nlp_processor, safety


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. SESSION STATE INITIALIZATION
# ============================================================

def initialize_session_state():
    """Initialize Streamlit session variables."""

    defaults = {
        "result": None,
        "db_warning": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# 3. SIDEBAR
# ============================================================

def render_sidebar() -> str:
    """Render navigation and application information."""

    with st.sidebar:
        st.title("🩺 Healthcare Assistant")

        st.caption("AI-powered general health information")

        page = st.radio(
            "Navigation",
            options=["Ask a question", "History"],
            key="navigation_page",
        )

        st.divider()

        st.subheader("About")

        st.write(
            "This application uses Python, Streamlit, "
            "the Gemini API, MySQL, and basic NLP to provide "
            "general health information based on user input."
        )

        st.subheader("Privacy")

        st.info(
            "Avoid entering names, contact details, addresses, "
            "or other identifying information. Interactions may "
            "be stored in a local MySQL database."
        )

        st.subheader("Medical disclaimer")

        st.warning(safety.DISCLAIMER)

        st.caption(
            "Educational demonstration only. "
            "Not a substitute for professional medical care."
        )

    return page


# ============================================================
# 4. EMERGENCY WARNING
# ============================================================

def render_emergency_banner():
    """Display a persistent emergency notice."""

    st.error(
        "🚨 **Emergency notice**\n\n"
        + safety.EMERGENCY_WARNING
    )


# ============================================================
# 5. INPUT VALIDATION AND AI WORKFLOW
# ============================================================

def handle_submission(user_text: str) -> dict:
    """
    Process a symptom description.

    Workflow:
    1. Validate and preprocess input.
    2. Check the original text for emergency indicators.
    3. Return emergency guidance when an indicator matches.
    4. Otherwise request general information from Gemini.
    5. Return a structured result.
    """

    # Reject empty or invalid input through the NLP module.
    try:
        processed = nlp_processor.preprocess(user_text)

    except Exception:
        return {
            "status": "processing_error",
            "message": "Input processing failed. Please try again.",
        }

    if not processed["is_valid"]:
        return {
            "status": "invalid",
            "message": processed["message"],
        }

    cleaned_text = processed["cleaned_text"]
    keywords = processed["keywords"]

    # Check the original and normalized input.
    # The safety module should normalize text consistently.
    try:
        original_matches = safety.check_emergency(user_text)
        cleaned_matches = safety.check_emergency(cleaned_text)

        matches = list(dict.fromkeys(
            list(original_matches or []) +
            list(cleaned_matches or [])
        ))

    except Exception:
        # Fail safely instead of calling Gemini when the
        # emergency-checking component is unavailable.
        return {
            "status": "safety_error",
            "message": (
                "The safety check is temporarily unavailable. "
                "Please try again later. If symptoms are severe "
                "or life-threatening, seek emergency medical care."
            ),
        }

    # Emergency guidance takes priority over AI generation.
    if matches:
        emergency_text = safety.EMERGENCY_GUIDANCE

        if safety.is_self_harm(matches):
            emergency_text += (
                "\n\n" + safety.SELF_HARM_SUPPORT
            )

        return {
            "status": "emergency",
            "text": emergency_text,
            "matches": matches,
            "cleaned": cleaned_text,
            "keywords": keywords,
        }

    # Generate general health information only when
    # the safety check completes without a matching indicator.
    try:
        with st.spinner(
            "Generating general health information..."
        ):
            response = gemini_service.generate_guidance(
                cleaned_text,
                keywords,
            )

        if not isinstance(response, str) or not response.strip():
            return {
                "status": "ai_error",
                "message": (
                    "The AI returned an empty response. "
                    "Please try again."
                ),
                "cleaned": cleaned_text,
            }

        return {
            "status": "ok",
            "text": response.strip(),
            "cleaned": cleaned_text,
            "keywords": keywords,
        }

    except gemini_service.GeminiServiceError:
        return {
            "status": "ai_error",
            "message": (
                "The AI service could not generate a response. "
                "Check your API configuration or try again later."
            ),
            "cleaned": cleaned_text,
        }

    except Exception:
        return {
            "status": "ai_error",
            "message": (
                "An unexpected error occurred while generating "
                "the response. Please try again later."
            ),
            "cleaned": cleaned_text,
        }


# ============================================================
# 6. DATABASE OPERATIONS
# ============================================================

def save_result(result: dict) -> str:
    """
    Save an interaction to MySQL.

    Returns an empty string on success, or a message
    if the database operation fails.
    """

    try:
        database.save_interaction(
            result["cleaned"],
            result["text"],
        )

        return ""

    except database.DatabaseError:
        return (
            "The database could not save this interaction. "
            "Check the database connection and table schema."
        )

    except Exception:
        return (
            "An unexpected database error occurred. "
            "The displayed response is still available."
        )


# ============================================================
# 7. DISPLAY THE GENERATED RESULT
# ============================================================

def render_result():
    """Display the latest result stored in session state."""

    result = st.session_state.get("result")

    if not result:
        return

    status = result.get("status")

    st.divider()

    if status == "invalid":
        st.warning(result["message"])

    elif status == "processing_error":
        st.error(result["message"])

    elif status == "safety_error":
        st.error(result["message"])

    elif status == "ai_error":
        st.error(result["message"])

    elif status == "emergency":
        st.error("🚨 **Urgent: seek appropriate medical care**")

        st.markdown(result["text"])

        st.caption(
            "Automated safety indicators may miss emergencies "
            "or flag situations incorrectly. Do not rely on "
            "this application to determine whether an emergency "
            "is present."
        )

    elif status == "ok":
        with st.container(border=True):
            st.subheader("General health information")

            keywords = result.get("keywords", [])

            if keywords:
                st.caption(
                    "Terms identified during text processing: "
                    + ", ".join(keywords)
                )

            st.markdown(result["text"])

        st.success("Response generated successfully.")

        st.caption(safety.DISCLAIMER)

    # Display database status only for saved-response statuses.
    if status in ("ok", "emergency"):
        warning = st.session_state.get("db_warning", "")

        if warning:
            st.warning(
                "The response is displayed, but saving failed. "
                + warning
            )
        else:
            st.info("Interaction saved to the local database.")


# ============================================================
# 8. ASK A QUESTION PAGE
# ============================================================

def render_ask_page():
    """Render the symptom input form and response."""

    st.title("Ask about your symptoms")

    st.write(
        "Describe how you feel in a few sentences to receive "
        "general health information. This application does "
        "**not** diagnose medical conditions."
    )

    render_emergency_banner()

    with st.form("symptom_form", clear_on_submit=False):

        user_text = st.text_area(
            "Describe your symptoms",
            height=150,
            max_chars=nlp_processor.MAX_LENGTH,
            placeholder=(
                "Example: I have a mild headache and "
                "a runny nose since yesterday."
            ),
            help=(
                "Do not include names, contact information, "
                "or other identifying details."
            ),
        )

        submitted = st.form_submit_button(
            "Get general health guidance",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        # Clear the previous result before processing new input.
        st.session_state["result"] = None
        st.session_state["db_warning"] = ""

        result = handle_submission(user_text)

        st.session_state["result"] = result

        # Save only successful AI responses and emergency
        # guidance generated by the local safety module.
        if result["status"] in ("ok", "emergency"):
            st.session_state["db_warning"] = save_result(result)

    render_result()


# ============================================================
# 9. HISTORY PAGE
# ============================================================

def render_history_page():
    """Retrieve and display recent interactions."""

    st.title("Interaction history")

    st.info(
        "This is a local academic demonstration. "
        "It is not intended to store real patient records."
    )

    if st.button("🔄 Refresh history"):
        # Streamlit reruns the script after a button click.
        # The history query below runs again.
        pass

    try:
        rows = database.get_history(limit=20)

    except database.DatabaseError:
        st.error(
            "History is unavailable. Verify the MySQL service, "
            "database configuration, and table structure."
        )
        return

    except Exception:
        st.error(
            "An unexpected error occurred while loading history."
        )
        return

    if not rows:
        st.write("No interactions saved yet.")
        return

    st.caption(
        f"Showing up to {len(rows)} recent interactions."
    )

    for row in rows:

        created_at = row.get("created_at")

        if created_at:
            if hasattr(created_at, "strftime"):
                timestamp = created_at.strftime(
                    "%d %b %Y, %H:%M"
                )
            else:
                timestamp = str(created_at)
        else:
            timestamp = "Date unavailable"

        user_input = row.get("user_input") or ""
        ai_response = row.get("ai_response") or ""

        # Avoid putting the entire symptom description
        # into the expander heading.
        heading = (
            f"{timestamp} — {user_input[:50]}"
        )

        with st.expander(heading):

            st.markdown("**Symptom description**")
            st.write(user_input)

            st.markdown("**Generated response**")
            st.markdown(ai_response)


# ============================================================
# 10. APPLICATION ENTRY POINT
# ============================================================

def main():
    """Run the application."""

    initialize_session_state()

    page = render_sidebar()

    if page == "History":
        render_history_page()
    else:
        render_ask_page()


if __name__ == "__main__":
    main()
