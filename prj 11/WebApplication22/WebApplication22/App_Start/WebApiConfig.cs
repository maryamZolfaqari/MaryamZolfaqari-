using System.Web.Http;

namespace WebApplication22
{
    public static class WebApiConfig
    {
        public static void Register(HttpConfiguration config)
        {
            // 🔹 حتما فعال باشد
            config.MapHttpAttributeRoutes();

            // مسیر پیش‌فرض
            config.Routes.MapHttpRoute(
                name: "DefaultApi",
                routeTemplate: "api/{controller}/{id}",
                defaults: new { id = RouteParameter.Optional }
            );
        }
    }
}
