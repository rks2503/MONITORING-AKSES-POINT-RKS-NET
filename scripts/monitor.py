#!/usr/bin/env python3
"""
Test koneksi ke MikroTik RouterOS API
Untuk dijalankan di GitHub Actions
"""

import os
import sys
import json
import routeros_api
from datetime import datetime

def test_connection():
    """Test koneksi dan kumpulkan hasil"""
    
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "tests": {},
        "success": False,
        "error": None
    }
    
    # Ambil config dari environment variables
    config = {
        'host': os.getenv('MIKROTIK_HOST'),
        'username': os.getenv('MIKROTIK_USER'),
        'password': os.getenv('MIKROTIK_PASS'),
        'port': int(os.getenv('MIKROTIK_PORT', 8728)),
        'plaintext_login': True,
        'timeout': 15
    }
    
    print(f"🔧 Testing connection to {config['host']}:{config['port']}")
    
    # Validasi config
    for key in ['host', 'username', 'password']:
        if not config[key]:
            results['error'] = f"Missing {key} in environment variables"
            print(f"❌ {results['error']}")
            return results
    
    api = None
    try:
        # Test 1: Basic Connection
        print("1. Testing basic connection...")
        try:
            api = routeros_api.connect(**config)
            results['tests']['basic_connection'] = {
                "status": "passed",
                "method": "connect()"
            }
            print("   ✅ Basic connection successful")
        except Exception as e:
            results['tests']['basic_connection'] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"   ❌ Basic connection failed: {e}")
            return results
        
        # Test 2: API Resource Access
        print("2. Testing API resource access...")
        try:
            resource = api.get_resource('/system/resource')
            info = resource.get()
            if info:
                results['tests']['resource_access'] = {
                    "status": "passed",
                    "data": {
                        "board": info[0].get('board-name'),
                        "model": info[0].get('model'),
                        "version": info[0].get('version'),
                        "uptime": info[0].get('uptime')
                    }
                }
                print(f"   ✅ Resource access successful")
                print(f"   📋 Board: {info[0].get('board-name')}")
                print(f"   🏷️  Version: {info[0].get('version')}")
            else:
                results['tests']['resource_access'] = {
                    "status": "failed",
                    "error": "No data returned"
                }
                print("   ❌ No data returned")
        except Exception as e:
            results['tests']['resource_access'] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"   ❌ Resource access failed: {e}")
        
        # Test 3: Multiple endpoints
        print("3. Testing multiple endpoints...")
        endpoints = ['/system/identity', '/interface', '/ip/address']
        endpoint_results = {}
        
        for endpoint in endpoints:
            try:
                resource = api.get_resource(endpoint)
                data = resource.get()
                endpoint_results[endpoint] = {
                    "status": "passed",
                    "count": len(data) if data else 0
                }
                print(f"   ✅ {endpoint}: {len(data) if data else 0} items")
            except Exception as e:
                endpoint_results[endpoint] = {
                    "status": "failed",
                    "error": str(e)
                }
                print(f"   ❌ {endpoint}: {e}")
        
        results['tests']['endpoints'] = endpoint_results
        
        # Test 4: Performance (response time)
        print("4. Testing response time...")
        import time
        start_time = time.time()
        
        for _ in range(3):
            api.get_resource('/system/resource').get()
        
        response_time = (time.time() - start_time) / 3
        results['tests']['performance'] = {
            "status": "passed",
            "avg_response_time": round(response_time, 3)
        }
        print(f"   ⏱️  Avg response time: {response_time:.3f}s")
        
        # Overall success
        failed_tests = [t for t in results['tests'].values() 
                       if isinstance(t, dict) and t.get('status') == 'failed']
        
        if len(failed_tests) == 0:
            results['success'] = True
            print("\n🎉 ALL TESTS PASSED!")
        else:
            results['success'] = False
            results['error'] = f"{len(failed_tests)} test(s) failed"
            print(f"\n⚠️  {len(failed_tests)} test(s) failed")
        
        return results
        
    except Exception as e:
        results['error'] = str(e)
        print(f"❌ Unexpected error: {e}")
        return results
        
    finally:
        if api:
            try:
                api.disconnect()
                print("🔌 Connection closed")
            except:
                pass

if __name__ == "__main__":
    # Run tests
    test_results = test_connection()
    
    # Save results to file
    os.makedirs('logs', exist_ok=True)
    with open('logs/test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    # Save for GitHub Actions summary
    with open(os.getenv('GITHUB_STEP_SUMMARY', 'test_summary.md'), 'a') as f:
        f.write(f"# MikroTik Connection Test Results\n\n")
        f.write(f"**Timestamp:** {test_results['timestamp']}\n")
        f.write(f"**Status:** {'✅ PASSED' if test_results['success'] else '❌ FAILED'}\n\n")
        
        if test_results.get('tests'):
            f.write("## Test Details\n")
            for test_name, test_result in test_results['tests'].items():
                if isinstance(test_result, dict):
                    status = test_result.get('status', 'unknown')
                    f.write(f"- **{test_name}:** {status.upper()}\n")
    
    # Exit with appropriate code
    sys.exit(0 if test_results['success'] else 1)
