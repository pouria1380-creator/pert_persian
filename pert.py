import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk
import math


FONT_FA = ("B Nazanin", 16)
FONT_FA_BOLD = ("B Nazanin", 16, "bold")


class Node:
    def __init__(self, canvas, x, y, text, node_type="normal"):
        self.canvas = canvas
        self.radius = 40
        self.depth = 10
        self.canvas_items = []
        self.node_type = node_type
        self.create_3d_node(x, y, text)
        self.x = x
        self.y = y
        self.text = text
        self.edges = []
        self.highlight_id = None

    def create_3d_node(self, x, y, text):

        if self.node_type == "start":
            main_color = "#4CAF50"
            outline_color = "#2E7D32"
        elif self.node_type == "end":
            main_color = "#F44336"
            outline_color = "#C62828"
        else:
            main_color = "#FFD700"
            outline_color = "#B8860B"


        shadow = self.canvas.create_oval(
            x - self.radius + self.depth, y - self.radius + self.depth,
            x + self.radius + self.depth, y + self.radius + self.depth,
            fill=outline_color, outline=outline_color, width=0
        )
        self.canvas_items.append(shadow)


        main_circle = self.canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill=main_color, outline=outline_color, width=2
        )
        self.canvas_items.append(main_circle)


        text_id = self.canvas.create_text(
            x, y, text=text,
            font=("B Nazanin", 20, "bold"),
            fill="white"
        )
        self.canvas_items.append(text_id)
        self.text_id = text_id


        self.canvas.tag_raise(main_circle)
        self.canvas.tag_raise(text_id)

    def move(self, new_x, new_y):
        dx = new_x - self.x
        dy = new_y - self.y


        for item in self.canvas_items:
            self.canvas.move(item, dx, dy)

        self.x = new_x
        self.y = new_y


        for edge in self.edges:
            edge.update_position()

    def highlight(self):
        if self.highlight_id is None:
            self.highlight_id = self.canvas.create_oval(
                self.x - self.radius - 5, self.y - self.radius - 5,
                self.x + self.radius + 5, self.y + self.radius + 5,
                outline="#00FF00", width=3, dash=(5, 2)
            )
            self.canvas.tag_raise(self.highlight_id)

            for item in self.canvas_items:
                self.canvas.tag_raise(item)
            self.canvas.tag_raise(self.text_id)

    def remove_highlight(self):
        if self.highlight_id is not None:
            self.canvas.delete(self.highlight_id)
            self.highlight_id = None


class Edge:
    edge_groups = {}

    def __init__(self, canvas, start_node, end_node, days):
        self.canvas = canvas
        self.start_node = start_node
        self.end_node = end_node
        self.days = days
        self.line_id = None
        self.text_id = None
        self.arrow_id = None
        self.curve_points = []


        node_pair = self.get_node_pair(start_node, end_node)
        if node_pair not in Edge.edge_groups:
            Edge.edge_groups[node_pair] = []
        Edge.edge_groups[node_pair].append(self)
        self.edge_index = len(Edge.edge_groups[node_pair]) - 1

        self.draw()

    @staticmethod
    def get_node_pair(node1, node2):
        """Returns a consistent key for a node pair regardless of order"""
        return frozenset({id(node1), id(node2)})

    def calculate_curve_points(self):
        """Calculate points for a curved edge (semi-circle)"""
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            return []


        perp_dx = -dy / distance
        perp_dy = dx / distance


        node_pair = self.get_node_pair(self.start_node, self.end_node)
        total_edges = len(Edge.edge_groups[node_pair])
        max_offset = 100
        curve_height = 40

        if total_edges == 1:

            angle = math.atan2(dy, dx)
            start_x = self.start_node.x + math.cos(angle) * self.start_node.radius
            start_y = self.start_node.y + math.sin(angle) * self.start_node.radius
            end_x = self.end_node.x - math.cos(angle) * self.end_node.radius
            end_y = self.end_node.y - math.sin(angle) * self.end_node.radius
            return [(start_x, start_y), (end_x, end_y)]
        else:

            offset = max_offset * ((self.edge_index + 1) // 2)
            if self.edge_index % 2 == 0:
                offset = -offset


            mid_x = (self.start_node.x + self.end_node.x) / 2
            mid_y = (self.start_node.y + self.end_node.y) / 2


            curve_height = curve_height * (1 + (self.edge_index // 2) * 0.5)


            control_x = mid_x + perp_dx * (offset + curve_height)
            control_y = mid_y + perp_dy * (offset + curve_height)


            angle1 = math.atan2(control_y - self.start_node.y, control_x - self.start_node.x)
            angle2 = math.atan2(self.end_node.y - control_y, self.end_node.x - control_x)

            start_x = self.start_node.x + math.cos(angle1) * self.start_node.radius
            start_y = self.start_node.y + math.sin(angle1) * self.start_node.radius
            end_x = self.end_node.x - math.cos(angle2) * self.end_node.radius
            end_y = self.end_node.y - math.sin(angle2) * self.end_node.radius


            points = []
            steps = 20
            for i in range(steps + 1):
                t = i / steps

                x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x
                y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y
                points.append((x, y))

            return points

    def draw(self):
        self.curve_points = self.calculate_curve_points()

        if len(self.curve_points) < 2:
            return


        self.line_id = self.canvas.create_line(
            *[coord for point in self.curve_points for coord in point],
            width=3, fill="#4169E1", smooth=True
        )


        if len(self.curve_points) >= 2:

            x1, y1 = self.curve_points[-2]
            x2, y2 = self.curve_points[-1]

            arrow_size = 10
            angle = math.atan2(y2 - y1, x2 - x1)


            arrow_x1 = x2 - math.cos(angle) * arrow_size
            arrow_y1 = y2 - math.sin(angle) * arrow_size

            self.arrow_id = self.canvas.create_polygon(
                x2, y2,
                arrow_x1 - math.sin(angle) * arrow_size / 2, arrow_y1 + math.cos(angle) * arrow_size / 2,
                arrow_x1 + math.sin(angle) * arrow_size / 2, arrow_y1 - math.cos(angle) * arrow_size / 2,
                fill="#4169E1", outline="#00008B"
            )


        if len(self.curve_points) >= 2:

            if len(self.curve_points) == 2:
                x1, y1 = self.curve_points[0]
                x2, y2 = self.curve_points[1]
                text_x = (x1 + x2) / 2
                text_y = (y1 + y2) / 2


                dx = x2 - x1
                dy = y2 - y1
                if dx == 0:
                    text_x += 15
                elif dy == 0:
                    text_y += 15
                else:
                    perp_dx = -dy / math.hypot(dx, dy)
                    perp_dy = dx / math.hypot(dx, dy)
                    text_x += perp_dx * 15
                    text_y += perp_dy * 15
            else:
                max_dist = 0
                text_point = self.curve_points[len(self.curve_points) // 2]

                x1, y1 = self.curve_points[0]
                x2, y2 = self.curve_points[-1]

                for point in self.curve_points:
                    px, py = point
                    if x1 == x2:
                        dist = abs(px - x1)
                    elif y1 == y2:
                        dist = abs(py - y1)
                    else:

                        A = y2 - y1
                        B = x1 - x2
                        C = x2 * y1 - x1 * y2
                        dist = abs(A * px + B * py + C) / math.sqrt(A ** 2 + B ** 2)

                    if dist > max_dist:
                        max_dist = dist
                        text_point = point

                text_x, text_y = text_point

            self.text_id = self.canvas.create_text(
                text_x, text_y, text=str(self.days),
                fill="#FF4500", font=("B Nazanin", 16, "bold"),
                activefill="#FF0000"
            )

        self.start_node.edges.append(self)
        self.end_node.edges.append(self)

    def update_position(self):
        self.curve_points = self.calculate_curve_points()

        if len(self.curve_points) < 2:
            return


        self.canvas.coords(self.line_id, *[coord for point in self.curve_points for coord in point])


        if len(self.curve_points) >= 2 and self.arrow_id:
            x1, y1 = self.curve_points[-2]
            x2, y2 = self.curve_points[-1]

            arrow_size = 10
            angle = math.atan2(y2 - y1, x2 - x1)

            arrow_x1 = x2 - math.cos(angle) * arrow_size
            arrow_y1 = y2 - math.sin(angle) * arrow_size

            self.canvas.coords(self.arrow_id,
                               x2, y2,
                               arrow_x1 - math.sin(angle) * arrow_size / 2, arrow_y1 + math.cos(angle) * arrow_size / 2,
                               arrow_x1 + math.sin(angle) * arrow_size / 2, arrow_y1 - math.cos(angle) * arrow_size / 2
                               )


        if len(self.curve_points) >= 2 and self.text_id:

            if len(self.curve_points) == 2:
                x1, y1 = self.curve_points[0]
                x2, y2 = self.curve_points[1]
                text_x = (x1 + x2) / 2
                text_y = (y1 + y2) / 2


                dx = x2 - x1
                dy = y2 - y1
                if dx == 0:
                    text_x += 15
                elif dy == 0:
                    text_y += 15
                else:
                    perp_dx = -dy / math.hypot(dx, dy)
                    perp_dy = dx / math.hypot(dx, dy)
                    text_x += perp_dx * 15
                    text_y += perp_dy * 15
            else:

                max_dist = 0
                text_point = self.curve_points[len(self.curve_points) // 2]

                x1, y1 = self.curve_points[0]
                x2, y2 = self.curve_points[-1]

                for point in self.curve_points:
                    px, py = point
                    if x1 == x2:
                        dist = abs(px - x1)
                    elif y1 == y2:
                        dist = abs(py - y1)
                    else:
                        A = y2 - y1
                        B = x1 - x2
                        C = x2 * y1 - x1 * y2
                        dist = abs(A * px + B * py + C) / math.sqrt(A ** 2 + B ** 2)

                    if dist > max_dist:
                        max_dist = dist
                        text_point = point

                text_x, text_y = text_point

            self.canvas.coords(self.text_id, text_x, text_y)


class PERTApp:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.dragged_node = None
        self.selected_node = None
        self.start_node = None
        self.end_node = None

        self.root = ctk.CTk()
        self.root.title("سازنده نمودار پرت")
        self.root.geometry("800x700")
        ctk.set_appearance_mode("dark")


        self.root.grid_propagate(False)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)


        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="سازنده نمودار پرت",
            font=("B Nazanin", 24, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=(10, 20), sticky="n")


        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.input_frame.grid_rowconfigure(7, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)


        self.start_node_label = ctk.CTkLabel(
            self.input_frame,
            text="نام گره شروع را وارد کنید",
            font=FONT_FA,
            anchor="e"
        )
        self.start_node_label.grid(row=0, column=0, pady=(0, 5), sticky="e")

        self.start_node_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="مثال: شروع",
            font=FONT_FA,
            width=400,
            height=40,
            justify="right"
        )
        self.start_node_entry.grid(row=1, column=0, pady=(0, 10), sticky="ew")

        # End node input (RTL)
        self.end_node_label = ctk.CTkLabel(
            self.input_frame,
            text="نام گره پایان را وارد کنید",
            font=FONT_FA,
            anchor="e"
        )
        self.end_node_label.grid(row=2, column=0, pady=(0, 5), sticky="e")

        self.end_node_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="مثال: پایان",
            font=FONT_FA,
            width=400,
            height=40,
            justify="right"
        )
        self.end_node_entry.grid(row=3, column=0, pady=(0, 10), sticky="ew")


        self.node_label = ctk.CTkLabel(
            self.input_frame,
            text="نام‌ گره‌های دیگر را وارد کنید",
            font=FONT_FA,
            anchor="e"
        )
        self.node_label.grid(row=4, column=0, pady=(0, 5), sticky="e")

        self.node_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="با کاما جدا شود (مثال: نقشه,تست,کد,تخویل)",
            font=FONT_FA,
            width=400,
            height=40,
            justify="right"
        )
        self.node_entry.grid(row=5, column=0, pady=(0, 10), sticky="ew")


        self.add_nodes_btn = ctk.CTkButton(
            self.input_frame,
            text="افزودن گره‌ها",
            command=self.add_nodes,
            font=FONT_FA_BOLD,
            fg_color="#4CAF50",
            hover_color="#45a049",
            height=40
        )
        self.add_nodes_btn.grid(row=6, column=0, pady=(0, 20), sticky="ew")


        self.create_graph_btn = ctk.CTkButton(
            self.input_frame,
            text="باز کردن پنجره نمودار",
            command=self.open_graph_window,
            font=FONT_FA_BOLD,
            fg_color="#2196F3",
            hover_color="#0b7dda",
            height=40
        )
        self.create_graph_btn.grid(row=7, column=0, pady=(0, 20), sticky="ew")


        self.instructions = ctk.CTkLabel(
            self.input_frame,
            text="راهنمای استفاده\n ابـتدا پنجره نمودار را باز کنید\n ضروریست که ابتدا نود شروع و پایان را وارد کنید\n نود شروع با سبز و نود  پایان با قرمز نشان داده خواهد شد\n می توانید به دلخواه گره های دیگر را وارد کنید\n روی افزودن گره ها کلیک کنید\n با زدن روی دکمه ایجاد یال وضعیت ایجاد یال فعال می شود راهنمای ایجاد یال روی خود دگمه ایجاد یال وجود دارد\n اگر می خواهید بین دو یال بیش از دو گره بزنید لطفا این کار را رفت و برگشتی انجام دهید\n برای حذف یک نود ابتدا مطمئن باشید وضعیت ایجاد یال غیر فعال باشد بعد مطمئن باشید که گره را با نقطه چین سبز انتخاب\n نموده اید ",
            font=FONT_FA,
            justify="right",
            wraplength=950,
            anchor="e"
        )
        self.instructions.grid(row=8, column=0, pady=(20, 0), sticky="sew")


        self.input_frame.grid_rowconfigure(8, weight=1)

        self.graph_window = None
        self.update_input_states()

    def update_input_states(self):
        """Enable/disable input fields based on whether start/end nodes exist"""
        self.start_node_entry.configure(state="normal" if self.start_node is None else "disabled")
        self.end_node_entry.configure(state="normal" if self.end_node is None else "disabled")
        self.node_entry.configure(state="normal")

    def add_nodes(self):

        if self.start_node is None:
            start_name = self.start_node_entry.get().strip()
            if not start_name:
                tkinter.messagebox.showwarning(title='خطای نود شروع', message='لطفا نود شروع را وارد کنید')
                return


        if self.end_node is None:
            end_name = self.end_node_entry.get().strip()
            if not end_name:
                tkinter.messagebox.showwarning(title='خطای نود پایان', message='لطفا نود پایان وارد کنید')
                return

        other_nodes = self.node_entry.get().strip()

        if not self.graph_window:
            self.open_graph_window()


        if self.start_node is None:
            start_name = self.start_node_entry.get().strip()
            self.start_node = Node(self.graph_window.canvas, 200, 150, start_name, "start")
            self.nodes.append(self.start_node)
            self.make_draggable(self.start_node)
            self.start_node_entry.delete(0, tk.END)


        if self.end_node is None:
            end_name = self.end_node_entry.get().strip()
            self.end_node = Node(self.graph_window.canvas, 600, 150, end_name, "end")
            self.nodes.append(self.end_node)
            self.make_draggable(self.end_node)
            self.end_node_entry.delete(0, tk.END)


        if other_nodes:
            names = [name.strip() for name in other_nodes.split(',') if name.strip()]
            start_x, start_y = 200, 300
            spacing = 200

            for i, name in enumerate(names):
                x = start_x + (i % 3) * spacing
                y = start_y + (i // 3) * spacing
                new_node = Node(self.graph_window.canvas, x, y, name)
                self.nodes.append(new_node)
                self.make_draggable(new_node)

            self.node_entry.delete(0, tk.END)

        self.update_input_states()

    def open_graph_window(self):
        if not self.graph_window:
            self.graph_window = GraphWindow(self)
        self.root.wait_window(self.graph_window.top)
        self.graph_window = None

    def make_draggable(self, node):

        for item in node.canvas_items:
            self.canvas_tag_bind(item, "<ButtonPress-1>", lambda e, n=node: self.start_drag(e, n))
            self.canvas_tag_bind(item, "<B1-Motion>", self.do_drag)
            self.canvas_tag_bind(item, "<ButtonRelease-1>", self.stop_drag)

    def canvas_tag_bind(self, tag, sequence, func):
        """Helper method to bind events to canvas tags"""
        self.graph_window.canvas.tag_bind(tag, sequence, func)

    def start_drag(self, event, node):
        self.dragged_node = node
        self.drag_start_x = event.x
        self.drag_start_y = event.y


        if self.selected_node:
            self.selected_node.remove_highlight()
        node.highlight()
        self.selected_node = node

    def do_drag(self, event):
        if self.dragged_node:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            new_x = self.dragged_node.x + dx
            new_y = self.dragged_node.y + dy
            self.dragged_node.move(new_x, new_y)
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def stop_drag(self, event):
        self.dragged_node = None

    def delete_node(self, node):
        if node is None:
            return


        edges_to_remove = []
        for edge in self.edges[:]:
            if edge.start_node == node or edge.end_node == node:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            self.graph_window.canvas.delete(edge.line_id)
            self.graph_window.canvas.delete(edge.text_id)
            self.graph_window.canvas.delete(edge.arrow_id)
            if edge in self.edges:
                self.edges.remove(edge)


        for item in node.canvas_items:
            self.graph_window.canvas.delete(item)
        if node.highlight_id:
            self.graph_window.canvas.delete(node.highlight_id)
        if node in self.nodes:
            self.nodes.remove(node)


        if node == self.start_node:
            self.start_node = None
        if node == self.end_node:
            self.end_node = None

        self.selected_node = None
        self.update_input_states()


class GraphWindow:
    def __init__(self, pert_app):
        self.pert_app = pert_app
        self.top = ctk.CTkToplevel()
        self.top.title("نمودار پرت")
        self.top.geometry("1200x800")
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)


        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_columnconfigure(0, weight=1)


        self.container = ctk.CTkFrame(self.top)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)


        self.canvas = tk.Canvas(
            self.container,
            bg="#2B2B2B",
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")


        self.control_frame = ctk.CTkFrame(self.container)
        self.control_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)


        self.edge_btn = ctk.CTkButton(
            self.control_frame,
            text="ایجاد یال (روی دو گره کلیک کنید)",
            command=self.toggle_edge_mode,
            font=FONT_FA_BOLD,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            width=200
        )
        self.edge_btn.pack(side="right", padx=5, pady=5)  # Right side for RTL

        self.status_label = ctk.CTkLabel(
            self.control_frame,
            text="وضعیت ایجاد یال: غیرفعال",
            font=FONT_FA
        )
        self.status_label.pack(side="right", padx=10, pady=5)  # Right side for RTL


        self.delete_btn = ctk.CTkButton(
            self.control_frame,
            text="حذف انتخاب‌شده‌ها",
            command=self.delete_selected,
            font=FONT_FA_BOLD,
            fg_color="#F44336",
            hover_color="#D32F2F",
            width=150
        )
        self.delete_btn.pack(side="left", padx=5, pady=5)  # Left side for RTL

        self.edge_mode = False
        self.edge_start_node = None
        self.temp_line = None

        self.canvas.bind("<ButtonPress-1>", self.canvas_click)

    def toggle_edge_mode(self):
        self.edge_mode = not self.edge_mode
        status = "فعال" if self.edge_mode else "غیرفعال"
        self.status_label.configure(text=f"وضعیت ایجاد یال: {status}")
        self.edge_start_node = None
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None

    def canvas_click(self, event):
        if self.edge_mode:
            item = self.canvas.find_closest(event.x, event.y)[0]
            clicked_node = None
            for node in self.pert_app.nodes:
                if item in node.canvas_items:
                    clicked_node = node
                    break

            if clicked_node:
                if not self.edge_start_node:
                    self.edge_start_node = clicked_node
                    self.temp_line = self.canvas.create_line(
                        clicked_node.x, clicked_node.y, event.x, event.y,
                        width=2, fill="#9E9E9E", arrow=tk.LAST
                    )
                else:
                    if self.edge_start_node != clicked_node:
                        days = ctk.CTkInputDialog(
                            text="تعداد روزها را وارد کنید:",
                            title="مدت زمان یال"
                        ).get_input()
                        if days and days.isdigit():
                            new_edge = Edge(
                                self.canvas, self.edge_start_node,
                                clicked_node, days
                            )
                            self.pert_app.edges.append(new_edge)
                    self.canvas.delete(self.temp_line)
                    self.toggle_edge_mode()
            elif self.temp_line and self.edge_start_node:
                self.canvas.coords(
                    self.temp_line, self.edge_start_node.x,
                    self.edge_start_node.y, event.x, event.y
                )

    def delete_selected(self):
        if self.pert_app.selected_node:
            self.pert_app.delete_node(self.pert_app.selected_node)

    def on_close(self):

        Edge.edge_groups = {}
        self.top.destroy()


if __name__ == "__main__":
    app = PERTApp()
    app.root.mainloop()