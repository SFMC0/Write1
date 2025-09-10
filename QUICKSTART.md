# SFMC AI Agent - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### 1. Install Requirements
```bash
pip install fastmcp mcp requests python-dotenv
```

### 2. Test Server Setup
```bash
python test-server.py
```
You should see all tests pass ✅

### 3. Set Up SFMC Connected App

**In Salesforce Marketing Cloud:**

1. **Setup → Apps → Installed Packages**
2. **Create New Connected App**
   - Name: "Asset Search Agent" 
   - Description: "MCP-based asset search"
3. **Enable OAuth Settings**
   - Grant Type: ✅ Client Credentials
   - Scopes: `email_read`, `email_write`, `offline`
4. **Get Credentials**
   - Copy Client ID and Client Secret
   - Note your subdomain (e.g., `mc123456789`)

### 4. Configure Credentials

Create `.env` file:
```bash
SFMC_SUBDOMAIN=your_subdomain
SFMC_CLIENT_ID=your_client_id  
SFMC_CLIENT_SECRET=your_client_secret
```

### 5. Run the Agent
```bash
python sfmc-mcp-client.py
```

### 6. Initialize Connection
```bash
🤖 SFMC Agent> init your_subdomain your_client_id your_client_secret
```

### 7. Start Searching!
```bash
🤖 SFMC Agent> search newsletter
🤖 SFMC Agent> search email template
🤖 SFMC Agent> get 12345
```

## 🎯 Common Use Cases

### Find All Email Templates
```bash
advanced {"query": {"property": "assetType.name", "simpleOperator": "eq", "value": "template"}}
```

### Search Recent Assets
```bash
advanced {"query": {"property": "modifiedDate", "simpleOperator": "gt", "value": "2024-01-01"}}
```

### Find Assets by Creator
```bash
advanced {"query": {"property": "createdBy.name", "simpleOperator": "contains", "value": "john"}}
```

## 🆘 Troubleshooting

### Authentication Error?
- Check client credentials are correct
- Verify Connected App has Client Credentials enabled
- Ensure integration user is assigned

### No Assets Found?
- Check user permissions in SFMC
- Verify search criteria
- Try broader search terms

### Server Won't Start?
- Run `python test-server.py` first
- Check all dependencies installed
- Verify Python 3.8+ is being used

## 💡 Pro Tips

1. **Use `status` command** to check connection health
2. **Use `types` command** to see available asset types  
3. **Start with simple searches** before trying advanced queries
4. **Use page sizes of 10-20** for better readability
5. **Save frequently used queries** as bash aliases

## 🔗 Next Steps

- Explore the full README.md for detailed documentation
- Check out advanced search examples
- Customize the agent for your specific needs
- Integrate with your existing workflows

Happy searching! 🚀