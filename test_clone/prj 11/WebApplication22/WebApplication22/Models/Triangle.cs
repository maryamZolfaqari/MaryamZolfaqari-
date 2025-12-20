using System;

namespace WebApplication22.Models
{
    public class Point
    {
        public double X { get; set; }
        public double Y { get; set; }
    }

    public class Triangle
    {
        public int Id { get; set; }
        public Point P1 { get; set; }
        public Point P2 { get; set; }
        public Point P3 { get; set; }

        // طول اضلاع
        public double SideA => Math.Sqrt(Math.Pow(P2.X - P1.X, 2) + Math.Pow(P2.Y - P1.Y, 2));
        public double SideB => Math.Sqrt(Math.Pow(P3.X - P2.X, 2) + Math.Pow(P3.Y - P2.Y, 2));
        public double SideC => Math.Sqrt(Math.Pow(P1.X - P3.X, 2) + Math.Pow(P1.Y - P3.Y, 2));

        // محیط
        public double Perimeter => SideA + SideB + SideC;

        // مساحت با فرمول مختصات
        public double Area => Math.Abs((P1.X * (P2.Y - P3.Y) + P2.X * (P3.Y - P1.Y) + P3.X * (P1.Y - P2.Y)) / 2.0);
    }
}
