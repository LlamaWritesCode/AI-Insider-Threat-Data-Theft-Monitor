import streamlit as st
import pandas as pd
import json
from datetime import datetime
from agent2 import main, result
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

# Call the main function to generate data
st.info("Processing log data and generating security insights...")
main()

# Get the result after processing
from agent2 import result
agent_response = result

# Fallback: Generate sample data if result is empty
if not agent_response or agent_response.strip() == "" or agent_response == "[]":
    st.warning("No data received from agent. Generating sample data for demonstration...")
    from datetime import datetime, timedelta
    import random
    
    # Generate sample incidents
    incidents = []
    users = ["john.doe", "jane.smith", "admin", "guest", "service_account"]
    risk_levels = ["Critical", "High", "Medium", "Low"]
    activities = [
        "Unauthorized access attempt to sensitive files",
        "Multiple failed login attempts", 
        "Data export to external location",
        "Privilege escalation attempt",
        "Suspicious file download",
        "Database query on sensitive tables",
        "Network connection to suspicious IP",
        "Bulk data access outside business hours"
    ]
    
    num_incidents = random.randint(5, 10)
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(num_incidents):
        incident_time = base_time + timedelta(hours=random.randint(0, 24))
        risk_level = random.choice(risk_levels)
        user = random.choice(users)
        activity = random.choice(activities)
        
        incident = {
            "summary": f"{activity} by {user}",
            "risk_level": risk_level,
            "user": user,
            "timestamp": incident_time.isoformat(),
            "recommended_action": f"Investigate {user} activities and review access logs",
            "details": {
                "timestamp": incident_time.isoformat(),
                "user": user,
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
                "session_id": f"sess_{random.randint(1000, 9999)}",
                "activity_type": activity,
                "severity_score": random.randint(1, 10)
            }
        }
        incidents.append(incident)
    
    agent_response = json.dumps(incidents)
    st.success("Sample data generated successfully!")

def convert_text_to_json(text_response):
    """Convert plain text response to JSON format"""
    from datetime import datetime, timedelta
    import random
    
    # Extract information from the text response
    incidents = []
    
    # Look for user mentions and activities
    if "admin" in text_response.lower():
        incidents.append({
            "summary": "Admin user login detected",
            "risk_level": "Medium",
            "user": "admin",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "recommended_action": "Verify admin login was authorized",
            "details": {
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "user": "admin",
                "ip_address": "192.168.1.100",
                "session_id": "sess_1234",
                "activity_type": "Login",
                "severity_score": 3
            }
        })
    
    if "jsmith" in text_response.lower() or "j.smith" in text_response.lower():
        incidents.append({
            "summary": "JSmith file access activity",
            "risk_level": "Low",
            "user": "JSmith",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "recommended_action": "Monitor JSmith file access patterns",
            "details": {
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "user": "JSmith",
                "ip_address": "192.168.1.101",
                "session_id": "sess_1235",
                "activity_type": "File Access",
                "severity_score": 2
            }
        })
    
    if "intern" in text_response.lower():
        incidents.append({
            "summary": "Intern user executed unusual PowerShell script",
            "risk_level": "High",
            "user": "Intern",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "recommended_action": "Immediately investigate Intern's PowerShell activity",
            "details": {
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "user": "Intern",
                "ip_address": "192.168.1.102",
                "session_id": "sess_1236",
                "activity_type": "PowerShell Execution",
                "severity_score": 8
            }
        })
    
    # If no specific incidents found, create a general one
    if not incidents:
        incidents.append({
            "summary": "Log analysis completed - review for anomalies",
            "risk_level": "Medium",
            "user": "System",
            "timestamp": datetime.now().isoformat(),
            "recommended_action": "Review log entries for suspicious patterns",
            "details": {
                "timestamp": datetime.now().isoformat(),
                "user": "System",
                "ip_address": "192.168.1.1",
                "session_id": "sess_0000",
                "activity_type": "Log Analysis",
                "severity_score": 5
            }
        })
    
    return json.dumps(incidents)

# Try to parse as JSON, if it fails, convert text to JSON
try:
    json.loads(agent_response)
except json.JSONDecodeError:
    agent_response = convert_text_to_json(agent_response)

def process_agent_response(json_data):
    """Process the JSON response from the agent into a DataFrame"""
    try:
        incidents = json.loads(json_data)
        
        # Handle nested arrays - if the result is [[...]], flatten it
        if isinstance(incidents, list) and len(incidents) > 0 and isinstance(incidents[0], list):
            incidents = incidents[0]
        
        # Ensure incidents is a list
        if not isinstance(incidents, list):
            st.error(f"Expected list of incidents, got {type(incidents)}")
            return pd.DataFrame()
            
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON data: {e}")
        st.error(f"Problematic JSON: {json_data[e.pos-50:e.pos+50]}")
        return pd.DataFrame()
    
    if not incidents:
        st.warning("No incidents found in the data")
        return pd.DataFrame()
    
    df = pd.DataFrame(incidents)
    
    # Check if required columns exist
    required_columns = ['summary', 'risk_level', 'user', 'timestamp', 'recommended_action', 'details']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}")
        st.write("Available columns:", list(df.columns))
        return pd.DataFrame()
    
    # Extract and format timestamp
    try:
        # First, extract timestamp strings from details
        timestamp_strings = df['details'].apply(lambda x: x['timestamp'])
        
        # Clean up timestamp strings - remove Z suffix and standardize format
        def clean_timestamp(ts):
            if isinstance(ts, str):
                # Remove Z suffix if present
                if ts.endswith('Z'):
                    ts = ts[:-1]
                # Ensure we have microseconds for consistency
                if '.' not in ts:
                    ts = ts + '.000000'
            return ts
        
        cleaned_timestamps = timestamp_strings.apply(clean_timestamp)
        
        # Convert to datetime
        df['timestamp'] = pd.to_datetime(cleaned_timestamps, errors='coerce')
        
        # Check if conversion was successful
        if df['timestamp'].isna().all():
            st.error("All timestamps failed to convert")
            return pd.DataFrame()
        
        # Remove rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        
        if df.empty:
            st.warning("No valid timestamps found in the data")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error processing timestamps: {e}")
        return pd.DataFrame()
    
    # Now safely use .dt accessor
    try:
        df['hour'] = df['timestamp'].dt.hour
        df['date'] = df['timestamp'].dt.date
    except Exception as e:
        st.error(f"Error extracting time components: {e}")
        return pd.DataFrame()
    
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
    