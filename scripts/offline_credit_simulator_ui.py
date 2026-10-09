"""Standalone Windows preview for offline multi-profile allocation.

This window is independent of the Flow-Otomatis production UI and does not
connect to Google, Chrome, an API, any user account, or any persisted SQLite DB.
"""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from offline_credit_simulator import simulate

DEMO: dict = {
    "mode": "OFFLINE_SIMULATION",
    "profiles": [
        {"profile_id": "demo-A", "simulated_balance": 20, "max_spend": 20},
        {"profile_id": "demo-B", "simulated_balance": 20, "max_spend": 20},
    ],
    "scenes": [
        {"project_id": "demo-film", "scene_id": "SCENE_001", "duration_s": 10, "outputs": 1},
        {"project_id": "demo-film", "scene_id": "SCENE_002", "duration_s": 8, "outputs": 1},
        {"project_id": "demo-film", "scene_id": "SCENE_003", "duration_s": 6, "outputs": 1},
    ],
    "rates_per_video": {"4": 7, "6": 10, "8": 12, "10": 15},
    "max_total_credits": 40,
}


class OfflineSimulatorApp:
    """Simple, standalone read-only preview for the fake planning algorithm."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flow-Otomatis | Simulator Multiakun Offline")
        self.root.geometry("1100x680")
        self.root.minsize(800, 500)
        self._report: str | None = None

        style = ttk.Style()
        style.configure("Header.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Note.TLabel", font=("Segoe UI", 10))
        wrapper = ttk.Frame(root, padding=16)
        wrapper.pack(fill="both", expand=True)
        ttk.Label(
            wrapper, text="Simulator Pembagian Scene & Kredit (OFFLINE)", style="Header.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            wrapper,
            text=(
                "HANYA SIMULASI. Saldo dan tarif adalah contoh, bukan bukti kredit "
                "Google Flow. Tidak ada login, Generate, Download, atau pemakaian kredit."
            ),
            style="Note.TLabel",
            wraplength=1050,
        ).pack(anchor="w", pady=(4, 12))

        actions = ttk.Frame(wrapper)
        actions.pack(fill="x", pady=(0, 10))
        ttk.Button(actions, text="Buka JSON", command=self._open_json).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(actions, text="Contoh Simulasi", command=self._load_demo).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(actions, text="Hitung Offline", command=self._run).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Simpan Hasil JSON", command=self._save_json).pack(side="left")
        self.status = tk.StringVar(value="Belum dihitung")
        ttk.Label(actions, textvariable=self.status).pack(side="right")

        panels = ttk.PanedWindow(wrapper, orient="horizontal")
        panels.pack(fill="both", expand=True)

        left = ttk.Frame(panels)
        right = ttk.Frame(panels)
        panels.add(left, weight=1)
        panels.add(right, weight=1)
        ttk.Label(left, text="Data simulasi (JSON)").pack(anchor="w", pady=(0, 5))
        ttk.Label(right, text="Hasil simulasi — tidak untuk live dispatch").pack(
            anchor="w", pady=(0, 5)
        )
        self.input_box = tk.Text(left, wrap="none", font=("Consolas", 10), undo=True)
        self.input_box.pack(fill="both", expand=True)
        self.output_box = tk.Text(right, wrap="none", font=("Consolas", 10), state="disabled")
        self.output_box.pack(fill="both", expand=True)
        self._load_demo()

    def _load_demo(self) -> None:
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", json.dumps(DEMO, indent=2, ensure_ascii=False))
        self._report = None
        self.status.set("Contoh lokal dimuat — belum dihitung")

    def _open_json(self) -> None:
        filename = filedialog.askopenfilename(
            title="Pilih file JSON simulasi", filetypes=[("JSON", "*.json")]
        )
        if not filename:
            return
        try:
            content = Path(filename).read_text(encoding="utf-8")
            json.loads(content)
        except (OSError, UnicodeError, ValueError) as exc:
            messagebox.showerror("JSON tidak valid", str(exc))
            return
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", content)
        self._report = None
        self.status.set("JSON dimuat — belum dihitung")

    def _run(self) -> None:
        try:
            payload = json.loads(self.input_box.get("1.0", "end"))
            result = simulate(payload)
        except ValueError as exc:
            self._report = None
            self.status.set("DIBLOKIR — input tidak valid")
            messagebox.showerror("Simulasi ditolak", str(exc))
            return
        self._report = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", self._report)
        self.output_box.configure(state="disabled")
        self.status.set(
            f"Selesai: {len(result['assigned'])} ditugaskan, "
            f"{len(result['blocked'])} ditahan (SIMULASI)"
        )

    def _save_json(self) -> None:
        if self._report is None:
            messagebox.showwarning("Belum ada hasil", "Klik Hitung Offline terlebih dahulu.")
            return
        filename = filedialog.asksaveasfilename(
            title="Simpan JSON hasil simulasi",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not filename:
            return
        try:
            with Path(filename).open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(self._report)
        except FileExistsError:
            messagebox.showwarning(
                "File sudah ada", "File lama tidak akan ditimpa. Pilih nama lain."
            )
            return
        except OSError as exc:
            messagebox.showerror("Tidak bisa menyimpan", str(exc))
            return
        self.status.set("Hasil simulasi tersimpan (tanpa kredensial)")


def main() -> None:
    root = tk.Tk()
    OfflineSimulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
