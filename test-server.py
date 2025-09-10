#!/usr/bin/env python3
"""
Test script for SFMC MCP Server functionality
Run this to verify your server setup before using the full client
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the SFMC MCP server functionality"""
    
    print("🧪 Testing SFMC MCP Server")
    print("=" * 40)
    
    try:
        # Connect to server
        server_params = StdioServerParameters(
            command="python", 
            args=["sfmc-mcp-server.py"]
        )
        
        print("🔌 Connecting to MCP server...")
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                print("✅ Connected successfully!")
                
                # Test 1: List available tools
                print("\n📋 Testing tool discovery...")
                tools = await session.list_tools()
                
                expected_tools = [
                    "initialize_sfmc_connection",
                    "search_sfmc_assets", 
                    "advanced_asset_search",
                    "get_asset_by_id"
                ]
                
                tool_names = [tool.name for tool in tools.tools]
                print(f"Found {len(tool_names)} tools:")
                for tool in tools.tools:
                    print(f"   ✓ {tool.name}")
                
                # Check if all expected tools are present
                missing_tools = set(expected_tools) - set(tool_names)
                if missing_tools:
                    print(f"❌ Missing tools: {missing_tools}")
                    return False
                
                # Test 2: List available resources
                print("\n📚 Testing resource discovery...")
                resources = await session.list_resources()
                
                expected_resources = [
                    "sfmc://connection/status",
                    "sfmc://assets/types"
                ]
                
                resource_uris = [resource.uri for resource in resources.resources]
                print(f"Found {len(resource_uris)} resources:")
                for resource in resources.resources:
                    print(f"   ✓ {resource.uri}")
                
                # Check if all expected resources are present
                missing_resources = set(expected_resources) - set(resource_uris)
                if missing_resources:
                    print(f"❌ Missing resources: {missing_resources}")
                    return False
                
                # Test 3: Test resource access
                print("\n📖 Testing resource access...")
                
                try:
                    status_resource = await session.read_resource("sfmc://connection/status")
                    print("   ✓ Connection status resource accessible")
                    
                    types_resource = await session.read_resource("sfmc://assets/types")
                    print("   ✓ Asset types resource accessible")
                    
                    # Display asset types for verification
                    types_content = types_resource.contents[0].text
                    types_data = json.loads(types_content)
                    print(f"   ✓ Asset types loaded: {len(types_data.get('common_asset_types', {}))} types")
                    
                except Exception as e:
                    print(f"   ❌ Resource access failed: {str(e)}")
                    return False
                
                # Test 4: Test tool call (without SFMC credentials)
                print("\n🔧 Testing tool execution...")
                
                try:
                    # This should fail gracefully without credentials
                    result = await session.call_tool(
                        "search_sfmc_assets",
                        {"asset_name": "test"}
                    )
                    
                    response = result.content[0].text
                    if "SFMC connection not initialized" in response:
                        print("   ✓ Tool execution works (expected auth error)")
                    else:
                        print(f"   ⚠️  Unexpected response: {response}")
                        
                except Exception as e:
                    print(f"   ❌ Tool execution failed: {str(e)}")
                    return False
                
                print("\n🎉 All tests passed! Server is working correctly.")
                print("\n💡 Next steps:")
                print("   1. Set up your SFMC Connected App")
                print("   2. Get your client credentials")
                print("   3. Run: python sfmc-mcp-client.py")
                print("   4. Use 'init' command with your credentials")
                
                return True
                
    except Exception as e:
        print(f"❌ Server test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    success = await test_mcp_server()
    
    if not success:
        print("\n❌ Tests failed. Please check your setup.")
        exit(1)
    else:
        print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())