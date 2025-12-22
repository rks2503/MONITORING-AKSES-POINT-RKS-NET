#!/usr/bin/env python3
"""
Monitoring script untuk RKS NET
Ambil data dari Netwatch Mikrotik GR3
"""

import json
import os
import sys
from datetime import datetime
import routeros_api
import yaml

# Load konfigurasi
def load_config():
    """Load konfigurasi dari file"""
    with open('config/mikrotik_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_customers():
    """Load data pelanggan"""
    with open('config/customers.json', 'r') as f:
        return json.load(f)

def get_netwatch_status(config):
    """Ambil status dari Netwatch Mikrotik"""
    try:
        mikrotik = config['mikrotik']
        
        # Connect ke Mikrotik
        api = routeros_api.RouterOsApi(
            mikrotik['ip'],
            username=mikrotik['username'],
            password=mikrotik['password'],
            port=mikrotik.get('port', 8728),
            plaintext_login=True,
            use_ssl=False
        )
        
        # Ambil data netwatch
        netwatch = api.get_resource('/tool/netwatch')
        entries = netwatch.get()
        
        # Buat mapping IP -> status
        status_map = {}
        for entry in entries:
            ip = entry.get('host')
            if ip:
                status_map[ip] = {
                    'status': 'UP' if entry.get('status') == 'up' else 'DOWN',
                    'last_down': entry.get('last-down', ''),
                    'last_up': entry.get('last-up', ''),
                    'comment': entry.get('comment', '')
                }
        
        api.disconnect()
        return status_map
        
    except Exception as e:
        print(f"❌ Error connect ke Mikrotik: {e}")
        return {}

def generate_status_data(customers, netwatch_data):
    """Generate data status untuk semua pelanggan"""
    customers_with_status = []
    online_count = 0
    offline_count = 0
    
    for customer in customers:
        ip = customer['ip']
        netwatch_info = netwatch_data.get(ip, {})
        
        status = netwatch_info.get('status', 'UNKNOWN')
        if status == 'UP':
            online_count += 1
        elif status == 'DOWN':
            offline_count += 1
        
        customers_with_status.append({
            'no': customer['no'],
            'name': customer['name'],
            'ip': ip,
            'status': status,
            'comment': netwatch_info.get('comment', ''),
            'last_down': netwatch_info.get('last_down', ''),
            'last_up': netwatch_info.get('last_up', '')
        })
    
    # Urutkan berdasarkan nomor
    customers_with_status.sort(key=lambda x: x['no'])
    
    return {
        'last_updated': datetime.now().isoformat(),
        'customers': customers_with_status,
        'summary': {
            'total_customers': len(customers),
            'online_customers': online_count,
            'offline_customers': offline_count,
            'availability_percent': round((online_count / len(customers)) * 100, 2) if customers else 0
        },
        'system_info': {
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_checked': len(customers)
        }
    }

def save_data(data):
    """Save data ke file JSON"""
    os.makedirs('data', exist_ok=True)
    
    # Save ke data/status.json
    main_file = 'data/status.json'
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Copy ke docs/data/ untuk GitHub Pages
    os.makedirs('docs/data', exist_ok=True)
    docs_file = 'docs/data/status.json'
    with open(docs_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Data saved to {main_file} and {docs_file}")
    
    # Backup dengan timestamp
    backup_dir = 'data/history'
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/status_{timestamp}.json'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return main_file

def main():
    """Main function"""
    print("=" * 60)
    print("RKS NET - Monitoring 74 Pelanggan")
    print("=" * 60)
    
    try:
        # Load config
        config = load_config()
        customers = load_customers()
        
        print(f"📋 Loaded {len(customers)} customers")
        print(f"🔗 Connecting to Mikrotik {config['mikrotik']['ip']}...")
        
        # Get data from Mikrotik
        netwatch_data = get_netwatch_status(config)
        
        if not netwatch_data:
            print("⚠️  No data received from Mikrotik")
            sys.exit(1)
        
        print(f"📊 Got {len(netwatch_data)} entries from Netwatch")
        
        # Generate status data
        data = generate_status_data(customers, netwatch_data)
        
        # Save data
        save_data(data)
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total Pelanggan  : {data['summary']['total_customers']}")
        print(f"Pelanggan Online : {data['summary']['online_customers']}")
        print(f"Pelanggan Offline: {data['summary']['offline_customers']}")
        print(f"Availability     : {data['summary']['availability_percent']}%")
        print(f"Last Updated     : {data['last_updated']}")
        print("=" * 60)
        
        # Show offline customers
        offline = [c for c in data['customers'] if c['status'] == 'DOWN']
        if offline:
            print(f"\n⚠️  OFFLINE CUSTOMERS ({len(offline)}):")
            for cust in offline[:5]:  # Show first 5
                print(f"  {cust['no']:2d}. {cust['name']} ({cust['ip']})")
            if len(offline) > 5:
                print(f"  ... and {len(offline)-5} more")
        
        print("\n✅ Monitoring completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
