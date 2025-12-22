#!/usr/bin/env python3
"""
Simple test untuk API MikroTik di port 7699
"""

import routeros_api
import sys

print("🔧 Testing API on port 7699...")

# Config
config = {
    'host': '103.59.95.27',
    'username': 'github-monitor',
    'password': 'GitHubPass@123',  # PASTIKAN INI BENAR!
    'port': 7699,
    'plaintext_login': True,
    'timeout': 10
}

print(f"Target: {config['host']}:{config['port']}")
print(f"User: {config['username']}")

try:
    # Coba semua method yang mungkin
    print("\nTrying different connection methods...")
    
    # METHOD 1: RouterOsApiPool (new in 0.21.0)
    try:
        print("1. Trying RouterOsApiPool...")
        pool = routeros_api.RouterOsApiPool(
            config['host'],
            config['username'], 
            config['password'],
            port=config['port'],
            plaintext_login=config['plaintext_login'],
            timeout=config['timeout']
        )
        api = pool.get_api()
        print("   ✅ RouterOsApiPool SUCCESS")
        method = "RouterOsApiPool"
    except Exception as e1:
        print(f"   ❌ RouterOsApiPool failed: {type(e1).__name__}")
        
        # METHOD 2: connect() function
        try:
            print("2. Trying connect()...")
            api = routeros_api.connect(**config)
            print("   ✅ connect() SUCCESS")
            method = "connect"
        except Exception as e2:
            print(f"   ❌ connect() failed: {type(e2).__name__}: {e2}")
            raise
    
    # Test basic query
    print(f"\n3. Testing API query (using {method})...")
    
    # A. Get system resource
    print("   A. Getting /system/resource...")
    resource = api.get_resource('/system/resource')
    result = resource.get()
    
    if result:
        data = result[0]
        print(f"      Board: {data.get('board-name', 'N/A')}")
        print(f"      Model: {data.get('model', 'N/A')}")
        print(f"      Version: {data.get('version', 'N/A')}")
        print(f"      CPU Load: {data.get('cpu-load', 'N/A')}%")
    else:
        print("      ❌ No data returned")
    
    # B. Get identity
    print("   B. Getting /system/identity...")
    identity = api.get_resource('/system/identity').get()
    if identity:
        print(f"      Name: {identity[0].get('name', 'N/A')}")
    
    # C. List interfaces
    print("   C. Getting interfaces...")
    interfaces = api.get_resource('/interface').get()
    print(f"      Total interfaces: {len(interfaces)}")
    
    # Show first 3 interfaces
    for i, iface in enumerate(interfaces[:3]):
        print(f"      {i+1}. {iface.get('name')} ({iface.get('type')})")
    
    if len(interfaces) > 3:
        print(f"      ... and {len(interfaces)-3} more")
    
    # Cleanup
    if method == "RouterOsApiPool":
        pool.disconnect()
    else:
        api.disconnect()
    
    print("\n🎉 API TEST SUCCESSFUL!")
    print(f"GR3 API is working on port {config['port']}")
    
except routeros_api.exceptions.RouterOsApiConnectionError as e:
    print(f"\n❌ CONNECTION ERROR: {e}")
    print("   Check: Network connectivity, firewall rules")
    
except routeros_api.exceptions.RouterOsApiCommunicationError as e:
    print(f"\n❌ COMMUNICATION ERROR: {e}")
    print("   Check: Username/password, API permissions")
    
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {type(e).__name__}")
    print(f"   Details: {e}")
    
    # Debug info
    print("\n🔧 DEBUG INFO:")
    print(f"   routeros_api version: {routeros_api.__version__}")
    print(f"   Available attributes: {[x for x in dir(routeros_api) if not x.startswith('_')]}")
