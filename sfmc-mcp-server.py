# SFMC MCP Server - Asset Search AI Agent
# This server provides tools to authenticate with SFMC and search for assets

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from fastmcp import FastMCP
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="SFMC Asset Search Agent",
    instructions="AI Agent for Salesforce Marketing Cloud asset search operations using REST API authentication"
)

class SFMCClient:
    """SFMC API Client for authentication and asset operations"""
    
    def __init__(self, subdomain: str, client_id: str, client_secret: str):
        self.subdomain = subdomain
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None
        self.base_url = f"https://{subdomain}.rest.marketingcloudapis.com"
        
    def get_access_token(self) -> Dict[str, Any]:
        """
        Authenticate with SFMC using OAuth 2.0 Client Credentials Flow
        Returns access token for API calls
        """
        try:
            # Check if we have a valid token
            if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
                return {"success": True, "token": self.access_token}
            
            # Authentication endpoint
            auth_url = f"https://{self.subdomain}.auth.marketingcloudapis.com/v2/token"
            
            # Prepare authentication request
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.info(f"Authenticating with SFMC at {auth_url}")
            
            # Make authentication request
            response = requests.post(auth_url, json=auth_data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store token and expiry
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)  # 60 sec buffer
            
            logger.info("Successfully authenticated with SFMC")
            
            return {
                "success": True,
                "token": self.access_token,
                "expires_in": expires_in,
                "token_type": token_data.get("token_type", "Bearer")
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Authentication failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected authentication error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def search_assets(self, search_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search for assets using SFMC Content Builder API
        Supports both simple and advanced query parameters
        """
        try:
            # Ensure we have a valid token
            token_result = self.get_access_token()
            if not token_result["success"]:
                return token_result
            
            # Prepare search endpoint
            search_url = f"{self.base_url}/asset/v1/content/assets"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Default search parameters
            default_params = {
                "$pagesize": 50,
                "$page": 1,
                "$orderBy": "modifiedDate desc"
            }
            
            # Merge with provided parameters
            if search_params:
                default_params.update(search_params)
            
            logger.info(f"Searching assets with params: {default_params}")
            
            # Make search request
            response = requests.get(search_url, headers=headers, params=default_params)
            response.raise_for_status()
            
            search_results = response.json()
            
            logger.info(f"Found {search_results.get('count', 0)} total assets")
            
            return {
                "success": True,
                "results": search_results,
                "total_count": search_results.get("count", 0),
                "page_size": search_results.get("pageSize", 50),
                "page": search_results.get("page", 1)
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Asset search failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected search error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def advanced_asset_search(self, query_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform advanced asset search using POST query endpoint
        Allows complex filtering and sorting options
        """
        try:
            # Ensure we have a valid token
            token_result = self.get_access_token()
            if not token_result["success"]:
                return token_result
            
            # Advanced search endpoint
            search_url = f"{self.base_url}/asset/v1/content/assets/query"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Default query structure
            default_query = {
                "page": {
                    "page": 1,
                    "pageSize": 50
                },
                "query": {
                    "property": "name",
                    "simpleOperator": "contains",
                    "value": ""
                },
                "sort": [
                    {
                        "property": "modifiedDate",
                        "direction": "DESC"
                    }
                ]
            }
            
            # Merge with provided query
            if query_body:
                default_query.update(query_body)
            
            logger.info(f"Advanced search with query: {json.dumps(default_query, indent=2)}")
            
            # Make advanced search request
            response = requests.post(search_url, headers=headers, json=default_query)
            response.raise_for_status()
            
            search_results = response.json()
            
            logger.info(f"Advanced search found {search_results.get('count', 0)} total assets")
            
            return {
                "success": True,
                "results": search_results,
                "total_count": search_results.get("count", 0),
                "page_size": search_results.get("pageSize", 50),
                "page": search_results.get("page", 1),
                "query_used": default_query
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Advanced asset search failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected advanced search error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

# Global SFMC client instance
sfmc_client = None

@mcp.tool()
def initialize_sfmc_connection(subdomain: str, client_id: str, client_secret: str) -> str:
    """
    Initialize connection to Salesforce Marketing Cloud
    
    Args:
        subdomain: Your SFMC subdomain (e.g., 'mc123456789')
        client_id: Connected app client ID
        client_secret: Connected app client secret
        
    Returns:
        Status message indicating success or failure
    """
    global sfmc_client
    
    try:
        # Create SFMC client instance
        sfmc_client = SFMCClient(subdomain, client_id, client_secret)
        
        # Test authentication
        auth_result = sfmc_client.get_access_token()
        
        if auth_result["success"]:
            return f"✅ Successfully connected to SFMC instance: {subdomain}"
        else:
            return f"❌ Authentication failed: {auth_result['error']}"
            
    except Exception as e:
        return f"❌ Connection initialization failed: {str(e)}"

@mcp.tool()
def search_sfmc_assets(
    asset_name: str = "", 
    asset_type: str = "", 
    page_size: int = 50,
    page_number: int = 1,
    category_id: Optional[int] = None
) -> str:
    """
    Search for assets in Salesforce Marketing Cloud Content Builder
    
    Args:
        asset_name: Name or partial name to search for (optional)
        asset_type: Type of asset (e.g., 'email', 'image', 'template') (optional) 
        page_size: Number of results per page (1-50, default: 50)
        page_number: Page number to retrieve (default: 1)
        category_id: Category/folder ID to search within (optional)
        
    Returns:
        JSON string with search results and asset details
    """
    global sfmc_client
    
    if not sfmc_client:
        return "❌ SFMC connection not initialized. Please call initialize_sfmc_connection first."
    
    try:
        # Build search parameters
        search_params = {
            "$pagesize": min(max(page_size, 1), 50),  # Ensure valid page size
            "$page": max(page_number, 1)  # Ensure valid page number
        }
        
        # Add filters if provided
        filters = []
        
        if asset_name:
            filters.append(f"name like '{asset_name}'")
            
        if asset_type:
            filters.append(f"assetType.name eq '{asset_type}'")
            
        if category_id:
            filters.append(f"category.id eq {category_id}")
        
        if filters:
            search_params["$filter"] = " and ".join(filters)
        
        # Perform search
        result = sfmc_client.search_assets(search_params)
        
        if result["success"]:
            # Format results for better readability
            assets = result["results"].get("items", [])
            formatted_results = {
                "search_summary": {
                    "total_found": result["total_count"],
                    "page": result["page"],
                    "page_size": result["page_size"],
                    "total_pages": (result["total_count"] + result["page_size"] - 1) // result["page_size"]
                },
                "assets": []
            }
            
            for asset in assets:
                asset_info = {
                    "id": asset.get("id"),
                    "name": asset.get("name"),
                    "asset_type": asset.get("assetType", {}).get("name"),
                    "created_date": asset.get("createdDate"),
                    "modified_date": asset.get("modifiedDate"),
                    "created_by": asset.get("createdBy", {}).get("name"),
                    "modified_by": asset.get("modifiedBy", {}).get("name"),
                    "category": asset.get("category", {}).get("name"),
                    "status": asset.get("status", {}).get("name"),
                    "file_size": asset.get("fileProperties", {}).get("fileSize")
                }
                formatted_results["assets"].append(asset_info)
            
            return json.dumps(formatted_results, indent=2)
            
        else:
            return f"❌ Search failed: {result['error']}"
            
    except Exception as e:
        return f"❌ Asset search error: {str(e)}"

@mcp.tool()
def advanced_asset_search(query_json: str) -> str:
    """
    Perform advanced asset search with complex filtering using JSON query
    
    Args:
        query_json: JSON string containing advanced query parameters
        Example: {
            "query": {
                "property": "name",
                "simpleOperator": "contains", 
                "value": "newsletter"
            },
            "page": {"page": 1, "pageSize": 25},
            "sort": [{"property": "modifiedDate", "direction": "DESC"}]
        }
        
    Returns:
        JSON string with detailed search results
    """
    global sfmc_client
    
    if not sfmc_client:
        return "❌ SFMC connection not initialized. Please call initialize_sfmc_connection first."
    
    try:
        # Parse query JSON
        query_body = json.loads(query_json)
        
        # Perform advanced search
        result = sfmc_client.advanced_asset_search(query_body)
        
        if result["success"]:
            return json.dumps(result, indent=2)
        else:
            return f"❌ Advanced search failed: {result['error']}"
            
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON query: {str(e)}"
    except Exception as e:
        return f"❌ Advanced search error: {str(e)}"

@mcp.tool()
def get_asset_by_id(asset_id: str) -> str:
    """
    Retrieve detailed information about a specific asset by ID
    
    Args:
        asset_id: The unique identifier of the asset
        
    Returns:
        JSON string with complete asset details
    """
    global sfmc_client
    
    if not sfmc_client:
        return "❌ SFMC connection not initialized. Please call initialize_sfmc_connection first."
    
    try:
        # Ensure we have a valid token
        token_result = sfmc_client.get_access_token()
        if not token_result["success"]:
            return f"❌ Authentication failed: {token_result['error']}"
        
        # Get asset details endpoint
        asset_url = f"{sfmc_client.base_url}/asset/v1/content/assets/{asset_id}"
        
        headers = {
            "Authorization": f"Bearer {sfmc_client.access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Retrieving asset details for ID: {asset_id}")
        
        # Make request
        response = requests.get(asset_url, headers=headers)
        response.raise_for_status()
        
        asset_data = response.json()
        
        return json.dumps(asset_data, indent=2)
        
    except requests.exceptions.RequestException as e:
        return f"❌ Failed to retrieve asset: {str(e)}"
    except Exception as e:
        return f"❌ Asset retrieval error: {str(e)}"

@mcp.resource("sfmc://connection/status")
def connection_status() -> str:
    """Provides current SFMC connection status and authentication info"""
    global sfmc_client
    
    if not sfmc_client:
        return "❌ No SFMC connection established"
    
    try:
        # Check token status
        token_result = sfmc_client.get_access_token()
        
        if token_result["success"]:
            status_info = {
                "connection_status": "✅ Connected",
                "subdomain": sfmc_client.subdomain,
                "base_url": sfmc_client.base_url,
                "token_valid": True,
                "token_expiry": sfmc_client.token_expiry.isoformat() if sfmc_client.token_expiry else None
            }
        else:
            status_info = {
                "connection_status": "❌ Authentication Failed",
                "subdomain": sfmc_client.subdomain,
                "base_url": sfmc_client.base_url,
                "token_valid": False,
                "error": token_result.get("error")
            }
        
        return json.dumps(status_info, indent=2)
        
    except Exception as e:
        return f"❌ Status check failed: {str(e)}"

@mcp.resource("sfmc://assets/types")
def asset_types_reference() -> str:
    """Provides reference information about SFMC asset types"""
    
    asset_types = {
        "common_asset_types": {
            "email": "Email messages and templates",
            "template": "Content templates and layouts", 
            "block": "Content blocks and snippets",
            "image": "Image files (JPG, PNG, GIF)",
            "document": "PDF and document files",
            "cloudpage": "Cloud pages and landing pages",
            "folder": "Folder/category containers"
        },
        "search_operators": {
            "eq": "Equals (exact match)",
            "neq": "Not equal to", 
            "contains": "Contains substring",
            "like": "Pattern matching with wildcards",
            "gt": "Greater than (numbers/dates)",
            "lt": "Less than (numbers/dates)",
            "gte": "Greater than or equal",
            "lte": "Less than or equal"
        },
        "example_searches": {
            "by_name": "$filter=name like 'newsletter'",
            "by_type": "$filter=assetType.name eq 'email'",
            "by_date": "$filter=modifiedDate gt '2024-01-01'",
            "combined": "$filter=name like 'welcome' and assetType.name eq 'email'"
        }
    }
    
    return json.dumps(asset_types, indent=2)

# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()