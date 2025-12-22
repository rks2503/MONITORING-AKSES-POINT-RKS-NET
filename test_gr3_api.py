#!/usr/bin/env python3
"""
Testing API MikroTik GR3 dengan routeros-api 0.21.0
"""

import routeros_api
import sys

def test_gr3_connection():
    """Test koneksi ke MikroTik GR3"""
    
    print("🔧 Testing MikroTik GR3 API Connection")
    
    # Konfigurasi GR3
    config = {
        'host': '103.59.95.27',      # Ganti dengan IP GR3 Anda
        'username': 'github-monitor', # Ganti dengan username
        'password': 'GitHubPass@123', # GANTI dengan password SEBENARNYA
        'port': 7699,                 # Port API, default 8728
        'plaintext_login': True,      # Jika pakai HTTPS, set False
        'timeout': 10
    }
    
    try:
        # METHOD 1: connect() - Cara paling mudah
        print("\n1. Mencoba connect() method...")
        api = routeros_api.connect(**config)
        print("   ✅ connect() berhasil")
        
        # METHOD 2: RouterOsApiPool - Untuk koneksi persistent
        print("\n2. Mencoba RouterOsApiPool...")
        pool = routeros_api.RouterOsApiPool(
            config['host'],
            config['username'],
            config['password'],
            port=config['port'],
            plaintext_login=config['plaintext_login'],
            timeout=config['timeout']
        )
        api_pool = pool.get_api()
        print("   ✅ RouterOsApiPool berhasil")
        
        # Test koneksi dengan query sederhana
        print("\n3. Testing API queries...")
        
        # A. System Info
        print("   A. System Resource:")
        resource = api.get_resource('/system/resource')
        info = resource.get()
        
        if info:
            print(f"      Board: {info[0].get('board-name', 'Unknown')}")
            print(f"      Model: {info[0].get('model', 'Unknown')}")
            print(f"      Version: {info[0].get('version', 'Unknown')}")
            print(f"      Architecture: {info[0].get('architecture-name', 'Unknown')}")
        
        # B. Identity
        print("   B. System Identity:")
        identity = api.get_resource('/system/identity').get()
        if identity:
            print(f"      Name: {identity[0].get('name', 'Unknown')}")
        
        # C. Interfaces (penting untuk GR3)
        print("   C. Network Interfaces:")
        interfaces = api.get_resource('/interface').get()
        ethernet_count = sum(1 for i in interfaces if i.get('type') == 'ether')
        wireless_count = sum(1 for i in interfaces if i.get('type') == 'wlan')
        print(f"      Total: {len(interfaces)} interfaces")
        print(f"      Ethernet: {ethernet_count}")
        print(f"      Wireless: {wireless_count}")
        
        # D. GR3 Specific: Check CAPsMAN jika ada
        print("   D. Wireless Configuration:")
        try:
            capsman = api.get_resource('/caps-man').get()
            print(f"      CAPsMAN: {'Enabled' if capsman else 'Not configured'}")
        except:
            print("      CAPsMAN: Not available")
        
        # E. Health Check untuk GR3
        print("   E. Health Check:")
        health = api.get_resource('/system/health').get()
        if health:
            print(f"      Temperature: {health[0].get('temperature', 'N/A')}°C")
            print(f"      Voltage: {health[0].get('voltage', 'N/A')}V")
        
        # Tutup koneksi
        api.disconnect()
        pool.disconnect()
        
        print("\n🎉 SEMUA TEST BERHASIL!")
        print("GR3 API berfungsi dengan baik!")
        
        return True
        
    except routeros_api.exceptions.RouterOsApiConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("   Periksa: IP, port, koneksi jaringan, dan API enabled")
        
    except routeros_api.exceptions.RouterOsApiCommunicationError as e:
        print(f"\n❌ Authentication Error: {e}")
        print("   Periksa: Username/password, user permissions")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
    return False

if __name__ == "__main__":
    # Cek versi library
    print(f"📦 routeros-api version: {routeros_api.__version__}")
    
    # Jalankan test
    success = test_gr3_connection()
    
    if not success:
        print("\n🔍 TROUBLESHOOTING GR3:")
        print("   1. Pastikan API aktif di GR3:")
        print("      /ip service set api port=7699")
        print("      /ip service enable api")
        print("   2. Cek user permissions:")
        print("      /user add name=api-user group=full password=123")
        print("   3. Test koneksi manual:")
        print("      telnet 103.59.95.27 7699")
        print("   4. Untuk GR3, port default API: 8728 (HTTP) atau 8729 (HTTPS)")
    
    sys.exit(0 if success else 1)
