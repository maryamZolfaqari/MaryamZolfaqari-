# client.py
import requests
import xml.etree.ElementTree as ET

def call_perimeter(lat1, lon1, lat2, lon2, lat3, lon3, unit="meters"):
    """
    فراخوانی وب‌متد Perimeter در SOAP Web Service
    """
    # SOAP Body
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://example.org/triangle">
  <soap:Body>
    <tns:Perimeter>
      <lat1>{lat1}</lat1><lon1>{lon1}</lon1>
      <lat2>{lat2}</lat2><lon2>{lon2}</lon2>
      <lat3>{lat3}</lat3><lon3>{lon3}</lon3>
      <unit>{unit}</unit>
    </tns:Perimeter>
  </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://example.org/triangle/Perimeter"  # اصلاح SOAPAction
    }

    try:
        resp = requests.post("http://127.0.0.1:8000/", data=soap_body.encode("utf-8"), headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error connecting to SOAP service:", e)
        return None

    # parse response XML
    try:
        root = ET.fromstring(resp.content)
        # namespace-aware parsing
        ns = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
              'tns': 'http://example.org/triangle'}
        body = root.find('soap:Body', ns)
        if body is not None:
            result_el = body.find('.//tns:Perimeter', ns)
            if result_el is not None and result_el.text:
                return float(result_el.text.strip())
    except Exception as e:
        print("Failed to parse SOAP response:", e)
        return None

    return None

if __name__ == "__main__":
    print("=== Triangle Perimeter SOAP Client ===")
    
    # گرفتن ورودی از کاربر
    try:
        lat1 = float(input("Enter latitude of point 1: "))
        lon1 = float(input("Enter longitude of point 1: "))
        lat2 = float(input("Enter latitude of point 2: "))
        lon2 = float(input("Enter longitude of point 2: "))
        lat3 = float(input("Enter latitude of point 3: "))
        lon3 = float(input("Enter longitude of point 3: "))
    except ValueError:
        print("Invalid input! Please enter numeric values.")
        exit(1)

    # فراخوانی وب‌متد
    perimeter = call_perimeter(lat1, lon1, lat2, lon2, lat3, lon3)

    if perimeter is not None:
        print(f"\nPerimeter of the triangle: {perimeter:.6f} meters")
    else:
        print("Failed to get perimeter from SOAP service.")
