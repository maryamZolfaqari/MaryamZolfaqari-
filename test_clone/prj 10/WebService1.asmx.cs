using System;
using System.Web.Services;

namespace TriangleService
{
    [WebService(Namespace = "http://example.com/triangle")]
    [WebServiceBinding(ConformsTo = WsiProfiles.BasicProfile1_1)]
    [System.ComponentModel.ToolboxItem(false)]
    public class WebService1 : WebService
    {
        private const double R = 6371000; // شعاع زمین بر حسب متر (WGS84)

        public WebService1() { }

        // تبدیل درجه به رادیان
        private double ToRad(double deg)
        {
            return deg * Math.PI / 180.0;
        }

        // فرمول هاورساین برای فاصله دو نقطه روی زمین
        private double Haversine(double lat1, double lon1, double lat2, double lon2)
        {
            double dLat = ToRad(lat2 - lat1);
            double dLon = ToRad(lon2 - lon1);

            lat1 = ToRad(lat1);
            lat2 = ToRad(lat2);

            double a =
                Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                Math.Cos(lat1) * Math.Cos(lat2) *
                Math.Sin(dLon / 2) * Math.Sin(dLon / 2);

            double c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));

            return R * c; // فاصله بر حسب متر
        }

        // محاسبه محیط مثلث با سه نقطه
        [WebMethod]
        public double GetPerimeter(double lat1, double lon1,
                                   double lat2, double lon2,
                                   double lat3, double lon3)
        {
            double a = Haversine(lat1, lon1, lat2, lon2);
            double b = Haversine(lat2, lon2, lat3, lon3);
            double c = Haversine(lat3, lon3, lat1, lon1);

            return a + b + c;
        }

        // یک متد ساده برای تست
        [WebMethod]
        public string HelloWorld()
        {
            return "Hello World";
        }
    }
}
