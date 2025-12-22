# soap.py
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from http.server import HTTPServer
import math

# ---------------- Dispatcher ----------------
dispatcher = SoapDispatcher(
    name='TriangleService',
    location='http://127.0.0.1:8000/',
    action='http://127.0.0.1:8000/',
    namespace='http://example.org/triangle',
    trace=True,
    ns=True
)

# ---------------- Functions ----------------
def Perimeter(lat1, lon1, lat2, lon2, lat3, lon3, unit='meters'):
    # تبدیل ورودی‌ها به float
    lat1, lon1 = float(lat1), float(lon1)
    lat2, lon2 = float(lat2), float(lon2)
    lat3, lon3 = float(lat3), float(lon3)
    
    # محاسبه فاصله دو نقطه (Euclidean approximation)
    def distance(x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

    d12 = distance(lat1, lon1, lat2, lon2)
    d23 = distance(lat2, lon2, lat3, lon3)
    d31 = distance(lat3, lon3, lat1, lon1)
    
    perimeter = d12 + d23 + d31

    # اگر خواستیم تبدیل واحد کنیم می‌تونیم بعداً اضافه کنیم
    return perimeter

# ثبت تابع در Dispatcher
dispatcher.register_function(
    name='Perimeter',
    fn=Perimeter,
    returns={'Perimeter': float},
    args={
        'lat1': float, 'lon1': float,
        'lat2': float, 'lon2': float,
        'lat3': float, 'lon3': float,
        'unit': str
    }
)

# ---------------- Request Handler ----------------
class SOAPRequestHandler(SOAPHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        if 'wsdl' in query_params or parsed_path.path == '/':
            wsdl_xml = dispatcher.wsdl()
            self.send_response(200)
            self.send_header('Content-type', 'text/xml; charset=utf-8')
            self.send_header('Content-Length', str(len(wsdl_xml)))
            self.end_headers()
            self.wfile.write(wsdl_xml)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        data_bytes = self.rfile.read(int(self.headers['content-length']))
        data = data_bytes.decode('utf-8')
        response = dispatcher.dispatch(data)
        self.send_response(200)
        self.send_header('Content-type', 'text/xml; charset=utf-8')
        self.end_headers()
        self.wfile.write(response)

# ---------------- Run Server ----------------
if __name__ == '__main__':
    httpd = HTTPServer(('127.0.0.1', 8000), SOAPRequestHandler)
    print("Triangle SOAP service running at http://127.0.0.1:8000/")
    print("For WSDL, go to http://127.0.0.1:8000/?wsdl")
    httpd.serve_forever()
