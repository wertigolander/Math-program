import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Math Practice Buddy 🎓",
    page_icon="🧮",
    layout="centered"
)

# Initialize session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_attempts' not in st.session_state:
    st.session_state.total_attempts = 0
if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None

# Header
st.title("🧮 Math Practice Buddy")
st.write("Let's practice math together and have fun learning! 🌟")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key = st.text_input(
        "Google API Key", 
        type="password",
        help="Get your key from aistudio.google.com"
    )
    
    grade_level = st.selectbox(
        "Grade Level",
        ["Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", "4th Grade", "5th Grade"]
    )
    
    problem_type = st.selectbox(
        "What to Practice?",
        ["Addition", "Subtraction", "Multiplication", "Division", "Mixed Operations", "Word Problems", "Fractions"]
    )
    
    difficulty = st.radio(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )
    
    st.divider()
    
    # Progress tracker
    st.subheader("📊 Your Progress")
    if st.session_state.total_attempts > 0:
        percentage = (st.session_state.score / st.session_state.total_attempts) * 100
        st.metric("Correct Answers", f"{st.session_state.score}/{st.session_state.total_attempts}")
        st.progress(percentage / 100)
        st.write(f"**{percentage:.0f}%** - Keep it up! 🎉")
    else:
        st.write("Start practicing to track your progress!")
    
    if st.button("🔄 Reset Score"):
        st.session_state.score = 0
        st.session_state.total_attempts = 0
        st.rerun()

# Main area
if not api_key:
    st.warning("👈 Please enter your Google API key in the sidebar to begin!")
    st.info("""
    **How to get an API key:**
    1. Visit [aistudio.google.com](https://aistudio.google.com)
    2. Click "Get API key"
    3. Create a new API key
    4. Copy and paste it in the sidebar
    
    **Note:** Google offers a FREE tier with generous limits! Perfect for learning apps.
    """)
else:
    # Configure Google API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free tier friendly
    
    # Generate problem button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🎲 Generate New Problem", type="primary", use_container_width=True):
            with st.spinner("Creating a fun problem for you..."):
                try:
                    prompt = f"""You are a friendly math tutor for {grade_level} students.

Generate ONE {difficulty.lower()} difficulty {problem_type.lower()} problem appropriate for {grade_level}.

Requirements:
- Make it engaging and age-appropriate
- For word problems, use fun scenarios (toys, animals, games, snacks, friends)
- Keep numbers reasonable for this grade level
- Return ONLY the problem text, nothing else
- DO NOT include the answer

Examples:
- Basic: "What is 7 + 5?"
- Word problem: "Alex has 15 toy cars and gets 8 more for his birthday. How many toy cars does Alex have now?"
"""
                    response = model.generate_content(prompt)
                    st.session_state.current_problem = response.text.strip()
                    
                except Exception as e:
                    st.error(f"Oops! Error: {str(e)}")
    
    with col2:
        if st.button("💡 Hint"):
            if st.session_state.current_problem:
                with st.spinner("Thinking..."):
                    try:
                        hint_prompt = f"""Student problem: {st.session_state.current_problem}

Give ONE helpful hint that guides them without giving the answer away.
Be encouraging. Use simple language for {grade_level}."""
                        
                        response = model.generate_content(hint_prompt)
                        st.info(f"💡 **Hint:** {response.text.strip()}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Generate a problem first!")
    
    # Display current problem
    if st.session_state.current_problem:
        st.markdown("---")
        st.subheader("📝 Your Problem:")
        st.markdown(f"### {st.session_state.current_problem}")
        
        # Answer input
        user_answer = st.text_input(
            "Your answer:", 
            key="answer_input",
            placeholder="Type your answer here..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✓ Check Answer", type="primary", use_container_width=True):
                if user_answer:
                    with st.spinner("Checking your answer..."):
                        try:
                            check_prompt = f"""You are a friendly math tutor for {grade_level}.

Problem: {st.session_state.current_problem}
Student's answer: {user_answer}

Check if correct, then respond:
- If CORRECT: Celebrate enthusiastically! Explain why in simple terms.
- If INCORRECT: Be very encouraging. Guide them gently. Explain the right approach step-by-step.

Be warm, supportive, and use emojis! Appropriate for {grade_level}."""
                            
                            response = model.generate_content(check_prompt)
                            feedback = response.text.strip()
                            
                            # Check if correct
                            is_correct = any(word in feedback.lower() for word in 
                                           ['correct', 'right', 'yes', 'perfect', 'excellent', 'great job', 'amazing', 'wonderful'])
                            
                            if is_correct:
                                st.success(feedback)
                                st.balloons()
                                st.session_state.score += 1
                                st.session_state.total_attempts += 1
                            else:
                                st.warning(feedback)
                                st.session_state.total_attempts += 1
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.warning("Please type an answer first!")
        
        with col2:
            if st.button("📚 Explain Solution", use_container_width=True):
                with st.spinner("Preparing explanation..."):
                    try:
                        explain_prompt = f"""You are a friendly math tutor for {grade_level}.

Problem: {st.session_state.current_problem}

Explain the solution step-by-step:
- Use simple language for {grade_level}
- Number each step clearly
- Use visual descriptions ("imagine you have 5 apples...")
- Be encouraging
- Use emojis
- Explain WHY, not just HOW"""
                        
                        response = model.generate_content(explain_prompt)
                        st.info(response.text.strip())
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Made with for learning | Powered by Google Gemini </p>
</div>
""", unsafe_allow_html=True)
```

## **File 2: `requirements.txt`**
```
streamlit>=1.28.0
google-generativeai>=0.3.0
