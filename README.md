# SFMC AI Agent - Asset Search with MCP

A powerful AI agent for Salesforce Marketing Cloud (SFMC) that uses Model Context Protocol (MCP) to provide intelligent asset search capabilities. This system consists of a local MCP server and client that authenticate with SFMC using OAuth 2.0 Client Credentials flow and provide comprehensive asset search functionality.

## 🚀 Features

### Core Capabilities
- **OAuth 2.0 Authentication**: Secure authentication using client credentials flow
- **Asset Search**: Search assets by name, type, category, and other parameters
- **Advanced Querying**: Complex searches with JSON-based query syntax
- **Asset Details**: Retrieve complete information about specific assets
- **Real-time Status**: Check connection status and token validity
- **Interactive CLI**: User-friendly command-line interface

### Supported Asset Types
- Emails and templates
- Content blocks and snippets  
- Images (JPG, PNG, GIF)
- Documents (PDF)
- Cloud pages and landing pages
- Folders and categories

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **SFMC Connected App** with the following:
   - Client Credentials OAuth flow enabled
   - Content Builder API permissions
   - Integration user assigned
3. **SFMC Credentials**:
   - Subdomain (e.g., `mc123456789`)
   - Client ID
   - Client Secret

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure SFMC Credentials

Copy the example environment file and add your credentials:

```bash
cp env-example.txt .env
```

Edit `.env` file with your SFMC details:
```bash
SFMC_SUBDOMAIN=your_subdomain_here
SFMC_CLIENT_ID=your_client_id_here
SFMC_CLIENT_SECRET=your_client_secret_here
```

### 3. SFMC Connected App Setup

In Salesforce Marketing Cloud:

1. **Create Connected App**:
   - Go to Setup → Apps → Installed Packages
   - Create new Connected App
   - Enable OAuth 2.0 settings

2. **Configure OAuth Settings**:
   - Grant Type: `Client Credentials`
   - Scope: `email_read`, `email_write`, `offline` (minimum)
   - Integration User: Assign a dedicated integration user

3. **Enable Client Credentials Flow**:
   - Edit the Connected App
   - OAuth Policies → Client Credentials Flow: Enable
   - Run-As User: Select your integration user

## 🎯 Usage

### Starting the Agent

Run the interactive client:

```bash
python sfmc-mcp-client.py
```

### Basic Commands

#### Initialize Connection
```bash
init <subdomain> <client_id> <client_secret>
```
Example:
```bash
init mc123456789 your_client_id your_client_secret
```

#### Search Assets
```bash
search newsletter
# or simply:
newsletter
```

#### Check Status
```bash
status
```

#### Get Asset by ID
```bash
get 12345
```

#### Advanced Search
```bash
advanced {"query": {"property": "name", "simpleOperator": "contains", "value": "welcome"}}
```

#### Show Asset Types Reference
```bash
types
```

#### Help
```bash
help
```

### Advanced Search Examples

#### Search by Asset Type
```json
{
  "query": {
    "property": "assetType.name",
    "simpleOperator": "eq", 
    "value": "email"
  },
  "page": {"page": 1, "pageSize": 25}
}
```

#### Search by Date Range
```json
{
  "query": {
    "property": "modifiedDate",
    "simpleOperator": "gt",
    "value": "2024-01-01"
  },
  "sort": [{"property": "modifiedDate", "direction": "DESC"}]
}
```

#### Complex Multi-Condition Search
```json
{
  "query": {
    "leftOperand": {
      "property": "name",
      "simpleOperator": "contains",
      "value": "newsletter"
    },
    "logicalOperator": "AND",
    "rightOperand": {
      "property": "assetType.name", 
      "simpleOperator": "eq",
      "value": "email"
    }
  }
}
```

## 🏗️ Architecture

### MCP Server (`sfmc-mcp-server.py`)
- **SFMCClient Class**: Handles authentication and API calls
- **FastMCP Tools**: Exposed functions for asset operations
- **Resources**: Static reference data and connection status
- **Error Handling**: Comprehensive error management and logging

### MCP Client (`sfmc-mcp-client.py`) 
- **Interactive CLI**: User-friendly command interface
- **Session Management**: Handles MCP server communication
- **Result Formatting**: Clean display of search results
- **Command Parsing**: Natural language command interpretation

### Key Components

#### Authentication Flow
1. Client credentials sent to SFMC OAuth endpoint
2. Access token received and cached
3. Token automatically refreshed when expired
4. All API calls use Bearer token authentication

#### Asset Search Process
1. User provides search criteria
2. Client calls appropriate MCP server tool
3. Server constructs SFMC API request
4. Results formatted and returned to user
5. Interactive display with pagination support

## 🔧 API Reference

### MCP Tools

#### `initialize_sfmc_connection(subdomain, client_id, client_secret)`
Initialize connection to SFMC instance.

#### `search_sfmc_assets(asset_name, asset_type, page_size, page_number, category_id)`
Search for assets with basic parameters.

#### `advanced_asset_search(query_json)`
Perform complex searches using JSON query syntax.

#### `get_asset_by_id(asset_id)`
Retrieve detailed information about a specific asset.

### MCP Resources

#### `sfmc://connection/status`
Current connection status and authentication info.

#### `sfmc://assets/types`
Reference information about asset types and search operators.

## 🛡️ Security Considerations

1. **Credential Protection**: Store credentials in environment variables
2. **Token Management**: Automatic token refresh with expiry handling  
3. **Error Logging**: Detailed logging without exposing sensitive data
4. **API Rate Limits**: Built-in request management and error handling
5. **Input Validation**: Sanitization of user inputs and search parameters

## 🔍 Troubleshooting

### Common Issues

#### Authentication Failures
- Verify Connected App configuration
- Check client credentials are correct
- Ensure integration user has proper permissions
- Confirm OAuth scopes are sufficient

#### Search Problems
- Validate search syntax
- Check asset permissions for integration user
- Verify category/folder access rights
- Review API rate limits

#### Connection Issues
- Test network connectivity
- Verify SFMC subdomain is correct
- Check firewall/proxy settings
- Validate SSL certificate handling

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export PYTHONPATH="."
export MCP_DEBUG=1
python sfmc-mcp-client.py
```

## 📊 Performance Tips

1. **Pagination**: Use appropriate page sizes (10-50 items)
2. **Filtering**: Apply specific filters to reduce result sets
3. **Caching**: Server caches access tokens automatically
4. **Batch Operations**: Group multiple searches when possible

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built using [FastMCP](https://github.com/jlowin/fastmcp) framework
- Utilizes [Model Context Protocol](https://modelcontextprotocol.io/) specification
- Salesforce Marketing Cloud REST API integration
- Inspired by the Claude Desktop MCP architecture