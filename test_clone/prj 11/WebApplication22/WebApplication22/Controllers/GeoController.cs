using System.Collections.Generic;
using System.Web.Http;
using WebApplication22.Models;

namespace WebApplication22.Controllers
{
    public class GeoController : ApiController
    {
        // --- GET: همه مثلث‌ها ---
        [HttpGet]
        [Route("api/geo")]
        public IEnumerable<Triangle> GetAll() => TriangleData.GetAll();

        // --- GET: مثلث با شناسه مشخص ---
        [HttpGet]
        [Route("api/geo/{id:int}")]
        public IHttpActionResult GetById(int id)
        {
            var t = TriangleData.GetById(id);
            if (t == null) return NotFound();
            return Ok(t);
        }

        // --- GET: مساحت ---
        [HttpGet]
        [Route("api/geo/{id:int}/area")]
        public IHttpActionResult GetArea(int id)
        {
            var t = TriangleData.GetById(id);
            if (t == null) return NotFound();
            return Ok(TriangleCalculations.GetArea(t));
        }

        // --- GET: محیط ---
        [HttpGet]
        [Route("api/geo/{id:int}/perimeter")]
        public IHttpActionResult GetPerimeter(int id)
        {
            var t = TriangleData.GetById(id);
            if (t == null) return NotFound();
            return Ok(TriangleCalculations.GetPerimeter(t));
        }

        // --- POST: ایجاد مثلث جدید ---
        [HttpPost]
        [Route("api/geo")]
        public IHttpActionResult Create([FromBody] Triangle t)
        {
            if (t == null) return BadRequest("Triangle data is required.");
            TriangleData.Add(t);
            return Ok(t);
        }

        // --- PUT: به‌روزرسانی مثلث ---
        [HttpPut]
        [Route("api/geo/{id:int}")]
        public IHttpActionResult Update(int id, [FromBody] Triangle t)
        {
            if (t == null) return BadRequest("Triangle data is required.");
            t.Id = id;
            var updated = TriangleData.Update(t);
            if (!updated) return NotFound();
            return Ok(t);
        }

        // --- DELETE: حذف مثلث ---
        [HttpDelete]
        [Route("api/geo/{id:int}")]
        public IHttpActionResult Delete(int id)
        {
            var deleted = TriangleData.Delete(id);
            if (!deleted) return NotFound();
            return Ok();
        }

        // --- POST جدید برای محاسبه محیط و مساحت از سه نقطه ---
        [HttpPost]
        [Route("api/geo/calculate")]
        public IHttpActionResult Calculate([FromBody] Triangle t)
        {
            if (t == null || t.P1 == null || t.P2 == null || t.P3 == null)
                return BadRequest("Triangle points are required.");

            return Ok(new
            {
                Perimeter = t.Perimeter,
                Area = t.Area
            });
        }
    }
}
