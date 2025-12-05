using System.Collections.Generic;
using System.Linq;

namespace WebApplication22.Models
{
    public static class TriangleData
    {
        private static List<Triangle> triangles = new List<Triangle>();

        public static List<Triangle> GetAll() => triangles;

        public static Triangle GetById(int id) =>
            triangles.FirstOrDefault(t => t.Id == id);

        public static void Add(Triangle t)
        {
            t.Id = triangles.Count > 0 ? triangles.Max(x => x.Id) + 1 : 1;
            triangles.Add(t);
        }

        public static bool Update(Triangle t)
        {
            var existing = GetById(t.Id);
            if (existing == null) return false;

            existing.P1 = t.P1;
            existing.P2 = t.P2;
            existing.P3 = t.P3;

            return true;
        }

        public static bool Delete(int id)
        {
            var t = GetById(id);
            if (t == null) return false;
            triangles.Remove(t);
            return true;
        }
    }
}
