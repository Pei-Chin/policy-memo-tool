import streamlit as st
import google.generativeai as genai
import time

# --- 1. Page Configuration & UI Styling ---
st.set_page_config(
    page_title="Policy Memo Architect Pro",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .step-header {
        color: #1E88E5;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid #eee;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
    .verify-tag {
        background-color: #ffebee;
        color: #c62828;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. State Management (The Brain) ---
# This keeps track of the user's progress and the data generated at each step.
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

# Initialize storage for each phase if not exists
phases = [
    'p0_triangle', 'p1_framing', 'p2_evidence', 
    'p3_recommendation', 'p4_exec_summary', 
    'p5_draft', 'p6_audit', 'p7_final'
]
for phase in phases:
    if phase not in st.session_state:
        st.session_state[phase] = ""

# --- 3. Sidebar: Configuration & Navigation ---
with st.sidebar:
    st.title("🏛️ Memo Architect")
    st.markdown("**Based on David Chrisinger's Algorithm**")
    
    api_key = st.text_input("🔑 Google Gemini API Key", type="password")
    
    st.markdown("---")
    st.markdown("### 📍 Progress Tracker")
    
    steps = [
        "0. Triangle of Persuasion",
        "1. Frame the Problem",
        "2. Evidence Base",
        "3. Recommendation",
        "4. Executive Summary",
        "5. Assemble Draft",
        "6. Tone & Bias Check",
        "7. Final Polish & Verify"
    ]
    
    # Progress Bar
    progress_value = (st.session_state.current_step) / (len(steps) - 1)
    st.progress(progress_value)
    
    # Navigation Radio (Allows jumping back, but limits jumping forward blindly)
    selected_step = st.radio(
        "Current Phase:", 
        range(len(steps)), 
        format_func=lambda x: steps[x],
        index=st.session_state.current_step
    )
    
    # Sync radio selection with state
    if selected_step != st.session_state.current_step:
        st.session_state.current_step = selected_step
        st.rerun()

    st.markdown("---")
    if st.button("🗑️ Reset All Progress"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# --- 4. Helper Function: Call AI ---
def generate_ai_content(prompt, system_instruction):
    if not api_key:
        st.error("⚠️ Please enter your API Key in the sidebar.")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # Flash is fast and good for iterative tasks
    
    full_prompt = f"{system_instruction}\n\nUSER REQUEST:\n{prompt}"
    
    with st.spinner("🤖 The Architect is thinking..."):
        try:
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            st.error(f"API Error: {e}")
            return None

# --- 5. Main Content Area (The Steps) ---

# GLOBAL CONTEXT (Variables accessible to all steps if previously filled)
# We assume the user inputs these in Step 0
context_input = st.session_state.get('user_context_input', {})

# === STEP 0: CLARIFY THE TRIANGLE ===
if st.session_state.current_step == 0:
    st.markdown('<div class="step-header">Phase 0: Clarify the Triangle of Persuasion</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Before writing, we must define the three foundations. If these are unclear, the memo collapses.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic", value=context_input.get('topic', 'Affordable housing reform'))
        policymaker = st.text_input("Policymaker Type", value=context_input.get('policymaker', 'City Budget Director'))
    with col2:
        audience = st.text_input("Specific Audience", value=context_input.get('audience', "City Budget Director's Office"))
        purpose = st.selectbox("Purpose", ["Persuade", "Inform", "Evaluate", "Hybrid"], index=0)
    
    writer_role = st.text_input("Your Role", value=context_input.get('role', 'Independent Analyst'))

    # Save inputs to session state
    st.session_state.user_context_input = {
        'topic': topic, 'policymaker': policymaker, 'audience': audience, 
        'purpose': purpose, 'role': writer_role
    }

    if st.button("Generate Strategy Analysis"):
        sys_prompt = """
        You are a Policy Strategy Consultant following Chrisinger's Phase 0.
        Analyze the user's input and output 3 sections:
        1. **Audience Profile:** Their likely values (efficiency, equity, etc.) and constraints.
        2. **Refined Purpose:** How tone and evidence should be shaped based on the audience.
        3. **Credibility Statement:** A draft sentence establishing the writer's legitimacy.
        """
        user_prompt = f"Topic: {topic}, Audience: {audience}, Role: {writer_role}, Purpose: {purpose}"
        result = generate_ai_content(user_prompt, sys_prompt)
        if result:
            st.session_state.p0_triangle = result

    # Display & Edit Result
    if st.session_state.p0_triangle:
        st.subheader("Strategy Output")
        # Editable text area allows user to refine before moving on
        st.session_state.p0_triangle = st.text_area("Review & Edit Strategy:", value=st.session_state.p0_triangle, height=300)
        
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("🔄 Regenerate"):
                st.session_state.p0_triangle = "" # Clear to force regen logic if clicked again
                st.rerun()
        with col_b:
            if st.button("Next Step: Frame Problem ➡️"):
                st.session_state.current_step = 1
                st.rerun()

# === STEP 1: FRAME THE PROBLEM ===
elif st.session_state.current_step == 1:
    st.markdown('<div class="step-header">Phase 1: Frame the Policy Problem</div>', unsafe_allow_html=True)
    
    if not st.session_state.p0_triangle:
        st.warning("⚠️ Please complete Phase 0 first.")
    else:
        st.markdown(f"**Context:** Writing about *{st.session_state.user_context_input['topic']}* for *{st.session_state.user_context_input['audience']}*.")
        
        st.info("We need to define a problem that is analytically rigorous. Not 'solve poverty', but a manageable slice.")

        if st.button("Generate Problem Framing"):
            sys_prompt = """
            You are an expert Policy Analyst (Chrisinger Phase 1).
            Based on the Strategy provided, generate:
            1. **Core Issue Summary (150 words):** Brief the policymaker. Focus on why it matters NOW.
            2. **Scope & Scale:** Define the jurisdiction and specific measurable variables.
            3. **Stakeholder Map:** Who benefits? Who suffers? Who decides?
            
            **CRITICAL RULE:** Do not invent specific statistics. Use [VERIFY: insert 2024 poverty rate] placeholders.
            """
            user_prompt = f"Previous Strategy:\n{st.session_state.p0_triangle}\n\nTask: Frame the problem for {st.session_state.user_context_input['topic']}."
            result = generate_ai_content(user_prompt, sys_prompt)
            if result:
                st.session_state.p1_framing = result

        if st.session_state.p1_framing:
            st.session_state.p1_framing = st.text_area("Refine Problem Framing:", value=st.session_state.p1_framing, height=400)
            
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button("🔄 Regenerate"):
                    st.session_state.p1_framing = ""
                    st.rerun()
            with c2:
                if st.button("Next Step: Evidence ➡️"):
                    st.session_state.current_step = 2
                    st.rerun()

# === STEP 2: BUILD EVIDENCE BASE ===
elif st.session_state.current_step == 2:
    st.markdown('<div class="step-header">Phase 2: Build the Evidence Base</div>', unsafe_allow_html=True)
    st.markdown("We need the Four Elements: **Status, Criteria, Interpretation, Outlook**.")
    
    if st.button("Draft Evidence Structure"):
        sys_prompt = """
        You are a Policy Researcher (Chrisinger Phase 2).
        Draft the 'Analysis' section using the Four Elements:
        1. **Status:** Describe what is happening.
        2. **Criteria:** Define standards for success (cost-effectiveness, equity, etc.) that match the Audience's values.
        3. **Interpretation:** Explain root causes (Structural vs Proximate).
        4. **Outlook:** Forecast Status Quo vs. Reform scenarios.
        
        **VERIFICATION RULE:** YOU MUST NOT HALLUCINATE DATA. 
        If a number is needed, write: `[VERIFY: specific cost of X program]` or `[DATA NEEDED: chart of 5-year trend]`.
        """
        user_prompt = f"Problem Framing:\n{st.session_state.p1_framing}"
        result = generate_ai_content(user_prompt, sys_prompt)
        if result:
            st.session_state.p2_evidence = result

    if st.session_state.p2_evidence:
        st.session_state.p2_evidence = st.text_area("Refine Evidence Base:", value=st.session_state.p2_evidence, height=500)
        
        c1, c2 = st.columns([1, 4])
        with c1: 
             if st.button("🔄 Regenerate"):
                st.session_state.p2_evidence = ""
                st.rerun()
        with c2: 
            if st.button("Next Step: Recommendation ➡️"):
                st.session_state.current_step = 3
                st.rerun()

# === STEP 3: DEVELOP RECOMMENDATION ===
elif st.session_state.current_step == 3:
    st.markdown('<div class="step-header">Phase 3: Develop Recommendation</div>', unsafe_allow_html=True)
    st.markdown("From Analysis to Action. Recommendations must be specific, feasible, and proportionate.")

    if st.button("Develop Solution"):
        sys_prompt = """
        You are a Policy Strategist (Chrisinger Phase 3).
        1. **Identify Leverage Points:** What mechanism (law, funding, pilot) can the user actually use?
        2. **Evaluate Alternatives:** Briefly compare 2 other options and why they were discarded based on the Criteria.
        3. **The Recommendation:** Draft a 3-sentence specific, measurable action.
        """
        user_prompt = f"Problem:\n{st.session_state.p1_framing}\n\nEvidence Analysis:\n{st.session_state.p2_evidence}"
        result = generate_ai_content(user_prompt, sys_prompt)
        if result:
            st.session_state.p3_recommendation = result

    if st.session_state.p3_recommendation:
        st.session_state.p3_recommendation = st.text_area("Refine Recommendation:", value=st.session_state.p3_recommendation, height=400)
        
        c1, c2 = st.columns([1, 4])
        with c1:
             if st.button("🔄 Regenerate"):
                st.session_state.p3_recommendation = ""
                st.rerun()
        with c2:
             if st.button("Next Step: Executive Summary ➡️"):
                st.session_state.current_step = 4
                st.rerun()

# === STEP 4: EXECUTIVE SUMMARY ===
elif st.session_state.current_step == 4:
    st.markdown('<div class="step-header">Phase 4: Draft Executive Summary</div>', unsafe_allow_html=True)
    st.info("The Executive Summary structure depends on the Purpose and Audience.")

    if st.button("Draft Executive Summary"):
        sys_prompt = f"""
        You are an Editor (Chrisinger Phase 4).
        Select the best template from the 7 Chrisinger types based on the Purpose ({st.session_state.user_context_input['purpose']}).
        
        Types:
        1. Recommendation-First (High stakes)
        2. Criteria-Driven (Comparing options)
        3. Context-Problem-Solution (Non-technical)
        4. Evidence-Driven (Technical audience)
        5. Stakeholder-Centered (Political complexity)
        6. Risk-Mitigation (Uncertainty)
        7. Implementation-Focused
        
        **Task:** State which template you chose and why, then write the Summary.
        """
        user_prompt = f"Purpose: {st.session_state.user_context_input['purpose']}\nRecommendation: {st.session_state.p3_recommendation}\nProblem: {st.session_state.p1_framing}"
        result = generate_ai_content(user_prompt, sys_prompt)
        if result:
            st.session_state.p4_exec_summary = result

    if st.session_state.p4_exec_summary:
        st.session_state.p4_exec_summary = st.text_area("Refine Executive Summary:", value=st.session_state.p4_exec_summary, height=300)
        
        c1, c2 = st.columns([1, 4])
        with c1:
             if st.button("🔄 Regenerate"):
                st.session_state.p4_exec_summary = ""
                st.rerun()
        with c2:
             if st.button("Next Step: Assemble Draft ➡️"):
                st.session_state.current_step = 5
                st.rerun()

# === STEP 5: ASSEMBLE DRAFT ===
elif st.session_state.current_step == 5:
    st.markdown('<div class="step-header">Phase 5: Structure the Policy Memo</div>', unsafe_allow_html=True)
    st.markdown("Combining all previous steps into a cohesive document.")

    if st.button("Assemble Full Draft"):
        sys_prompt = """
        You are a Policy Writer (Chrisinger Phase 5).
        Assemble the full memo in Markdown.
        Structure:
        1. Title & Executive Summary
        2. Status (Background)
        3. Analysis (Criteria + Interpretation + Outlook)
        4. Recommendation
        5. Implementation Considerations
        
        **Style Rules:**
        - Deductive paragraphs (Topic sentence first).
        - Active voice.
        - Cut filler words ("It is important to note").
        - Keep the [VERIFY] tags visible.
        """
        user_prompt = f"""
        Exec Summary: {st.session_state.p4_exec_summary}
        Framing: {st.session_state.p1_framing}
        Evidence: {st.session_state.p2_evidence}
        Recommendation: {st.session_state.p3_recommendation}
        """
        result = generate_ai_content(user_prompt, sys_prompt)
        if result:
            st.session_state.p5_draft = result

    if st.session_state.p5_draft:
        st.session_state.p5_draft = st.text_area("Review Full Draft:", value=st.session_state.p5_draft, height=600)
        
        c1, c2 = st.columns([1, 4])
        with c1:
             if st.button("🔄 Regenerate"):
                st.session_state.p5_draft = ""
                st.rerun()
        with c2:
             if st.button("Next Step: Tone Check ➡️"):
                st.session_state.current_step = 6
                st.rerun()

# === STEP 6: TONE & BIAS CHECK ===
elif st.session_state.current_step == 6:
    st.markdown('<div class="step-header">Phase 6: Tone, Bias, and Trauma-Informed Check</div>', unsafe_allow_html=True)
    st.markdown("Ensuring the language is empathetic, factual, and avoids paternalism.")

    if st.button("Run Audit"):
        sys_prompt = """
        You are an Ethics & Tone Auditor (Chrisinger Phase 6).
        Review the draft for:
        1. **Tone:** Is it professional yet empathetic?
        2. **Bias:** Are there assumptions that alienate stakeholders?
        3. **Trauma-Informed:** Do descriptions preserve dignity/agency?
        
        **Output:** - Provide a critique list.
        - Suggest specific re-phrasing for 3 problematic sentences (if any).
        - DO NOT rewrite the whole memo yet. Just the audit.
        """
        user_prompt = f"Draft Memo:\n{st.session_state.p5_draft}"
        result = generate_ai_content(user_prompt, sys_prompt)
        if result:
            st.session_state.p6_audit = result

    if st.session_state.p6_audit:
        st.warning("Audit Results:")
        st.markdown(st.session_state.p6_audit)
        
        st.markdown("---")
        st.markdown("**Action:** Read the audit above. If you want to apply changes, edit the draft below.")
        st.session_state.p5_draft = st.text_area("Edit Draft based on Audit:", value=st.session_state.p5_draft, height=500)
        
        if st.button("Next Step: Final Polish ➡️"):
            st.session_state.current_step = 7
            st.rerun()

# === STEP 7: FINAL POLISH ===
elif st.session_state.current_step == 7:
    st.markdown('<div class="step-header">Phase 7 & 8: Final Polish & Verification Checklist</div>', unsafe_allow_html=True)
    
    st.success("Your Memo is nearly ready. This step extracts all facts that require human verification.")

    if st.button("Generate Verification Checklist"):
        sys_prompt = """
        You are a Fact-Checker (Phase 8).
        Scan the memo. Extract EVERY factual statement (numbers, dates, names, laws, causal claims) into a bulleted list.
        For each, mark it as:
        - [VERIFY] (Needs external check)
        - [UNCERTAIN] (AI logic might be shaky)
        
        Then, output the Final Polished Memo in clean Markdown.
        """
        user_prompt = f"Final Draft:\n{st.session_state.p5_draft}"
        result = generate_ai_content(user_prompt, sys_prompt)
        if result:
            st.session_state.p7_final = result

    if st.session_state.p7_final:
        st.subheader("🏁 Final Output")
        st.markdown(st.session_state.p7_final)
        
        st.download_button(
            label="📥 Download Policy Memo (.md)",
            data=st.session_state.p7_final,
            file_name="policy_memo_final.md",
            mime="text/markdown"
        )
