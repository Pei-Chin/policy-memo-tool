import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import json

# --- 1. CONFIGURATION & STYLES ---
st.set_page_config(
    page_title="Policy Memo Architect (Pro)",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS to match the "Crimson Pro" academic vibe
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
    
    h1, h2, h3 { font-family: 'Crimson Pro', serif; }
    p, div, button { font-family: 'IBM Plex Sans', sans-serif; }
    
    .phase-box {
        border: 1px solid #e5e2db;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: white;
    }
    .search-badge {
        background-color: #dbeafe;
        color: #1d4ed8;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.7em;
        font-weight: bold;
        margin-left: 8px;
    }
    .step-card {
        background-color: #fafaf8;
        border-left: 3px solid #e5e2db;
        padding: 15px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .verify-tag {
        background-color: #fef3c7;
        color: #92400e;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: bold;
        font-size: 0.8em;
    }
    .stButton button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA STRUCTURE (The Logic from React) ---
PHASES = [
    {
        "id": "phase0", "name": "Phase 0: Triangle of Persuasion", 
        "desc": "Define Audience, Purpose, and Position",
        "explanation": "Before gathering data or drafting, define your three foundations. If any part is unclear, the memo's persuasiveness collapses.",
        "steps": [
            {"key": "audience_profile", "name": "Define Your Audience", "useSearch": False},
            {"key": "purpose_clarity", "name": "Clarify Your Purpose", "useSearch": False},
            {"key": "position_credibility", "name": "Establish Your Position", "useSearch": False}
        ]
    },
    {
        "id": "phase1", "name": "Phase 1: Frame the Policy Problem", 
        "desc": "Define a problem that is analytically rigorous",
        "explanation": "We're not writing about broad topics. We're writing about a specific policy problem using real data.",
        "steps": [
            {"key": "core_issue", "name": "Identify the Core Issue", "useSearch": True},
            {"key": "scope_scale", "name": "Determine Scope and Scale", "useSearch": True},
            {"key": "stakeholders", "name": "Define Stakeholders", "useSearch": True}
        ]
    },
    {
        "id": "phase2", "name": "Phase 2: Build the Evidence Base", 
        "desc": "Status, Criteria, Interpretation, Outlook",
        "explanation": "Shift from defining what's wrong to explaining why it matters and how we know using verified sources.",
        "steps": [
            {"key": "status", "name": "Status — What Is Happening", "useSearch": True},
            {"key": "criteria", "name": "Criteria — What Matters", "useSearch": False},
            {"key": "interpretation", "name": "Interpretation — Why This Is Happening", "useSearch": True},
            {"key": "outlook", "name": "Outlook — What Might Happen Next", "useSearch": True}
        ]
    },
    {
        "id": "phase3", "name": "Phase 3: Develop Recommendation", 
        "desc": "Move from analysis to action",
        "explanation": "A persuasive recommendation is specific, feasible, and proportionate to the evidence.",
        "steps": [
            {"key": "leverage_point", "name": "Identify Leverage Points", "useSearch": True},
            {"key": "alternatives", "name": "Evaluate Alternatives", "useSearch": True},
            {"key": "recommendation", "name": "Articulate the Recommendation", "useSearch": False}
        ]
    },
    {
        "id": "phase4", "name": "Phase 4: Draft Executive Summary", 
        "desc": "Signal purpose and trustworthiness",
        "explanation": "Different audiences need different structures. Choose the type that fits your memo's purpose.",
        "steps": [
            {"key": "executive_summary", "name": "Executive Summary", "useSearch": False}
        ]
    },
    {
        "id": "phase5", "name": "Phase 5: Structure the Memo", 
        "desc": "Organize with clarity and flow",
        "explanation": "Assemble all sections. Apply deductive paragraph structure and active voice.",
        "steps": [
            {"key": "full_memo_draft", "name": "Complete Memo Draft", "useSearch": False}
        ]
    },
    {
        "id": "phase6", "name": "Phase 6: Tone & Bias Check", 
        "desc": "Ensure empathy, inclusion, and balance",
        "explanation": "Review for professional yet empathetic tone. Check for implicit bias.",
        "steps": [
            {"key": "tone_audit", "name": "Tone Audit", "useSearch": False},
            {"key": "bias_audit", "name": "Bias Audit", "useSearch": False},
            {"key": "trauma_check", "name": "Trauma-Informed Check", "useSearch": False}
        ]
    },
    {
        "id": "phase7", "name": "Phase 7: Guided Revision", 
        "desc": "Systematic revision",
        "explanation": "Move through revisions systematically: macro, meso, and micro levels.",
        "steps": [
            {"key": "macro_revision", "name": "Macro-Level Revision", "useSearch": False},
            {"key": "meso_revision", "name": "Meso-Level Revision", "useSearch": False},
            {"key": "micro_revision", "name": "Micro-Level Revision", "useSearch": False}
        ]
    },
    {
        "id": "phase8", "name": "Phase 8: Final Polish", 
        "desc": "Quality assurance checklist",
        "explanation": "Final pass before submission. Extract claims needing verification.",
        "steps": [
            {"key": "final_checklist", "name": "Final Checklist", "useSearch": False},
            {"key": "verification_list", "name": "Verification List", "useSearch": False},
            {"key": "final_memo", "name": "Final Polished Memo", "useSearch": False}
        ]
    }
]

# --- 3. STATE MANAGEMENT ---
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'input_data' not in st.session_state:
    st.session_state.input_data = {}

# --- 4. PROMPT ENGINEERING (Ported from React) ---
def create_prompt(step_key, input_data, results, use_search):
    # Context variables
    topic = input_data.get('topic', '')
    policymaker = input_data.get('policymaker_type', '')
    audience = input_data.get('audience', '')
    purpose = input_data.get('purpose', '')
    role = input_data.get('writer_role', '')
    
    # Previous results retrieval helper
    def get_res(key): return results.get(key, '')

    search_instruction = ""
    if use_search:
        search_instruction = """
        \n\n**CRITICAL INSTRUCTION: USE GOOGLE SEARCH.** You MUST search for REAL, CURRENT data, statistics, and specific examples. 
        - Do not make up numbers. 
        - Cite your sources with names and years (e.g., U.S. Census Bureau, 2023).
        - If you cannot find a specific number, state that data is unavailable rather than hallucinating.
        """

    prompts = {
        "audience_profile": f"""
            Profile the target audience.
            Topic: {topic} | Policymaker: {policymaker} | Audience: {audience}
            Answer: 1) Who is the primary reader? 2) What authority do they have? 3) What do they value most (efficiency, equity, etc.)? 
            Describe top 3 decision priorities.
        """,
        "purpose_clarity": f"""
            Clarify the memo's purpose.
            Audience Profile: {get_res('audience_profile')}
            Stated Purpose: {purpose}
            Suggest 3 distinct purposes (inform/evaluate/persuade) and how each affects tone and evidence.
        """,
        "position_credibility": f"""
            Establish the writer's credibility.
            Role: {role} | Topic: {topic}
            Draft 2 sentences establishing analytical credibility without overstating expertise.
        """,
        "core_issue": f"""
            Frame the core policy issue using REAL DATA.
            Topic: {topic} | Audience: {audience}
            **Search for current stats.** Answer with REAL DATA: 
            1) What is happening? (Include stats) 
            2) Why does it matter NOW? 
            3) Who is affected?
            {search_instruction}
        """,
        "scope_scale": f"""
            Determine scope and scale using REAL DATA.
            Core Issue: {get_res('core_issue')}
            Policymaker: {policymaker}
            **Search for jurisdiction info.**
            Propose 3 ways to narrow this into a tractable problem. Identify which agency has jurisdiction.
            {search_instruction}
        """,
        "stakeholders": f"""
            Define stakeholders with REAL information.
            Issue: {get_res('core_issue')}
            **Search for actual stakeholder orgs.**
            Create a map: Primary, Secondary, Decision-makers. Name actual organizations.
            {search_instruction}
        """,
        "status": f"""
            Describe current STATUS using REAL, VERIFIED DATA.
            Problem: {get_res('core_issue')}
            **Search for verified statistics.**
            Find REAL DATA on: 1) Scope/Scale 2) Recent trends (last 3 years) 3) Policy environment.
            Every number must have a source.
            {search_instruction}
        """,
        "criteria": f"""
            Define evaluation CRITERIA.
            Audience: {audience} | Purpose: {purpose}
            List 3-5 criteria defining "success" for this audience.
        """,
        "interpretation": f"""
            Provide INTERPRETATION using RESEARCH.
            Status: {get_res('status')}
            **Search for research on root causes.**
            Distinguish proximate from root causes. Cite think tanks or academic studies.
            {search_instruction}
        """,
        "outlook": f"""
            Forecast OUTLOOK using PROJECTIONS.
            Status: {get_res('status')}
            **Search for credible forecasts.**
            Scenario A (Status Quo) vs Scenario B (Reform).
            {search_instruction}
        """,
        "leverage_point": f"""
            Identify LEVERAGE POINTS.
            Decision-Maker: {policymaker}
            **Search for legal/admin authority.**
            What mechanisms (law, funding, pilot) can they realistically use?
            {search_instruction}
        """,
        "alternatives": f"""
            EVALUATE ALTERNATIVES with CASE STUDIES.
            Criteria: {get_res('criteria')}
            **Search for actual implementations elsewhere.**
            Compare 3 options. For each, find where it has been tried and what the outcomes were.
            {search_instruction}
        """,
        "recommendation": f"""
            ARTICULATE RECOMMENDATION.
            Alternatives: {get_res('alternatives')}
            Draft a concise recommendation that is specific, measurable, and tied to the evidence.
        """,
        "executive_summary": f"""
            Draft EXECUTIVE SUMMARY.
            Problem: {get_res('core_issue')} | Recommendation: {get_res('recommendation')}
            Choose the best structure (Recommendation-First, Criteria-Driven, etc.) based on Purpose: {purpose}.
        """,
        "full_memo_draft": f"""
            STRUCTURE THE COMPLETE MEMO.
            Exec Summary: {get_res('executive_summary')}
            Status: {get_res('status')}
            Interpretation: {get_res('interpretation')}
            Recommendation: {get_res('recommendation')}
            
            Write 800-1200 words. Sections: 
            1) Title & Exec Summary 
            2) Status/Background 
            3) Analysis 
            4) Recommendation 
            5) Implementation 
            6) Sources List.
        """,
        "tone_audit": f"""
            TONE AUDIT.
            Memo: {get_res('full_memo_draft')}
            Review for empathy, factualness, and lack of paternalism.
        """,
        "bias_audit": f"""
            BIAS AUDIT.
            Memo: {get_res('full_memo_draft')}
            Identify implicit assumptions or unfair framings.
        """,
        "trauma_check": f"""
            TRAUMA-INFORMED CHECK.
            Memo: {get_res('full_memo_draft')}
            Ensure dignity and agency for affected groups.
        """,
        "macro_revision": f"""
            MACRO-LEVEL REVISION.
            Review structure and flow. Does every section advance the purpose?
        """,
        "meso_revision": f"""
            MESO-LEVEL REVISION.
            Check data sources and balance of evidence.
        """,
        "micro_revision": f"""
            MICRO-LEVEL REVISION.
            Identify wordy sentences and passive voice. Suggest concise rewrites.
        """,
        "final_checklist": f"""
            FINAL CHECKLIST.
            Evaluate Clarity, Concision, Evidence, and Tone.
        """,
        "verification_list": f"""
            VERIFICATION LIST.
            Extract ALL factual statements from: {get_res('full_memo_draft')}
            List numbers, dates, names. Indicate if source is cited.
        """,
        "final_memo": f"""
            FINAL POLISHED MEMO.
            Refine the draft: {get_res('full_memo_draft')}
            Incorporate all audit feedback. Ensure professional formatting.
            Add a 'Verification Notes' section at the end.
        """
    }
    
    return prompts.get(step_key, "Generate content.") + search_instruction

# --- 5. AI GENERATION FUNCTION ---
def generate_step_content(api_key, step_key, use_search):
    if not api_key:
        st.error("Please enter API Key in sidebar.")
        return
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Tool Configuration
    # 修正: 確保 tools 是一個列表，且格式正確
    tools = []
    if use_search:
        # 這是新版 SDK 的標準寫法
        tools = [{'google_search': {}}] 
    
    try:
        # 建議: 雖然你註解寫 flash，但 Policy Memo 需要較強的邏輯，建議維持使用 'gemini-1.5-pro'
        # 注意: 如果 tools 是空列表，建議不要傳入該參數，或者傳入 None，避免部分舊版 API 報錯
        model_kwargs = {'model_name': 'gemini-1.5-pro'}
        if tools:
            model_kwargs['tools'] = tools

        model = genai.GenerativeModel(**model_kwargs)
        
        prompt = create_prompt(step_key, st.session_state.input_data, st.session_state.results, use_search)
        
        system_instruction = """
        You are an expert Policy Analyst following David Chrisinger's workflow.
        Key Rules:
        1. USE REAL DATA when requested.
        2. Cite sources (Name, Year).
        3. Be specific, not generic.
        4. Do not hallucinate. If data isn't found, say so.
        """
        
        with st.spinner(f"🤖 Generating {step_key.replace('_', ' ')}... {'(Searching Web 🌍)' if use_search else ''}"):
            # 呼叫 generate_content
            response = model.generate_content(
                f"{system_instruction}\n\nTASK:\n{prompt}",
                generation_config=genai.types.GenerationConfig(temperature=0.3)
            )
            
            # 處理回應
            text = response.text
            
            # 簡單的格式處理
            if "[VERIFY]" not in text and use_search:
                text += "\n\n*(Note: Please verify specific numbers against primary sources)*"
                
            st.session_state.results[step_key] = text
            st.rerun() # Refresh to show result
            
    except Exception as e:
        st.error(f"Generation Error: {str(e)}")
        
        # 增加針對此特定錯誤的提示
        if "Unknown field for FunctionDeclaration" in str(e):
             st.warning("⚠️ 此錯誤通常表示 'google-generativeai' 函式庫版本過舊。請在終端機執行: pip install -U google-generativeai")
        
        if "400" in str(e):
            st.warning("Tip: Check if your API Key supports the selected model.")
        st.info("Tip: If you are using a free key, high-frequency search requests might be rate-limited.")

# --- 6. SIDEBAR & INPUT ---
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.caption("Get a free key at [Google AI Studio](https://aistudio.google.com/).")
    
    st.markdown("---")
    st.info("Workflow based on *Public Policy Writing That Matters* by David Chrisinger.")
    
    if st.button("🗑️ Reset All Progress"):
        st.session_state.results = {}
        st.rerun()

# --- 7. MAIN INTERFACE ---
st.title("🏛️ Policy Memo Architect")
st.markdown("**An Algorithm for Clarity, Concision, and Compelling Argument**")
st.markdown("This tool follows a strict 9-phase workflow, utilizing **Google Search** to ground your memo in real data.")

# INPUT SECTION
with st.expander("📝 Step 1: Define Memo Parameters", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic", value="Affordable housing reform in Chicago")
        policymaker = st.text_input("Policymaker", value="City Budget Director")
        audience = st.text_input("Audience", value="City Budget Director's Office")
    with col2:
        purpose = st.text_input("Purpose", value="Persuade adoption of pilot program")
        role = st.text_input("Writer Role", value="Independent Analyst")
        context = st.text_input("Institution", value="Urban Policy Institute")
    
    # Save inputs
    st.session_state.input_data = {
        "topic": topic, "policymaker_type": policymaker, "audience": audience,
        "purpose": purpose, "writer_role": role, "institutional_context": context
    }

# PHASES LOOP
st.markdown("### 🚀 Workflow Phases")

for phase in PHASES:
    # Check if previous phase is done (simple logic: check if last step of prev phase has result)
    # For simplicity, we allow users to open any phase, but warn if data missing
    
    with st.expander(f"**{phase['name']}**", expanded=False):
        st.info(f"{phase['explanation']}")
        
        for step in phase['steps']:
            step_key = step['key']
            has_result = step_key in st.session_state.results
            
            st.markdown(f"#### {step['name']}")
            if step['useSearch']:
                st.markdown('<span class="search-badge">🌍 WEB SEARCH ENABLED</span>', unsafe_allow_html=True)
            
            # Display Result if exists
            if has_result:
                st.markdown(f'<div class="step-card">{st.session_state.results[step_key]}</div>', unsafe_allow_html=True)
                
                col_a, col_b = st.columns([1, 5])
                if col_a.button("🔄 Regenerate", key=f"regen_{step_key}"):
                    generate_step_content(api_key, step_key, step['useSearch'])
            else:
                # Generate Button
                if st.button(f"Generate {step['name']}", key=f"gen_{step_key}", type="primary"):
                    generate_step_content(api_key, step_key, step['useSearch'])
            
            st.markdown("---")

# EXPORT SECTION
if 'final_memo' in st.session_state.results:
    st.markdown("### 📥 Export")
    memo_content = st.session_state.results['final_memo']
    verification = st.session_state.results.get('verification_list', '')
    
    full_doc = f"{memo_content}\n\n---\n\n# VERIFICATION CHECKLIST\n\n{verification}"
    
    st.download_button(
        label="Download Policy Memo (.md)",
        data=full_doc,
        file_name="policy_memo.md",
        mime="text/markdown"
    )
