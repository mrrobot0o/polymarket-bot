#!/usr/bin/env python3
"""
Balance Checker - التحقق من رصيد المحفظة
"""

import httpx

def get_balance(address: str):
    """التحقق من رصيد المحفظة"""
    
    # MATIC Balance
    try:
        resp = httpx.get(
            "https://polygon.blockscout.com/api",
            params={
                "module": "account",
                "action": "balance",
                "address": address
            },
            timeout=10
        )
        data = resp.json()
        if data.get('status') == '1':
            matic = int(data['result']) / 10**18
        else:
            matic = 0
    except:
        matic = 0
    
    # USDC Balance
    try:
        resp = httpx.get(
            "https://polygon.blockscout.com/api",
            params={
                "module": "account",
                "action": "tokenlist",
                "address": address
            },
            timeout=10
        )
        data = resp.json()
        usdc = 0
        if data.get('status') == '1':
            for token in data.get('result', []):
                if token.get('symbol') == 'USDC':
                    usdc = int(token['balance']) / 10**6
                    break
    except:
        usdc = 0
    
    return {
        'matic': matic,
        'usdc': usdc
    }

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from eth_account import Account
    
    load_dotenv()
    
    private_key = os.getenv('POLYGON_WALLET_PRIVATE_KEY', '')
    if not private_key:
        print("❌ No private key found in .env")
        exit(1)
    
    account = Account.from_key(private_key)
    address = account.address
    
    print("=" * 50)
    print("💰 رصيد المحفظة")
    print("=" * 50)
    print(f"📍 العنوان: {address}")
    
    balance = get_balance(address)
    
    print(f"💵 USDC: ${balance['usdc']:.2f}")
    print(f"⛽ MATIC: {balance['matic']:.4f}")
    print("=" * 50)
    
    if balance['usdc'] < 10:
        print("⚠️ USDC منخفض! أرسل المزيد للتداول.")
    if balance['matic'] < 0.1:
        print("⚠️ MATIC منخفض! أرسل المزيد للـ gas fees.")
