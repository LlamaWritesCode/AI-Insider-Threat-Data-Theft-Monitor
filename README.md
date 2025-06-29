# 🛡️ AI Insider Data Protection Dashboard

A real-time security monitoring dashboard that uses IBM Watson AI to detect and analyze potential insider threats and data theft activities within organizations.

## Features

- **Real-time Log Analysis**: Processes system logs in chunks for continuous monitoring
- **AI-Powered Threat Detection**: Uses IBM Watson AI to identify security incidents
- **Interactive Dashboard**: Streamlit-based interface with real-time metrics and visualizations
- **Risk Level Categorization**: Classifies incidents as Critical, High, Medium, or Low risk
- **User Activity Tracking**: Monitors individual user activities and patterns
- **Timeline Visualization**: Chronological view of security incidents
- **Filtering & Search**: Advanced filtering by risk level and user

## Security Incidents Detected

The system can identify various types of security threats:

- **Unauthorized Access Attempts**
- **Suspicious File Access**
- **PowerShell Script Execution**
- **External Network Connections**
- **Audit Log Tampering**
- **Account Lockouts**
- **Data Exfiltration Attempts**
- **Privilege Escalation**

## Technology Stack

- **AI/ML**: IBM Watson AI (Granite-3-3-8b-instruct model)
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Log Processing**: Custom chunking system
- **Visualization**: Streamlit charts and components

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-insider-data-protection.git
   cd ai-insider-data-protection
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure IBM Watson**:
   - Update the API credentials in `agent2.py`
   - Ensure you have access to IBM Watson AI services

## Usage

1. **Start the dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

2. **Add log files**:
   - Place your system logs in the project directory
   - Update the filename in `agent2.py` if needed

3. **Monitor security**:
   - The dashboard will automatically process logs
   - View real-time security insights and incidents

## Project Structure

```
ai-insider-data-protection/
├── dashboard.py          # Main Streamlit dashboard
├── agent2.py            # IBM Watson AI agent
├── input.py             # Log processing utilities
├── sys_log.txt          # Sample system logs
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Git ignore rules
```

## Configuration

### IBM Watson Setup

1. Get your IBM Watson API credentials
2. Update the credentials in `agent2.py`:
   ```python
   def get_credentials():
       return {
           "url": "https://us-south.ml.cloud.ibm.com",
           "apikey": "YOUR_API_KEY"
       }
   ```

### Log Processing

- **Chunk Size**: Adjust `lines_per_chunk` in `agent2.py`
- **Processing Delay**: Modify `delay_between_chunks` for performance tuning
- **Log Format**: Ensure logs follow the expected CSV format

## Security Features

- **Real-time Analysis**: Continuous monitoring of system activities
- **AI-Powered Detection**: Advanced threat detection using IBM Watson
- **Risk Assessment**: Automated risk level classification
- **Incident Tracking**: Comprehensive incident timeline and details
- **User Monitoring**: Individual user activity tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact the development team

## Disclaimer

This tool is designed for educational and security research purposes. Always ensure you have proper authorization before monitoring any systems or networks. 