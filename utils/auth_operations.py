import os
import json
import re
from utils.common.cli_utils import http_get, http_post
from utils.common.cli_utils import get_auth_config


def handle_auth_operations(args):
    """Handle authentication operations."""
    server_url, base_url, token, reorc_mcp_server, mcp_servers_config = get_auth_config()
    if not server_url:
        return None
    
    if args.command == "validate":
        # Call the server to validate token
        validate_url = f"{base_url}/mcp/auth/validate-token?access_token={token}"
        
        try:
            response = http_get(validate_url)
            if response.get("valid"):
                print("Token validation successful")
                return True
            else:
                print("Token validation failed")
                return False
        except Exception as e:
            print(f"Token validation failed: {str(e)}")
            return False
    
    elif args.command == "login":
        # Login to get a new token
        login_url = f"{base_url}/mcp/auth/login"

        print(f"login_url: {login_url}")
        
        # Use provided credentials or default credentials from config
        auth_config = reorc_mcp_server.get("auth", None)
        if not auth_config:
            # check in mcp_servers_config for backward compatibility
            auth_config = mcp_servers_config.get("auth", {})

        if not auth_config:
            print("Error: No auth configuration found in MCP server URL")
            return False
        
        default_credentials = auth_config.get("defaultCredentials", {})
        if not default_credentials:
            print("Error: No default credentials found in auth configuration")
            return False
        
        email = args.email or default_credentials.get("email") or input("Email: ")
        password = args.password or default_credentials.get("password") or input("Password: ")
        tenant = args.tenant or default_credentials.get("tenant_domain") or input("Tenant domain: ")
        
        # Check for placeholder password to prevent account lockout
        if password == "{YOUR_REORC_PASSWORD}":
            print("Error: Please update your password in the MCP configuration file.")
            print("The placeholder password '{YOUR_REORC_PASSWORD}' cannot be used for login.")
            print("Update your .cursor/mcp.json file with your actual ReORC password to prevent account lockout.")
            return False
        
        payload = {
            "email": email,
            "password": password,
            "tenant_domain": tenant
        }
        
        try:
            response = http_post(login_url, payload)
            if "access_token" in response:
                new_token = response["access_token"]
                
                # Update token in server URL
                new_url = re.sub(r"access_token=[^&]+", f"access_token={new_token}", server_url)
                reorc_mcp_server["url"] = new_url
                
                # Save updated config
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cursor", "mcp.json")
                with open(config_path, "w") as f:
                    json.dump(mcp_servers_config, f, indent=2)
                
                print("Login successful, token updated")
                return True
            else:
                # Handle specific error responses
                error_detail = response.get('detail', 'Unknown error')
                error_code = response.get('code')
                
                # Check for account locked errors
                if error_code == "ACCOUNT_LOCKED" or "locked" in str(error_detail).lower():
                    print("❌ ACCOUNT LOCKED: Your ReORC account has been locked due to multiple failed login attempts.")
                    print("Please contact your system administrator to unlock your account.")
                    print("Do not attempt to login again until your account is unlocked to prevent further lockout.")
                elif "invalid credentials" in str(error_detail).lower() or "authentication failed" in str(error_detail).lower():
                    print("❌ LOGIN FAILED: Invalid email, password, or tenant domain.")
                    print("Please verify your credentials in the MCP configuration file (.cursor/mcp.json).")
                    print("Multiple failed attempts may result in account lockout.")
                else:
                    print(f"❌ LOGIN FAILED: {error_detail}")
                
                return False
        except Exception as e:
            error_message = str(e)
            
            # Check if the exception contains account locked information
            if "locked" in error_message.lower() or "ACCOUNT_LOCKED" in error_message:
                print("❌ ACCOUNT LOCKED: Your ReORC account has been locked due to multiple failed login attempts.")
                print("Please contact your system administrator to unlock your account.")
                print("Do not attempt to login again until your account is unlocked.")
            else:
                print(f"❌ LOGIN FAILED: Network or server error occurred: {error_message}")
                print("Please check your network connection and server availability.")
            
            return False
    
    else:
        print(f"Unknown command: {args.command}")
        return False 