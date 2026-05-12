import streamlit as st

def render_assessment_card(assessment):
    """Render a beautiful card for an assessment."""
    st.markdown(
        f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        ">
            <h4 style="margin-top: 0; margin-bottom: 8px; color: #1e1e1e;">
                <a href="{assessment.get('url', '#')}" target="_blank" style="text-decoration: none; color: #0056b3;">
                    {assessment.get('name', 'Unknown Assessment')}
                </a>
            </h4>
            <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                <span style="background-color: #f0f4f8; color: #003366; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500;">
                    Type: {assessment.get('test_type', 'Unknown')}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
