import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="AI Insider Threat Monitor",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .critical { background-color: #ff4444 !important; }
    .high { background-color: #ff6666 !important; }
    .medium { background-color: #ffbb33 !important; }
    .low { background-color: #00C851 !important; }
    .metric-card { 
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .plot-container { 
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .incident-card {
        border-left: 5px solid;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .critical-card { border-left-color: #ff4444; }
    .high-card { border-left-color: #ff6666; }
    .medium-card { border-left-color: #ffbb33; }
    .low-card { border-left-color: #00C851; }
</style>
""", unsafe_allow_html=True)

# Properly formatted JSON data with escaped backslashes
agent_response = r'''[
  {
    "incident_id": "INC20250628-001",
    "summary": "On June 28, 2025, at 02:22:48, user 'Intern' launched an unusual PowerShell script. Risk Level: Medium. Recommended Action: Notify security team.",
    "risk_level": "Medium",
    "recommended_action": "Notify security team",
    "details": {
      "user": "Intern",
      "event": "2025-06-28,02:22:48,Warning,Security,4688,Process Creation,User Intern launched an unusual PowerShell script.",
      "timestamp": "2025-06-28 02:22:48"
    }
  },
  {
    "incident_id": "INC20250628-002",
    "summary": "On June 28, 2025, at 03:09:22, user account 'Intern' was locked out. Risk Level: Medium. Recommended Action: Suspend user access and investigate.",
    "risk_level": "Medium",
    "recommended_action": "Suspend user access and investigate",
    "details": {
      "user": "Intern",
      "event": "2025-06-28,03:09:22,Error,Security,4740,Account Lockout,A user account was locked out. Account: Intern.",
      "timestamp": "2025-06-28 03:09:22"
    }
  },
  {
    "incident_id": "INC20250628-006",
    "summary": "On June 28, 2025, at 05:55:18, a suspicious connection was made to IP: 198.51.100.45 by 'Intern'. Risk Level: High. Recommended Action: Suspend user access and investigate.",
    "risk_level": "High",
    "recommended_action": "Suspend user access and investigate",
    "details": {
      "user": "Intern",
      "event": "2025-06-28,05:55:18,Error,Security,36887,Suspicious Connection,A suspicious connection was made to IP: 198.51.100.45 by Intern.",
      "timestamp": "2025-06-28 05:55:18"
    }
  },
  {
    "incident_id": "INC20250628-008",
    "summary": "On June 28, 2025, at 02:13:53, a suspicious connection was made to IP: 203.0.113.45 by 'JSmith'. Risk Level: High. Recommended Action: Suspend user access and investigate.",
    "risk_level": "High",
    "recommended_action": "Suspend user access and investigate",
    "details": {
      "user": "JSmith",
      "event": "2025-06-28,02:13:53,Error,Security,36887,Suspicious Connection,A suspicious connection was made to IP: 203.0.113.45 by JSmith.",
      "timestamp": "2025-06-28 02:13:53"
    }
  },
  {
    "incident_id": "INC20250628-009",
    "summary": "On June 28, 2025, at 00:04:22, user 'Intern' accessed the sensitive file 'EmployeeData.xlsx'. Risk Level: Medium. Recommended Action: Notify security team.",
    "risk_level": "Medium",
    "recommended_action": "Notify security team",
    "details": {
      "user": "Intern",
      "event": "2025-06-28,00:04:22,Warning,Security,4663,File Access,File accessed: C:\\\\HR\\\\EmployeeData.xlsx by Intern.",
      "timestamp": "2025-06-28 00:04:22"
    }
  }
]'''

def process_agent_response(json_data):
    """Process the JSON response from the agent into a DataFrame"""
    try:
        incidents = json.loads(json_data)
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON data: {e}")
        st.error(f"Problematic JSON: {json_data[e.pos-50:e.pos+50]}")
        return pd.DataFrame()
    
    df = pd.DataFrame(incidents)
    
    # Extract and format timestamp
    df['timestamp'] = pd.to_datetime(df['details'].apply(lambda x: x['timestamp']))
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date
    
    # Extract user from details
    df['user'] = df['details'].apply(lambda x: x['user'])
    
    # Create risk level order for sorting
    risk_level_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
    df['risk_level_order'] = df['risk_level'].map(risk_level_order)
    
    return df

# Process the data
df = process_agent_response(agent_response)

# Only proceed if we have data
if not df.empty:
    # Dashboard Header
    st.title("🛡️ AI Insider Threat & Data Theft Monitoring Dashboard")
    st.markdown("""
    This dashboard provides real-time monitoring and analysis of potential insider threats and data theft activities within the organization.
    """)

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_events = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Events</h3>
            <h1>{total_events}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        critical_events = len(df[df['risk_level'] == 'Critical'])
        st.markdown(f"""
        <div class="metric-card {'critical' if critical_events > 0 else ''}">
            <h3>Critical Events</h3>
            <h1>{critical_events}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        high_events = len(df[df['risk_level'] == 'High'])
        st.markdown(f"""
        <div class="metric-card {'high' if high_events > 0 else ''}">
            <h3>High Risk Events</h3>
            <h1>{high_events}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        suspicious_users = df['user'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Suspicious Users</h3>
            <h1>{suspicious_users}</h1>
        </div>
        """, unsafe_allow_html=True)

    # Charts Row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("Events by Risk Level")
        risk_counts = df['risk_level'].value_counts()
        st.bar_chart(risk_counts)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
        st.subheader("Events by Hour of Day")
        hourly_counts = df['hour'].value_counts().sort_index()
        st.line_chart(hourly_counts)
        st.markdown('</div>', unsafe_allow_html=True)

    # Incident Timeline
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.subheader("Incident Timeline")

    for _, row in df.sort_values('timestamp', ascending=False).iterrows():
        risk_class = f"{row['risk_level'].lower()}-card"
        st.markdown(f"""
        <div class="incident-card {risk_class}">
            <h4>{row['summary']}</h4>
            <p><strong>User:</strong> {row['user']}</p>
            <p><strong>Timestamp:</strong> {row['timestamp']}</p>
            <p><strong>Recommended Action:</strong> {row['recommended_action']}</p>
            <details>
                <summary>View Details</summary>
                <pre>{json.dumps(row['details'], indent=2)}</pre>
            </details>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed Events Table
    st.subheader("Detailed Event Log")
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)

    # Add filtering options
    col1, col2 = st.columns(2)

    with col1:
        risk_filter = st.multiselect(
            "Filter by Risk Level",
            options=df['risk_level'].unique(),
            default=df['risk_level'].unique()
        )

    with col2:
        user_filter = st.multiselect(
            "Filter by User",
            options=df['user'].unique(),
            default=df['user'].unique()
        )

    # Apply filters
    filtered_df = df[
        (df['risk_level'].isin(risk_filter)) &
        (df['user'].isin(user_filter))
    ]

    # Display the table with custom styling
    def color_risk_level(val):
        if val == 'Critical':
            color = 'red'
        elif val == 'High':
            color = 'orangered'
        elif val == 'Medium':
            color = 'orange'
        else:
            color = 'green'
        return f'color: {color}; font-weight: bold'

    styled_df = filtered_df[['timestamp', 'user', 'risk_level', 'summary', 'recommended_action']].sort_values('timestamp', ascending=False)
    styled_df = styled_df.style.applymap(color_risk_level, subset=['risk_level'])

    st.dataframe(styled_df, height=400, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("No valid data to display. Please check the JSON input.")  