import tkinter as tk
from tkinter import ttk, messagebox
from algorithms.flujomaximo.PushRelabel import push_relabel
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx

class GrafoPushRelabelApp(tk.Tk):
    def __init__(self, G, nodos):
        super().__init__()
        self.title("Push-Relabel: Flujo máximo entre dos nodos")
        ancho, alto = 1400, 750
        self.geometry(f"{ancho}x{alto}")
        self.minsize(900, 450)
        self.center_window(ancho, alto)
        self.G = G
        self.nodos = nodos
        self.resultado_flujo = None
        self._crear_layout()
        self._make_responsive()

    def center_window(self, ancho, alto):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (ancho // 2)
        y = (hs // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_layout(self):
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=0)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=2)

        self.boton_atras = ttk.Button(self.container, text="← Atrás", command=self.volver_a_main)
        self.boton_atras.grid(row=0, column=0, sticky="nw", padx=10, pady=8, columnspan=2)

        self.left = tk.Frame(self.container)
        self.left.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(self.left, text="Selecciona Nodo Fuente:").pack(pady=(20,5), fill=tk.X)
        self.combo_fuente = ttk.Combobox(self.left, values=self.nodos, state="readonly")
        self.combo_fuente.pack(fill=tk.X)

        ttk.Label(self.left, text="Selecciona Nodo Sumidero:").pack(pady=(10,5), fill=tk.X)
        self.combo_sumidero = ttk.Combobox(self.left, values=self.nodos, state="readonly")
        self.combo_sumidero.pack(fill=tk.X)

        ttk.Button(self.left, text="Calcular Flujo Máximo (Push-Relabel)", command=self.calcular_flujo_maximo).pack(pady=20, fill=tk.X)

        self.resultado = tk.Text(self.left, height=28, width=43, state="disabled")
        self.resultado.pack(pady=10, fill=tk.BOTH, expand=True)

        self.right = tk.Frame(self.container)
        self.right.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.right.grid_rowconfigure(0, weight=1)
        self.right.grid_rowconfigure(1, weight=0)
        self.right.grid_columnconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(13, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        self.toolbar_frame = tk.Frame(self.right)
        self.toolbar_frame.grid(row=1, column=0, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def _make_responsive(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def calcular_flujo_maximo(self):
        fuente = self.combo_fuente.get()
        sumidero = self.combo_sumidero.get()

        if not fuente or not sumidero:
            messagebox.showwarning("Advertencia", "Debes seleccionar tanto el nodo fuente como el sumidero.")
            return

        if fuente == sumidero:
            messagebox.showwarning("Advertencia", "El nodo fuente y sumidero deben ser diferentes.")
            return
        from models.graph_logic import redireccionar_grafo_favor_flujo
        G_redirigido = redireccionar_grafo_favor_flujo(self.G, fuente, sumidero)

        try:
            self.resultado_flujo = push_relabel(G_redirigido, fuente, sumidero)
        except Exception as e:
            messagebox.showerror("Error", f"Error en el cálculo: {e}")
            return

        self.mostrar_resultados_flujo(fuente, sumidero)
        self.visualizar_grafo_flujo(fuente, sumidero)

    def mostrar_resultados_flujo(self, fuente, sumidero):
        self.resultado.configure(state="normal")
        self.resultado.delete(1.0, tk.END)

        self.resultado.insert(tk.END, f"FLUJO MÁXIMO: {fuente} → {sumidero}\n")
        self.resultado.insert(tk.END, "=" * 58 + "\n\n")
        flujo_maximo = self.resultado_flujo['max_flow']
        self.resultado.insert(tk.END, f"Flujo Máximo Total: {flujo_maximo:.2f} unidades\n")
        self.resultado.insert(tk.END, f"Etapas de preflujo: {len(self.resultado_flujo['flow_steps'])}\n\n")
        self.resultado.insert(tk.END, "ETAPAS DE EXCESO:\n")
        self.resultado.insert(tk.END, "-" * 58 + "\n")
        for i, step in enumerate(self.resultado_flujo['flow_steps'], 1):
            node = step['node']
            excess = step['excess']
            self.resultado.insert(tk.END, f"{i}. Nodo: {node}, Exceso: {excess[node]:.2f}\n")

        self.resultado.insert(tk.END, "\nUTILIZACIÓN DE ARISTAS:\n")
        self.resultado.insert(tk.END, "-" * 58 + "\n")
        self.resultado.insert(tk.END, f"{'Arista':<20} {'Flujo/Cap':>15} {'Utilización':>15}\n")
        self.resultado.insert(tk.END, "-" * 58 + "\n")

        for (u, v), flow_data in self.resultado_flujo['edge_flows'].items():
            if flow_data['flow'] > 0:
                arista = f"{u} → {v}"
                flujo_cap = f"{flow_data['flow']:.1f}/{flow_data['capacity']:.1f}"
                utilizacion = f"{flow_data['utilization']:.1f}%"
                self.resultado.insert(tk.END, f"{arista:<20} {flujo_cap:>15} {utilizacion:>15}\n")

        self.resultado.configure(state="disabled")

    def visualizar_grafo_flujo(self, fuente, sumidero):
        self.ax.clear()
        try:
            pos = {
                n: (self.G.nodes[n].get('pos', (0, 0))[1], self.G.nodes[n].get('pos', (0, 0))[0])
                for n in self.G.nodes if self.G.nodes[n].get('pos', (0, 0)) != (0,0)
            }
            for n in self.G.nodes:
                if self.G.nodes[n].get('pos', (0, 0)) == (0,0):
                    pos[n] = (0,0)
        except Exception as e:
            print("Error en posiciones de nodos:", e)
            pos = nx.spring_layout(self.G)

        node_colors = []
        for n in self.G.nodes():
            if n == fuente:
                node_colors.append("green")
            elif n == sumidero:
                node_colors.append("red")
            else:
                node_colors.append("skyblue")

        nx.draw_networkx_nodes(self.G, pos, ax=self.ax, node_color=node_colors, node_size=650)
        nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=10, font_family="DejaVu Sans")

        for (u, v), flow_data in self.resultado_flujo['edge_flows'].items():
            if flow_data['flow'] > 0:
                max_flow = max(1, self.resultado_flujo['max_flow'])
                width = max(2, (flow_data['flow'] / max_flow) * 8)
                utilization = flow_data['utilization']
                if utilization >= 90:
                    color = "red"
                elif utilization >= 70:
                    color = "orange"
                elif utilization >= 40:
                    color = "blue"
                else:
                    color = "green"
                nx.draw_networkx_edges(self.G, pos, edgelist=[(u, v)], ax=self.ax,
                                     width=width, edge_color=color, alpha=0.8)
            else:
                nx.draw_networkx_edges(self.G, pos, edgelist=[(u, v)], ax=self.ax,
                                     width=1, edge_color="lightgray", alpha=0.3)

        edge_labels = {}
        for (u, v), flow_data in self.resultado_flujo['edge_flows'].items():
            if flow_data['flow'] > 0:
                edge_labels[(u, v)] = f"{flow_data['flow']:.1f}/{flow_data['capacity']:.1f}"

        nx.draw_networkx_edge_labels(self.G, pos, edge_labels, ax=self.ax, font_size=6, font_family="DejaVu Sans")

        self.ax.set_title(f"Flujo Máximo: {fuente} → {sumidero} = {self.resultado_flujo['max_flow']:.2f} unidades",
                         fontsize=18, fontfamily="DejaVu Sans")
        self.ax.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()

    def volver_a_main(self):
        self.destroy()
        from app.gui_main import MainApp
        MainApp().mainloop()