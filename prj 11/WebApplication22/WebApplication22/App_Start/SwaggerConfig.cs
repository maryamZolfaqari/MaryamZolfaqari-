using System.Web.Http;
using WebActivatorEx;
using Swashbuckle.Application;

[assembly: PreApplicationStartMethod(typeof(WebApplication22.App_Start.SwaggerConfig), "Register")]

namespace WebApplication22.App_Start
{
    public class SwaggerConfig
    {
        public static void Register()
        {
            GlobalConfiguration.Configuration
                .EnableSwagger(c =>
                {
                    c.SingleApiVersion("v1", "Triangle API");
                })
                .EnableSwaggerUi();
        }
    }
}
