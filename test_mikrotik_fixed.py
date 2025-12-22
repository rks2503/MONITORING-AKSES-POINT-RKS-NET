#!/usr/bin/env python3
"""
Script untuk testing koneksi ke MikroTik RouterOS API
Usage: python test_mikrotik_fixed.py
"""

import routeros_api
import sys
import os


def test_mikrotik_connection():
    """Test koneksi ke router MikroTik"""
    
    # Ambil password dari environment variable (LEBIH AMAN)
    password = os.getenv('MIKROTIK_PASSWORD', 'GitHubPass@123')
    
    # Konfigurasi router
    config = {
        'host': '103.59.95.27',
        'username': 'github-monitor',
        'password': password,
        'port': 7699,
        'plaintext_login': True,
        'timeout': 10
    }
    
    print("🔧 Testing MikroTik RouterOS API Connection")
    print(f"📡 Host: {config['host']}:{config['port']}")
    print(f"👤 User: {config['username']}")
    
    api = None
    try:
        # METHOD 1: Coba pakai RouterOsApi
        try:
            print("\n🔄 Mencoba RouterOsApi class...")
            api = routeros_api.RouterOsApi(**config)
            method = 'RouterOsApi'
            
        except AttributeError:
            # METHOD 2: Coba pakai connect()
            print("ℹ️  RouterOsApi tidak ditemukan, mencoba connect()...")
            api = routeros_api.connect(**config)
            method = 'connect()'
        
        print(f"✅ Connected menggunakan: {method}")
        
        # Test 1: System Resource
        print("\n📊 Test 1: System Resource")
        resource = api.get_resource('/system/resource')
        info = resource.get()
        
        if info:
            data = info[0]
            print(f"   Board: {data.get('board-name', 'Unknown')}")
            print(f"   Model: {data.get('model', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Uptime: {data.get('uptime', 'Unknown')}")
            print(f"   CPU Load: {data.get('cpu-load', 'Unknown')}%")
            print(f"   Free Memory: {data.get('free-memory', 'Unknown')}")
        else:
            print("   ❌ Tidak ada data resource")
        
        # Test 2: System Identity
        print("\n🆔 Test 2: System Identity")
        identity = api.get_resource('/system/identity').get()
        if identity:
            print(f"   Router Name: {identity[0].get('name', 'Unknown')}")
        
        # Test 3: Interface List (opsional)
        print("\n🌐 Test 3: Interface List")
        interfaces = api.get_resource('/interface').get()
        if interfaces:
            print(f"   Jumlah Interface: {len(interfaces)}")
            for iface in interfaces[:3]:  # Tampilkan 3 pertama
                print(f"   - {iface.get('name', 'Unknown')}: {iface.get('type', 'Unknown')}")
            if len(interfaces) > 3:
                print(f"   ... dan {len(interfaces) - 3} lainnya")
        
        # Test 4: Active Users (opsional)
        print("\n👥 Test 4: Active Users")
        users = api.get_resource('/user/active').get()
        if users:
            print(f"   User Aktif: {len(users)}")
        
        api.disconnect()
        print("\n🎉 SEMUA TEST BERHASIL!")
        return True
        
    except routeros_api.exceptions.RouterOsApiConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("   Periksa: IP, port, firewall, dan koneksi jaringan")
        
    except routeros_api.exceptions.RouterOsApiCommunicationError as e:
        print(f"\n❌ Communication Error: {e}")
        print("   Periksa: Username/password, API access enabled")
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {type(e).__name__}: {e}")
        
    finally:
        if api:
            try:
                api.disconnect()
                print("🔌 Koneksi ditutup")
            except:
                pass
    
    return False


if __name__ == "__main__":
    # Cek dulu module tersedia
    try:
        print(f"📦 routeros_api version check...")
        # Coba beberapa cara cek versi
        version = "unknown"
        try:
            version = routeros_api.__version__
        except AttributeError:
            try:
                import pkg_resources
                version = pkg_resources.get_distribution("routeros-api").version
            except:
                pass
        print(f"   Package version: {version}")
    except ImportError:
        print("❌ Module 'routeros_api' tidak ditemukan!")
        print("   Install dengan: pip install routeros-api")
        sys.exit(1)
    
    # Jalankan test
    success = test_mikrotik_connection()
    
    if not success:
        print("\n🔍 TROUBLESHOOTING:")
        print("   1. Pastikan router menyala dan terkoneksi jaringan")
        print("   2. Pastikan API enabled di router: /ip service set api port=7699")
        print("   3. Pastikan user 'github-monitor' ada dan punya permission")
        print("   4. Test koneksi manual: telnet 103.59.95.27 7699")
        print("   5. Cek firewall/router apakah port 7699 terbuka")
    
    sys.exit(0 if success else 1)
