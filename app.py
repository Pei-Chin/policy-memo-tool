import streamlit as st
import google.generativeai as genai
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Policy Memo Architect",
    page_icon="⚖️",
    layout="wide"
)

# --- Sidebar: API Configuration ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.markdown("### 1. Enter Gemini API Key")
    api_key = st.text_input("Paste Google API Key Here", type="password")
    
    st.markdown("""
    ---
    **How to get a free key:**
    1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Log in with your Google account.
    3. Click **Create API Key**.
    4. Copy and paste it above.
    
    *(Note: Your key is not stored. It is only used for this session.)*
    """)
    
    st.info("Workflow based on *Public Policy Writing That Matters* by David Chrisinger.")

# --- Main Interface ---
st.title("🏛️ Policy Memo Architect")
st.markdown("### An Algorithm for Clarity, Concision, and Compelling Argument")
st.markdown("This tool generates a policy memo draft strictly following David Chrisinger's structured workflow, ensuring audience-centered analysis and rigorous verification.")

# Default JSON Example (English)
default_input = [
    {
        "topic": "Affordable housing reform",
        "policymaker_type": "City budget director",
        "audience": "City Budget Director’s Office",
        "purpose": "Persuade adoption of pilot program",
        "writer_role": "Independent analyst",
        "institutional_context": "Urban Development Think Tank"
    }
]

# --- Input Section ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Context Configuration")
    st.markdown("Define your 'Triangle of Persuasion' parameters in JSON format:")
    json_input = st.text_area(
        "JSON Input", 
        value=json.dumps(default_input, indent=2), 
        height=300
    )
    
    generate_btn = st.button("🚀 Generate Policy Memo", type="primary")

# --- Core Logic (The Chrisinger Algorithm) ---
def run_chrisinger_workflow(api_key, user_json):
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Use Gemini 1.5 Pro (Better for logic/reasoning)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # --- The System Prompt (Logic Hard-coding) ---
    system_prompt = f"""
    You are an expert Policy Analyst acting as a writing assistant based strictly on David Chrisinger's "Policy Memo Writing Workflow".
    
    Your goal is to write a high-quality Policy Memo based on the provided JSON context.

    ### CRITICAL RULES (THE ALGORITHM):
    
    1.  **Triangle of Persuasion (Phase 0):** - Analyze the JSON to understand the Audience's values (e.g., if Audience is a Budget Director, prioritize fiscal prudence and efficiency).
        - Adopt the Tone defined by the Purpose (Inform vs. Persuade).
    
    2.  **VERIFICATION RULE (Phase 2 & 8 - MOST IMPORTANT):**
        - **DO NOT HALLUCINATE DATA.** - AI cannot verify facts. If a strong argument requires a specific statistic, date, law, or budget number, YOU MUST INSERT A PLACEHOLDER.
        - Format placeholders like this: `**[VERIFY: specific budget for 2024 housing pilot]**` or `**[DATA NEEDED: exact percentage of homelessness increase]**`.
        - Do not invent numbers.
    
    3.  **Structure Selection (Phase 4):**
        - Choose the best structure for the audience:
          - *Recommendation-First*: For busy executives/high stakes.
          - *Criteria-Driven*: When comparing options.
          - *Context-Problem-Solution*: For non-technical audiences.
    
    4.  **Tone & Style (Phase 5 & 6):**
        - **Trauma-Informed:** Ensure language is respectful and avoids paternalism.
        - **Concision:** Active voice. Subject and verb close together. Avoid filler phrases like "It is important to note that..."
    
    ### TASK:
    
    Based on the following JSON Input:
    {user_json}
    
    **Generate the response in the following Markdown format:**
    
    ## 📋 Strategy Note
    *(Briefly explain which Audience Values you prioritized and which Memo Structure template you selected and why.)*
    
    ---
    
    ## 📝 Policy Memo Draft
    *(The actual memo content)*
    
    ---
    
    ## 🔍 Verification & Bias Checklist
    *(List all the [VERIFY] tags you created. Also, provide a brief 'Tone Audit' confirming you checked for bias.)*
    """

    # Call API
    response = model.generate_content(system_prompt)
    return response.text

# --- Output Section ---
with col2:
    st.subheader("2. Generated Draft")
    
    if generate_btn:
        if not api_key:
            st.error("⚠️ Error: Please enter your Google API Key in the sidebar first.")
        else:
            with st.spinner("Running Chrisinger's Algorithm... (Analyzing Audience -> Drafting -> Auditing)"):
                try:
                    # Validate JSON
                    parsed_json = json.loads(json_input)
                    
                    # Run Generation
                    result_text = run_chrisinger_workflow(api_key, json_input)
                    
                    st.markdown(result_text)
                    st.success("Draft generation complete. Please review the Verification Checklist below.")
                    
                except json.JSONDecodeError:
                    st.error("❌ Error: Invalid JSON format. Please check your input syntax.")
                except Exception as e:
                    st.error(f"❌ System Error: {e}")
                    st.markdown("Possible causes: Invalid API Key or API limit reached.")
