"""
API Documentation & Testing Script
Test all endpoints and generate sample requests
"""

import requests
import json
from tabulate import tabulate

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_stats():
    """Test stats endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Dashboard Stats")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        print(json.dumps(data, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_categories():
    """Test category analysis endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Category Analysis")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/api/category-analysis")
        data = response.json()
        
        if 'categories' in data:
            table_data = []
            for cat in data['categories']:
                table_data.append([
                    cat['category'],
                    f"₹{cat['total_revenue']:,.2f}",
                    f"₹{cat['avg_order_value']:.2f}",
                    cat['order_count'],
                    f"{cat['return_rate']:.1f}%"
                ])
            
            headers = ['Category', 'Total Revenue', 'Avg Order Value', 'Order Count', 'Return Rate']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_customer_summary():
    """Test customer summary endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Customer Summary")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/api/customer-summary")
        data = response.json()
        
        print(f"\nTotal Customers: {data['total_customers']}")
        print(f"Avg Customer Value: ₹{data['avg_customer_value']:.2f}")
        print(f"Avg Orders/Customer: {data['avg_orders_per_customer']:.2f}")
        
        if 'top_10_customers' in data:
            print("\nTop 10 Customers:")
            table_data = []
            for cust_id, values in list(data['top_10_customers'].items())[:10]:
                table_data.append([
                    f"#{cust_id}",
                    f"₹{values[0]:,.2f}",
                    values[1],
                    f"₹{values[2]:.2f}"
                ])
            
            headers = ['Customer ID', 'Total Spend', 'Order Count', 'Avg Order Value']
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_churn_prediction():
    """Test churn prediction endpoint"""
    print("\n" + "="*60)
    print("TEST 5: Churn Prediction")
    print("="*60)
    
    test_cases = [
        {
            "name": "High Risk Customer",
            "data": {
                "total_spend": 300,
                "order_count": 2,
                "days_since_order": 180,
                "return_rate": 0.3,
                "avg_order_value": 150
            }
        },
        {
            "name": "Low Risk Customer",
            "data": {
                "total_spend": 2000,
                "order_count": 15,
                "days_since_order": 10,
                "return_rate": 0.05,
                "avg_order_value": 133
            }
        },
        {
            "name": "Medium Risk Customer",
            "data": {
                "total_spend": 800,
                "order_count": 8,
                "days_since_order": 60,
                "return_rate": 0.10,
                "avg_order_value": 100
            }
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        print(f"\n  {test_case['name']}:")
        try:
            response = requests.post(
                f"{BASE_URL}/api/predict-churn",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"    Churn Probability: {result['churn_probability']*100:.1f}%")
                print(f"    Risk Level: {result['churn_risk']}")
                print(f"    Recommendation: {result['recommendation']}")
            else:
                print(f"    ❌ Error: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"    ❌ Error: {e}")
            all_passed = False
    
    return all_passed

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  E-COMMERCE ANALYTICS API TEST SUITE".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Health Check": test_health(),
        "Dashboard Stats": test_stats(),
        "Category Analysis": test_categories(),
        "Customer Summary": test_customer_summary(),
        "Churn Prediction": test_churn_prediction()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Application is ready for use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs for details.")
    
    return passed == total

if __name__ == "__main__":
    import sys
    
    print("\n⏳ Waiting for application to be ready...")
    print(f"   Connecting to {BASE_URL}...")
    print("\n   Make sure the Flask app is running: python app.py")
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
