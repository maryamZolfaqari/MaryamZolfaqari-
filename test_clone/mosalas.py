### mrym zolfaqari ###
#wenet

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pyproj import Transformer
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import math
import json
import csv
from datetime import datetime
from matplotlib import animation


# Utilities: geometry & UTM
TRANSFORMER_CACHE = {}

def get_transformer_for_lon(lon):
    zone = int((lon + 180) / 6) + 1
    key = zone
    if key in TRANSFORMER_CACHE:
        return TRANSFORMER_CACHE[key]
    crs_to = f"+proj=utm +zone={zone} +datum=WGS84 +units=m +no_defs"
    transformer = Transformer.from_crs("EPSG:4326", crs_to, always_xy=True)
    TRANSFORMER_CACHE[key] = transformer
    return transformer

def latlon_to_utm(lat, lon):
    t = get_transformer_for_lon(lon)
    x, y = t.transform(lon, lat)
    return (float(x), float(y), int((lon + 180) / 6) + 1)

def area_from_coords(A, B, C):
    area2 = abs(A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1]))
    return area2/2.0

def is_triangle(A, B, C, tol=1e-6):
    return area_from_coords(A, B, C) > tol

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def triangle_perimeter(A, B, C):
    return dist(A, B) + dist(B, C) + dist(C, A)

def triangle_angles(A, B, C):
    a = dist(B, C) 
    b = dist(C, A) 
    c = dist(A, B)  
    def angle_from_sides(opposite, s1, s2):
        denom = 2*s1*s2
        if denom == 0:
            return 0.0
        val = (s1*s2*0 + s1*s2*0)  
        cosv = (s1*s1 + s2*s2 - opposite*opposite) / denom
        cosv = max(-1.0, min(1.0, cosv))
        return math.degrees(math.acos(cosv))
    A_ang = angle_from_sides(a, b, c)
    B_ang = angle_from_sides(b, c, a)
    C_ang = angle_from_sides(c, a, b)
    return (A_ang, B_ang, C_ang)

def triangle_type_by_sides(A, B, C, tol=1e-6):
    a = dist(B, C)
    b = dist(C, A)
    c = dist(A, B)
    sides = [a, b, c]
    eq_ab = abs(a-b) <= tol
    eq_bc = abs(b-c) <= tol
    eq_ca = abs(c-a) <= tol
    if eq_ab and eq_bc:
        return "Equilateral"
    if eq_ab or eq_bc or eq_ca:
        return "Isosceles"
    return "Scalene"

def is_right_triangle(angles, tol_deg=1e-1):
    return any(abs(a-90.0) <= tol_deg for a in angles)


# UI

PLACEHOLDERS = [
    "e.g. 35.6892",
    "e.g. 51.3890"
]

def set_placeholder(entry, text):
    entry.delete(0, tk.END)
    entry.insert(0, text)
    entry.config(fg="#999")

def clear_placeholder(event, placeholder_text):
    w = event.widget
    if w.get() == placeholder_text:
        w.delete(0, tk.END)
        w.config(fg="#111")

def restore_placeholder(event, placeholder_text):
    w = event.widget
    if w.get().strip() == "":
        w.insert(0, placeholder_text)
        w.config(fg="#999")

def validate_number_string(s):
    try:
        v = float(s)
        return True, v
    except Exception:
        return False, None

# Main Application Class
    
class TriangleAnalyzerApp:
    def __init__(self, root):
        self.root = root
        root.title("Triangle Analyzer — WGS84 → UTM")
        root.geometry("1320x780")
        root.minsize(1100, 700)
        self.dark_mode = False
        self._style_colors()
        self._build_ui()
        self.current_utm = None  

    def _style_colors(self):
        self.bg_light = "#f4f7fb"
        self.panel_bg = "#ffffff"
        self.accent = "#2b7cff"   
        self.warn = "#d9534f"
        self.ok = "#28a745"
        self.soft = "#f1f5fb"
        self.text = "#222"

    def _build_ui(self):
        root = self.root
        root.configure(bg=self.bg_light)

        left = tk.Frame(root, bg=self.panel_bg, bd=1, relief="solid")
        left.place(x=18, y=18, width=420, height=744)

        title = tk.Label(left, text="Coordinate Input (WGS84)", font=("Segoe UI", 15, "bold"), bg=self.panel_bg, fg=self.text)
        title.pack(pady=(12,6), anchor="w", padx=12)

        hint = tk.Label(left, text="Enter lat, lon in decimal degrees (e.g. 35.6892, 51.3890).", font=("Segoe UI", 9), bg=self.panel_bg, fg="#666")
        hint.pack(anchor="w", padx=12)

        self.entries = []
        self.entry_error_labels = []

        for i in range(3):
            frame = tk.Frame(left, bg=self.panel_bg)
            frame.pack(padx=12, pady=(10 if i==0 else 6), fill="x")

            lbl = tk.Label(frame, text=f"Point {i+1}", font=("Segoe UI", 11, "bold"), bg=self.panel_bg, fg=self.text)
            lbl.grid(row=0, column=0, sticky="w")

            lat_entry = tk.Entry(frame, width=12, font=("Segoe UI", 11))
            lon_entry = tk.Entry(frame, width=12, font=("Segoe UI", 11))
            lat_entry.grid(row=1, column=0, padx=(0,8), pady=6)
            lon_entry.grid(row=1, column=1, padx=(0,8), pady=6)

            set_placeholder(lat_entry, "Lat " + PLACEHOLDERS[0])
            set_placeholder(lon_entry, "Lon " + PLACEHOLDERS[1])
            lat_entry.bind("<FocusIn>", lambda e, ph="Lat " + PLACEHOLDERS[0]: clear_placeholder(e, ph))
            lon_entry.bind("<FocusIn>", lambda e, ph="Lon " + PLACEHOLDERS[1]: clear_placeholder(e, ph))
            lat_entry.bind("<FocusOut>", lambda e, ph="Lat " + PLACEHOLDERS[0]: restore_placeholder(e, ph))
            lon_entry.bind("<FocusOut>", lambda e, ph="Lon " + PLACEHOLDERS[1]: restore_placeholder(e, ph))

            lat_entry.bind("<KeyRelease>", self._on_input_change)
            lon_entry.bind("<KeyRelease>", self._on_input_change)

            err = tk.Label(left, text="", font=("Segoe UI", 9), fg=self.warn, bg=self.panel_bg)
            err.pack(anchor="w", padx=12)
            self.entries.append((lat_entry, lon_entry))
            self.entry_error_labels.append(err)


        mode_frame = tk.Frame(left, bg=self.panel_bg)
        mode_frame.pack(padx=12, pady=12, fill="x")
        tk.Label(mode_frame, text="Display Mode", font=("Segoe UI", 11, "bold"), bg=self.panel_bg, fg=self.text).pack(anchor="w")
        self.mode_var = tk.StringVar(value="perimeter")
        r1 = ttk.Radiobutton(mode_frame, text="Highlight Perimeter", variable=self.mode_var, value="perimeter")
        r2 = ttk.Radiobutton(mode_frame, text="Fill Area", variable=self.mode_var, value="area")
        r1.pack(anchor="w", pady=4)
        r2.pack(anchor="w", pady=2)


        btns = tk.Frame(left, bg=self.panel_bg)
        btns.pack(padx=12, pady=8, fill="x")
        draw_btn = ttk.Button(btns, text="Draw & Calculate", command=self.on_draw)
        draw_btn.grid(row=0, column=0, padx=4, sticky="w")
        reset_btn = ttk.Button(btns, text="Reset", command=self.on_reset)
        reset_btn.grid(row=0, column=1, padx=4)
        sample_btn = ttk.Button(btns, text="Insert Test Sample", command=self._insert_sample)
        sample_btn.grid(row=0, column=2, padx=4)
        export_btn = ttk.Button(btns, text="Export...", command=self._export_menu)
        export_btn.grid(row=0, column=3, padx=4)

        # Info / results panel
        info = tk.Frame(left, bg="#fbfdff", bd=1, relief="solid")
        info.pack(padx=12, pady=12, fill="both", expand=False)

        self.perim_var = tk.StringVar(value="Perimeter: -")
        self.area_var = tk.StringVar(value="Area: -")
        self.side_vars = [tk.StringVar(value="AB: -"), tk.StringVar(value="BC: -"), tk.StringVar(value="CA: -")]
        self.angle_vars = [tk.StringVar(value="∠A: -"), tk.StringVar(value="∠B: -"), tk.StringVar(value="∠C: -")]
        self.meta_var = tk.StringVar(value="Type: - | Orientation: - | Right-angled: -")

        tk.Label(info, textvariable=self.perim_var, font=("Segoe UI", 11, "bold"), bg="#fbfdff").pack(anchor="w", padx=8, pady=(8,2))
        tk.Label(info, textvariable=self.area_var, font=("Segoe UI", 11, "bold"), bg="#fbfdff").pack(anchor="w", padx=8, pady=(0,6))

        for v in self.side_vars:
            tk.Label(info, textvariable=v, font=("Segoe UI", 10), bg="#fbfdff").pack(anchor="w", padx=8)
        for v in self.angle_vars:
            tk.Label(info, textvariable=v, font=("Segoe UI", 10), bg="#fbfdff").pack(anchor="w", padx=8)

        tk.Label(info, textvariable=self.meta_var, font=("Segoe UI", 10, "italic"), bg="#fbfdff").pack(anchor="w", padx=8, pady=(6,8))


        self.status = tk.Label(left, text="Ready", font=("Segoe UI", 10), bg=self.panel_bg, fg="#333")
        self.status.pack(side="bottom", pady=8, fill="x")

        right = tk.Frame(root, bg="#eef4ff", bd=1, relief="solid")
        right.place(x=456, y=18, width=840, height=744)

        tlabel = tk.Label(right, text="UTM Triangle Preview", font=("Segoe UI", 15, "bold"), bg="#eef4ff")
        tlabel.pack(pady=(12,6), anchor="w", padx=10)


        self.fig = Figure(figsize=(7.8,7.0), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#ffffff")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=6)

        toolbar = NavigationToolbar2Tk(self.canvas, right)
        toolbar.update()
        self.canvas._tkcanvas.pack(fill="both", expand=True)

        dm_frame = tk.Frame(root, bg=self.bg_light)
        dm_frame.place(x=1180, y=12, width=160, height=36)
        self.dark_btn = ttk.Button(dm_frame, text="Toggle Dark Mode", command=self._toggle_dark)
        self.dark_btn.pack(anchor="e", padx=8)


    # Event handlers & logic

    def _insert_sample(self):
        sample = [("35.6892", "51.3890"), ("35.6900", "51.3900"), ("35.6885", "51.3910")]
        for (le, ln), (la, lo) in zip(self.entries, sample):
            le.delete(0, tk.END); le.insert(0, la); le.config(fg="#111")
            ln.delete(0, tk.END); ln.insert(0, lo); ln.config(fg="#111")
        self.status.config(text="Sample coordinates inserted.", fg="#006400")
        self._on_input_change()

    def _on_input_change(self, event=None):
        for i, (lat_e, lon_e) in enumerate(self.entries):
            lat_s = lat_e.get().strip()
            lon_s = lon_e.get().strip()
            err_msg = ""
            valid_lat = False
            valid_lon = False

            if lat_s == "" or lat_s.startswith("Lat "):
                err_msg = "Latitude is empty."
            else:
                ok, v = validate_number_string(lat_s)
                if not ok:
                    err_msg = "Latitude not numeric."
                elif not (-90.0 <= v <= 90.0):
                    err_msg = "Latitude out of range (-90..90)."
                else:
                    valid_lat = True

            if lon_s == "" or lon_s.startswith("Lon "):
                if err_msg == "":
                    err_msg = "Longitude is empty."
                else:
                    err_msg += " Longitude is empty."
            else:
                ok2, w = validate_number_string(lon_s)
                if not ok2:
                    err_msg = (err_msg + " " if err_msg else "") + "Longitude not numeric."
                elif not (-180.0 <= w <= 180.0):
                    err_msg = (err_msg + " " if err_msg else "") + "Longitude out of range (-180..180)."
                else:
                    valid_lon = True

            if valid_lat:
                lat_e.config(bg="#eaffea")
            else:
                lat_e.config(bg="#ffecec")
            if valid_lon:
                lon_e.config(bg="#eaffea")
            else:
                lon_e.config(bg="#ffecec")

            self.entry_error_labels[i].config(text=err_msg)

    def on_draw(self):
        # Clear status
        self.status.config(text="", fg="#333")
        for lbl in self.entry_error_labels:
            lbl.config(text="")

        # Read and validate
        latlon = []
        any_error = False

        for i, (lat_e, lon_e) in enumerate(self.entries):
            lat_s = lat_e.get().strip()
            lon_s = lon_e.get().strip()
            if lat_s == "" or lat_s.startswith("Lat ") or lon_s == "" or lon_s.startswith("Lon "):
                self.entry_error_labels[i].config(text="Point incomplete.")
                any_error = True
                continue
            ok1, latv = validate_number_string(lat_s)
            ok2, lonv = validate_number_string(lon_s)
            if not ok1 or not ok2:
                self.entry_error_labels[i].config(text="Latitude/Longitude must be numeric.")
                any_error = True
                continue
            if not (-90.0 <= latv <= 90.0):
                self.entry_error_labels[i].config(text="Latitude must be between -90 and 90.")
                any_error = True
                continue
            if not (-180.0 <= lonv <= 180.0):
                self.entry_error_labels[i].config(text="Longitude must be between -180 and 180.")
                any_error = True
                continue
            latlon.append((latv, lonv))

        if any_error:
            self.status.config(text="Fix indicated input errors.", fg=self.warn)
            return

        try:
            utm_pts = []
            zones = set()
            for (latv, lonv) in latlon:
                x, y, zone = latlon_to_utm(latv, lonv)
                utm_pts.append((x, y))
                zones.add(zone)
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Error converting to UTM:\n{e}")
            return

        if len(zones) > 1:
            self.status.config(text=f"Warning: Points in multiple UTM zones: {sorted(zones)}. Visualization still shown.", fg="#b06b00")
        else:
            self.status.config(text="Converted to UTM.", fg="#006400")

        A, B, C = utm_pts

        
        min_pair_dist = min(dist(A, B), dist(B, C), dist(C, A))
        if min_pair_dist < 1e-3:  # less than 1 mm
            messagebox.showerror("Degenerate Points", "Some points are extremely close (less than 1 mm). Check inputs.")
            return
        
        max_pair_dist = max(dist(A, B), dist(B, C), dist(C, A))
        if max_pair_dist > 3e6:  # > 3000 km
            if not messagebox.askyesno("Large Distances", f"One edge is > {max_pair_dist/1000:.1f} km. Continue?"):
                return

        
        if not is_triangle(A, B, C):
            messagebox.showerror("Not a Triangle", "These three points are collinear (do not form a valid triangle).")
            # clear plot
            self.ax.clear(); self.ax.grid(True); self.canvas.draw()
            self.perim_var.set("Perimeter: -"); self.area_var.set("Area: -")
            return

        
        per = triangle_perimeter(A, B, C)
        area = area_from_coords(A, B, C)
        sides = [dist(A, B), dist(B, C), dist(C, A)]
        angles = triangle_angles(A, B, C)
        ttype = triangle_type_by_sides(A, B, C)
        right = is_right_triangle(angles)

       
        self.perim_var.set(f"Perimeter: {per:.3f} m ({per/1000:.6f} km)")
        self.area_var.set(f"Area: {area/1e6:.9f} km²")
        self.side_vars[0].set(f"AB: {sides[0]:.3f} m")
        self.side_vars[1].set(f"BC: {sides[1]:.3f} m")
        self.side_vars[2].set(f"CA: {sides[2]:.3f} m")
        self.angle_vars[0].set(f"∠A: {angles[0]:.3f}°")
        self.angle_vars[1].set(f"∠B: {angles[1]:.3f}°")
        self.angle_vars[2].set(f"∠C: {angles[2]:.3f}°")
        orientation = self._orientation_latlon_order(latlon)  # CW/CCW in latlon order
        self.meta_var.set(f"Type: {ttype} | Orientation: {orientation} | Right-angled: {'Yes' if right else 'No'}")

        
        self.current_utm = utm_pts
        self.current_latlon = latlon
        self.current_zones = zones

       
        mode = self.mode_var.get()
        self._animate_and_plot(utm_pts, mode)

    def _orientation_latlon_order(self, latlon):
        # compute signed area on lat/lon to get orientation sign
        A = latlon[0]; B = latlon[1]; C = latlon[2]
        s = (A[0]*(B[1]-C[1]) + B[0]*(C[1]-A[1]) + C[0]*(A[1]-B[1]))/2.0
        return "CCW" if s > 0 else "CW"

    def _animate_and_plot(self, pts, mode):
        self.ax.clear()
        self.ax.grid(True)
        xs = [p[0] for p in pts] + [pts[0][0]]
        ys = [p[1] for p in pts] + [pts[0][1]]

        self.canvas.draw_idle()

       
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        dx = xmax - xmin if xmax!=xmin else 1.0
        dy = ymax - ymin if ymax!=ymin else 1.0
        margin = 0.08
        self.ax.set_xlim(xmin - dx*margin, xmax + dx*margin)
        self.ax.set_ylim(ymin - dy*margin, ymax + dy*margin)
        self.ax.set_aspect("equal", adjustable="datalim")
        self.ax.set_xlabel("Easting (m)")
        self.ax.set_ylabel("Northing (m)")
        self.ax.set_title("UTM Triangle Preview")

        
        if mode == "area":
            self.ax.fill(xs, ys, color="#ff7f50", alpha=0.35, zorder=1)
            self.ax.plot(xs, ys, color="#d75a3a", linewidth=2, zorder=2)
        else:
            self.ax.plot(xs, ys, color=self.accent, linewidth=4, zorder=2)

        for idx, (px, py) in enumerate(pts):
            self.ax.scatter(px, py, s=90, color="#004a99", zorder=3)
            self.ax.text(px, py, f"  {chr(65+idx)}\n  ({px:.2f}, {py:.2f})", fontsize=8, zorder=4)

        self.canvas.draw_idle()


        
        lines = []
        scat = None
        fillpoly = None

        
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        dx = xmax - xmin if xmax!=xmin else 1.0
        dy = ymax - ymin if ymax!=ymin else 1.0
        margin = 0.08
        self.ax.set_xlim(xmin - dx*margin, xmax + dx*margin)
        self.ax.set_ylim(ymin - dy*margin, ymax + dy*margin)
        self.ax.set_aspect("equal", adjustable="datalim")
        self.ax.set_xlabel("Easting (m)")
        self.ax.set_ylabel("Northing (m)")
        self.ax.set_title("UTM Triangle Preview")

        
        scat = self.ax.scatter([], [], s=90, zorder=5)

        
        max_frames = 30
        def init():
            return []

        def animate(fr):
            self.ax.collections = [c for c in self.ax.collections if isinstance(c, type(self.ax.collections[0]))] if self.ax.collections else []
            self.ax.lines = []
            current = int((fr / (max_frames-1)) * 3)  # 0..3 segments
            frac = (fr / (max_frames-1)) * 3 - current
            # plot full segments up to current-1
            drawn_x = []
            drawn_y = []
            # segment drawing with smoothing
            for sidx in range(current):
                drawn_x += [xs[sidx], xs[sidx+1]]
                drawn_y += [ys[sidx], ys[sidx+1]]
            # partial segment
            if current < 3:
                x0, y0 = xs[current], ys[current]
                x1, y1 = xs[current+1], ys[current+1]
                dxs = x1 - x0
                dys = y1 - y0
                drawn_x += [x0, x0 + dxs * frac]
                drawn_y += [y0, y0 + dys * frac]
            # if mode area and fully drawn, fill polygon
            if mode == "area" and fr >= (max_frames-1):
                self.ax.fill(xs, ys, color="#ff7f50", alpha=0.35, zorder=1)
                self.ax.plot(xs, ys, color="#d75a3a", linewidth=2, zorder=2)
                self.ax.scatter(xs[:-1], ys[:-1], s=90, color="#b03a2e", zorder=3)
            elif mode == "perimeter":
                self.ax.plot(drawn_x, drawn_y, color=self.accent, linewidth=4, solid_capstyle="round", zorder=4)
                # draw points always
                self.ax.scatter(xs[:-1], ys[:-1], s=90, color="#004a99", zorder=5)
            else:
                self.ax.plot(drawn_x, drawn_y, color=self.accent, linewidth=3, zorder=4)
            # labels near points
            for idx, (px, py) in enumerate(pts):
                self.ax.text(px, py, f"  {chr(65+idx)}\n  ({px:.2f}, {py:.2f})", fontsize=8, zorder=6)
            return []

        ani = animation.FuncAnimation(self.fig, animate, frames=30, interval=40, blit=False, repeat=False)
        self.canvas.draw_idle()

    def on_reset(self):
        for lat_e, lon_e in self.entries:
            lat_e.delete(0, tk.END)
            set_placeholder(lat_e, "Lat " + PLACEHOLDERS[0])
            lon_e.delete(0, tk.END)
            set_placeholder(lon_e, "Lon " + PLACEHOLDERS[1])
            lat_e.config(bg="white"); lon_e.config(bg="white")
        for lbl in self.entry_error_labels:
            lbl.config(text="")
        self.perim_var.set("Perimeter: -")
        self.area_var.set("Area: -")
        for v in self.side_vars: v.set("AB: -")
        for v in self.angle_vars: v.set("∠A: -")
        self.meta_var.set("Type: - | Orientation: - | Right-angled: -")
        self.status.config(text="Reset.", fg="#333")
        self.ax.clear(); self.ax.grid(True); self.canvas.draw_idle()
        self.current_utm = None

    # -------------------------
    # Exports
    # -------------------------
    def _export_menu(self):
        if not self.current_utm:
            messagebox.showwarning("Nothing to Export", "Compute triangle first (Draw & Calculate) before exporting.")
            return
        # simple dialog using filedialog asks
        menu = tk.Toplevel(self.root)
        menu.title("Export Options")
        menu.geometry("360x220")
        menu.transient(self.root)
        menu.grab_set()

        tk.Label(menu, text="Choose export format:", font=("Segoe UI", 11, "bold")).pack(pady=8)
        tk.Button(menu, text="Export PNG (image)", width=30, command=lambda: [menu.destroy(), self._export_png()]).pack(pady=6)
        tk.Button(menu, text="Export CSV (UTM coords)", width=30, command=lambda: [menu.destroy(), self._export_csv()]).pack(pady=6)
        tk.Button(menu, text="Export GeoJSON", width=30, command=lambda: [menu.destroy(), self._export_geojson()]).pack(pady=6)
        tk.Button(menu, text="Close", width=30, command=menu.destroy).pack(pady=6)

    def _export_png(self):
        fn = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png")], title="Save as PNG")
        if not fn:
            return
        # draw fully (no animation) then save
        # We'll re-draw final state
        pts = self.current_utm
        xs = [p[0] for p in pts] + [pts[0][0]]
        ys = [p[1] for p in pts] + [pts[0][1]]
        mode = self.mode_var.get()
        self.ax.clear(); self.ax.grid(True)
        if mode == "area":
            self.ax.fill(xs, ys, color="#ff7f50", alpha=0.35, zorder=1)
            self.ax.plot(xs, ys, color="#d75a3a", linewidth=2, zorder=2)
        else:
            self.ax.plot(xs, ys, color=self.accent, linewidth=4, zorder=2)
        for idx, (px, py) in enumerate(pts):
            self.ax.text(px, py, f"  {chr(65+idx)}\n  ({px:.2f}, {py:.2f})", fontsize=8, zorder=3)
        self.canvas.draw()
        try:
            self.fig.savefig(fn, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Saved", f"PNG saved to:\n{fn}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _export_csv(self):
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")], title="Save CSV")
        if not fn:
            return
        try:
            with open(fn, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Point", "Lat", "Lon", "UTM_Easting", "UTM_Northing"])
                for idx, ((lat, lon), (x, y)) in enumerate(zip(self.current_latlon, self.current_utm)):
                    writer.writerow([chr(65+idx), f"{lat:.8f}", f"{lon:.8f}", f"{x:.4f}", f"{y:.4f}"])
            messagebox.showinfo("Saved", f"CSV saved to:\n{fn}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _export_geojson(self):
        fn = filedialog.asksaveasfilename(defaultextension=".geojson", filetypes=[("GeoJSON", "*.geojson")], title="Save GeoJSON")
        if not fn:
            return
        try:
            # Create polygon in lon/lat order from original latlon list
            coords = [[lon, lat] for (lat, lon) in self.current_latlon]
            coords.append([self.current_latlon[0][1], self.current_latlon[0][0]])
            feature = {
                "type": "Feature",
                "properties": {
                    "generated_by": "TriangleAnalyzer",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
            fc = {"type": "FeatureCollection", "features": [feature]}
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(fc, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Saved", f"GeoJSON saved to:\n{fn}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    # -------------------------
    # Dark mode toggle (simple)
    # -------------------------
    def _toggle_dark(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.root.configure(bg="#1e1e2f")
            for child in self.root.winfo_children():
                try:
                    child.configure(bg="#2b2b3d")
                except Exception:
                    pass
            self.ax.set_facecolor("#2b2b3d")
            self.accent = "#f0a500"  # خطوط مثلث
            self.canvas.draw_idle()
            self.status.config(text="Dark mode ON", fg="#e0e0e0")
        else:
            self.root.configure(bg=self.bg_light)
            for child in self.root.winfo_children():
                try:
                    child.configure(bg=self.bg_light)
                except Exception:
                    pass
            self.ax.set_facecolor("#ffffff")
            self.accent = "#2b7cff"
            self.canvas.draw_idle()
            self.status.config(text="Dark mode OFF", fg="#333")



def main():
    root = tk.Tk()
    app = TriangleAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()