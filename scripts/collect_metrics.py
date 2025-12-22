#!/usr/bin/env python3
"""
Collect metrics dari MikroTik router
Untuk monitoring dan dashboard
"""

import os
import json
import routeros_api
from datetime import datetime

def collect_metrics():
    """Kumpulkan metrics dari router"""
    
    config = {
        'host': os.getenv('MIKROTIK_HOST'),
        'username': os.getenv('MIKROTIK_USER'),
        'password': os.getenv('MIKROTIK_PASS'),
        'port': int(os.getenv('MIKROTIK_PORT', 8728)),
        'plaintext_login': True,
        'timeout': 10
    }
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": "github-actions",
        "router": config['host'],
        "data": {}
    }
    
    try:
        api = routeros_api.connect(**config)
        
        # 1. System Resources
        print("Collecting system resources...")
        resource = api.get_resource('/system/resource').get()[0]
        metrics['data']['system'] = {
            "cpu_load": float(resource.get('cpu-load', 0)),
            "free_memory": int(resource.get('free-memory', 0)),
            "total_memory": int(resource.get('total-memory', 0)),
            "free_hdd": int(resource.get('free-hdd-space', 0)),
            "total_hdd": int(resource.get('total-hdd-space', 0)),
            "uptime": resource.get('uptime', '0s'),
            "version": resource.get('version', 'unknown'),
            "board_name": resource.get('board-name', 'unknown')
        }
        
        # 2. Interfaces traffic
        print("Collecting interface statistics...")
        interfaces = api.get_resource('/interface').get()
        metrics['data']['interfaces'] = []
        
        for iface in interfaces:
            if iface.get('type') not in ['bridge', 'vlan', 'ppp']:
                metrics['data']['interfaces'].append({
                    "name": iface.get('name'),
                    "type": iface.get('type'),
                    "rx_bytes": int(iface.get('rx-byte', 0)),
                    "tx_bytes": int(iface.get('tx-byte', 0)),
                    "status": iface.get('running', 'false') == 'true'
                })
        
        # 3. Active connections
        print("Collecting connection data...")
        connections = api.get_resource('/ip/firewall/connection').get()
        metrics['data']['connections'] = {
            "total": len(connections),
            "tcp": len([c for c in connections if c.get('protocol') == 'tcp']),
            "udp": len([c for c in connections if c.get('protocol') == 'udp'])
        }
        
        # 4. DHCP leases (if available)
        try:
            dhcp_leases = api.get_resource('/ip/dhcp-server/lease').get()
            metrics['data']['dhcp'] = {
                "total_leases": len(dhcp_leases),
                "active_leases": len([l for l in dhcp_leases if l.get('status') == 'bound'])
            }
        except:
            metrics['data']['dhcp'] = {"error": "Not available"}
        
        api.disconnect()
        
        # Save to file
        os.makedirs('data', exist_ok=True)
        filename = f"data/metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"✅ Metrics saved to {filename}")
        print(f"📊 System CPU: {metrics['data']['system']['cpu_load']}%")
        print(f"📊 Active connections: {metrics['data']['connections']['total']}")
        print(f"📊 Interfaces: {len(metrics['data']['interfaces'])}")
        
    except Exception as e:
        print(f"❌ Error collecting metrics: {e}")
        raise

if __name__ == "__main__":
    collect_metrics()
