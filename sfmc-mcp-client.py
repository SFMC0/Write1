# SFMC MCP Client - Interactive Asset Search Agent
# This client connects to the SFMC MCP server and provides a chat interface

import asyncio
import json
import os
from typing import Dict, List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class SFMCMCPClient:
    """MCP Client for interacting with SFMC Asset Search Server"""
    
    def __init__(self, server_script_path: str = "sfmc-mcp-server.py"):
        self.server_script_path = server_script_path
        self.session = None
        self.connected = False
        
    async def connect(self):
        """Connect to the MCP server"""
        try:
            # Configure server parameters
            server_params = StdioServerParameters(
                command="python", 
                args=[self.server_script_path]
            )
            
            print("🔌 Connecting to SFMC MCP server...")
            
            # Create client session
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    self.connected = True
                    
                    print("✅ Connected to SFMC MCP server")
                    print("📋 Available tools:")
                    
                    # List available tools
                    tools = await session.list_tools()
                    for tool in tools.tools:
                        print(f"   • {tool.name}: {tool.description}")
                    
                    print("\n📚 Available resources:")
                    
                    # List available resources  
                    resources = await session.list_resources()
                    for resource in resources.resources:
                        print(f"   • {resource.uri}: {resource.name}")
                    
                    # Start interactive session
                    await self.interactive_session(session)
                    
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {str(e)}")
            self.connected = False
    
    async def interactive_session(self, session: ClientSession):
        """Run interactive session with the SFMC MCP server"""
        
        print("\n🚀 SFMC Asset Search Agent Ready!")
        print("Type 'help' for available commands or 'quit' to exit")
        print("=" * 60)
        
        # Track connection state
        sfmc_initialized = False
        
        while True:
            try:
                user_input = input("\n🤖 SFMC Agent> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                    
                if user_input.lower() == 'help':
                    await self.show_help(session)
                    continue
                    
                if user_input.lower() == 'status':
                    await self.check_status(session)
                    continue
                    
                if user_input.lower().startswith('init '):
                    # Initialize SFMC connection
                    # Expected format: init subdomain client_id client_secret
                    parts = user_input.split(' ', 3)
                    if len(parts) == 4:
                        _, subdomain, client_id, client_secret = parts
                        await self.initialize_sfmc(session, subdomain, client_id, client_secret)
                        sfmc_initialized = True
                    else:
                        print("❌ Usage: init <subdomain> <client_id> <client_secret>")
                    continue
                    
                if user_input.lower().startswith('search '):
                    # Search assets
                    if not sfmc_initialized:
                        print("⚠️  Please initialize SFMC connection first using 'init' command")
                        continue
                        
                    search_term = user_input[7:].strip()  # Remove 'search '
                    await self.search_assets(session, search_term)
                    continue
                    
                if user_input.lower().startswith('advanced '):
                    # Advanced search with JSON
                    if not sfmc_initialized:
                        print("⚠️  Please initialize SFMC connection first using 'init' command")
                        continue
                        
                    query_json = user_input[9:].strip()  # Remove 'advanced '
                    await self.advanced_search(session, query_json)
                    continue
                    
                if user_input.lower().startswith('get '):
                    # Get asset by ID
                    if not sfmc_initialized:
                        print("⚠️  Please initialize SFMC connection first using 'init' command")
                        continue
                        
                    asset_id = user_input[4:].strip()  # Remove 'get '
                    await self.get_asset_by_id(session, asset_id)
                    continue
                    
                if user_input.lower() == 'types':
                    # Show asset types reference
                    await self.show_asset_types(session)
                    continue
                
                # If no command matches, treat as general search
                if sfmc_initialized:
                    await self.search_assets(session, user_input)
                else:
                    print("⚠️  Please initialize SFMC connection first using 'init' command")
                    print("💡 Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    async def show_help(self, session: ClientSession):
        """Display help information"""
        help_text = """
📖 SFMC Asset Search Agent - Available Commands:

🔧 Setup Commands:
   init <subdomain> <client_id> <client_secret>  Initialize SFMC connection
   status                                         Check connection status

🔍 Search Commands:  
   search <term>                                  Search assets by name
   <search term>                                  Same as above (direct search)
   advanced <json_query>                          Advanced search with JSON query
   get <asset_id>                                 Get specific asset by ID

📚 Reference Commands:
   types                                          Show asset types and operators
   help                                           Show this help message
   quit/exit/q                                    Exit the application

💡 Examples:
   init mc123456789 your_client_id your_client_secret
   search newsletter
   advanced {"query": {"property": "name", "simpleOperator": "contains", "value": "email"}}
   get 12345
        """
        print(help_text)
    
    async def check_status(self, session: ClientSession):
        """Check SFMC connection status"""
        try:
            result = await session.read_resource("sfmc://connection/status")
            print("📊 Connection Status:")
            print(result.contents[0].text)
        except Exception as e:
            print(f"❌ Failed to check status: {str(e)}")
    
    async def initialize_sfmc(self, session: ClientSession, subdomain: str, client_id: str, client_secret: str):
        """Initialize SFMC connection"""
        try:
            print(f"🔐 Initializing connection to SFMC subdomain: {subdomain}")
            
            result = await session.call_tool(
                "initialize_sfmc_connection",
                {
                    "subdomain": subdomain,
                    "client_id": client_id,
                    "client_secret": client_secret
                }
            )
            
            print(result.content[0].text)
            
        except Exception as e:
            print(f"❌ Failed to initialize SFMC connection: {str(e)}")
    
    async def search_assets(self, session: ClientSession, search_term: str):
        """Search for assets"""
        try:
            print(f"🔍 Searching for assets: '{search_term}'")
            
            result = await session.call_tool(
                "search_sfmc_assets",
                {
                    "asset_name": search_term,
                    "page_size": 20  # Limit for readability
                }
            )
            
            # Parse and display results nicely
            response_text = result.content[0].text
            
            if response_text.startswith('{'):
                # It's JSON, format it nicely
                try:
                    data = json.loads(response_text)
                    self.display_search_results(data)
                except json.JSONDecodeError:
                    print(response_text)
            else:
                print(response_text)
                
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
    
    async def advanced_search(self, session: ClientSession, query_json: str):
        """Perform advanced asset search"""
        try:
            print(f"🔍 Advanced search with query...")
            
            result = await session.call_tool(
                "advanced_asset_search",
                {
                    "query_json": query_json
                }
            )
            
            response_text = result.content[0].text
            
            if response_text.startswith('{'):
                try:
                    data = json.loads(response_text)
                    print("📊 Advanced Search Results:")
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print(response_text)
            else:
                print(response_text)
                
        except Exception as e:
            print(f"❌ Advanced search failed: {str(e)}")
    
    async def get_asset_by_id(self, session: ClientSession, asset_id: str):
        """Get asset details by ID"""
        try:
            print(f"📄 Getting asset details for ID: {asset_id}")
            
            result = await session.call_tool(
                "get_asset_by_id",
                {
                    "asset_id": asset_id
                }
            )
            
            response_text = result.content[0].text
            
            if response_text.startswith('{'):
                try:
                    data = json.loads(response_text)
                    print("📄 Asset Details:")
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print(response_text)
            else:
                print(response_text)
                
        except Exception as e:
            print(f"❌ Failed to get asset: {str(e)}")
    
    async def show_asset_types(self, session: ClientSession):
        """Show asset types reference"""
        try:
            result = await session.read_resource("sfmc://assets/types")
            print("📚 SFMC Asset Types Reference:")
            print(result.contents[0].text)
        except Exception as e:
            print(f"❌ Failed to get asset types: {str(e)}")
    
    def display_search_results(self, data: Dict):
        """Display search results in a formatted way"""
        
        if "search_summary" in data:
            summary = data["search_summary"]
            print(f"\n📊 Search Results Summary:")
            print(f"   Total Found: {summary['total_found']}")
            print(f"   Page: {summary['page']} of {summary['total_pages']}")
            print(f"   Showing: {len(data.get('assets', []))} assets")
            
        if "assets" in data and data["assets"]:
            print(f"\n📁 Assets Found:")
            print("-" * 80)
            
            for i, asset in enumerate(data["assets"], 1):
                print(f"{i:2}. 📄 {asset.get('name', 'Unnamed')}")
                print(f"     ID: {asset.get('id', 'N/A')}")
                print(f"     Type: {asset.get('asset_type', 'Unknown')}")
                print(f"     Modified: {asset.get('modified_date', 'N/A')}")
                if asset.get('created_by'):
                    print(f"     Created by: {asset.get('created_by')}")
                if asset.get('category'):
                    print(f"     Category: {asset.get('category')}")
                print()
        else:
            print("\n📭 No assets found matching your search criteria")

async def main():
    """Main function to run the SFMC MCP client"""
    
    print("🚀 SFMC Asset Search Agent Starting...")
    print("=" * 50)
    
    # Check if server file exists
    server_file = "sfmc-mcp-server.py"
    if not os.path.exists(server_file):
        print(f"❌ Server file '{server_file}' not found!")
        print("Make sure the SFMC MCP server file is in the same directory.")
        return
    
    # Create and connect client
    client = SFMCMCPClient(server_file)
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())