# SFMC MCP Server - Asset Search AI Agent

import os
import json
import requests
import logging
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError  # <-- ADD THIS
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        try:
            if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
                return {"success": True, "token": self.access_token}
            auth_url = f"https://{self.subdomain}.auth.marketingcloudapis.com/v2/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            headers = {
                "Content-Type": "application/json"
            }
            logger.info(f"Authenticating with SFMC at {auth_url}")
            response = requests.post(auth_url, json=auth_data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
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
        try:
            token_result = self.get_access_token()
            if not token_result["success"]:
                return token_result
            search_url = f"{self.base_url}/asset/v1/content/assets"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            default_params = {
                "$pagesize": 50,
                "$page": 1,
                "$orderBy": "modifiedDate desc"
            }
            if search_params:
                default_params.update(search_params)
            logger.info(f"Searching assets with params: {default_params}")
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
        try:
            token_result = self.get_access_token()
            if not token_result["success"]:
                return token_result
            search_url = f"{self.base_url}/asset/v1/content/assets/query"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            default_query = {
                "page": {"page": 1, "pageSize": 50},
                "query": {"property": "name", "simpleOperator": "contains", "value": ""},
                "sort": [{"property": "modifiedDate", "direction": "DESC"}]
            }
            if query_body:
                default_query.update(query_body)
            logger.info(f"Advanced search with query: {json.dumps(default_query, indent=2)}")
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

sfmc_client = None

@mcp.tool()
def initialize_sfmc_connection(subdomain: str, client_id: str, client_secret: str) -> str:
    global sfmc_client
    try:
        sfmc_client = SFMCClient(subdomain, client_id, client_secret)
        auth_result = sfmc_client.get_access_token()
        if auth_result["success"]:
            return f"✅ Successfully connected to SFMC instance: {subdomain}"
        else:
            raise ToolError(f"❌ Authentication failed: {auth_result['error']}")
    except Exception as e:
        raise ToolError(f"❌ Connection initialization failed: {str(e)}")

@mcp.tool()
def search_sfmc_assets(
    asset_name: str = "",
    asset_type: str = "",
    page_size: int = 50,
    page_number: int = 1,
    category_id: Optional[int] = None
) -> str:
    global sfmc_client
    if not sfmc_client:
        raise ToolError("❌ SFMC connection not initialized. Please call initialize_sfmc_connection first.")
    try:
        search_params = {
            "$pagesize": min(max(page_size, 1), 50),
            "$page": max(page_number, 1)
        }
        filters = []
        if asset_name:
            filters.append(f"name like '{asset_name}'")
        if asset_type:
            filters.append(f"assetType.name eq '{asset_type}'")
        if category_id:
            filters.append(f"category.id eq {category_id}")
        if filters:
            search_params["$filter"] = " and ".join(filters)
        result = sfmc_client.search_assets(search_params)
        if result["success"]:
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
            raise ToolError(f"❌ Search failed: {result['error']}")
    except Exception as e:
        raise ToolError(f"❌ Asset search error: {str(e)}")

@mcp.tool()
def advanced_asset_search(query_json: str) -> str:
    global sfmc_client
    if not sfmc_client:
        raise ToolError("❌ SFMC connection not initialized. Please call initialize_sfmc_connection first.")
    try:
        query_body = json.loads(query_json)
        result = sfmc_client.advanced_asset_search(query_body)
        if result["success"]:
            return json.dumps(result, indent=2)
        else:
            raise ToolError(f"❌ Advanced search failed: {result['error']}")
    except json.JSONDecodeError as e:
        raise ToolError(f"❌ Invalid JSON query: {str(e)}")
    except Exception as e:
        raise ToolError(f"❌ Advanced search error: {str(e)}")

@mcp.tool()
def get_asset_by_id(asset_id: str) -> str:
    global sfmc_client
    if not sfmc_client:
        raise ToolError("❌ SFMC connection not initialized. Please call initialize_sfmc_connection first.")
    try:
        token_result = sfmc_client.get_access_token()
        if not token_result["success"]:
            raise ToolError(f"❌ Authentication failed: {token_result['error']}")
        asset_url = f"{sfmc_client.base_url}/asset/v1/content/assets/{asset_id}"
        headers = {
            "Authorization": f"Bearer {sfmc_client.access_token}",
            "Content-Type": "application/json"
        }
        logger.info(f"Retrieving asset details for ID: {asset_id}")
        response = requests.get(asset_url, headers=headers)
        response.raise_for_status()
        asset_data = response.json()
        return json.dumps(asset_data, indent=2)
    except requests.exceptions.RequestException as e:
        raise ToolError(f"❌ Failed to retrieve asset: {str(e)}")
    except Exception as e:
        raise ToolError(f"❌ Asset retrieval error: {str(e)}")

@mcp.resource("sfmc://connection/status")
def connection_status() -> str:
    global sfmc_client
    if not sfmc_client:
        raise ToolError("❌ No SFMC connection established")
    try:
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
        raise ToolError(f"❌ Status check failed: {str(e)}")

@mcp.resource("sfmc://assets/types")
def asset_types_reference() -> str:
    try:
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
    except Exception as e:
        raise ToolError(f"❌ Asset type reference error: {str(e)}")

if __name__ == "__main__":
    mcp.run()
