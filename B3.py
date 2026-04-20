import tkinter as tk
from tkinter import scrolledtext, messagebox
import serial
import threading

class STM32Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("BÀI 3")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.serial_port = None
        self.is_reading = False

        self.setup_ui()

    def setup_ui(self):
        # --- Khu vực Kết nối ---
        frame_conn = tk.LabelFrame(self.root, text="Cấu hình Kết nối", padx=10, pady=10)
        frame_conn.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_conn, text="Cổng COM:").grid(row=0, column=0, padx=5)
        self.com_entry = tk.Entry(frame_conn, width=10)
        self.com_entry.insert(0, "COM9") # Mặc định là COM9 theo yêu cầu của bạn
        self.com_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame_conn, text="Baudrate:").grid(row=0, column=2, padx=5)
        self.baud_entry = tk.Entry(frame_conn, width=10)
        self.baud_entry.insert(0, "115200") # Khớp với code C
        self.baud_entry.grid(row=0, column=3, padx=5)

        self.btn_connect = tk.Button(frame_conn, text="Kết nối", bg="lightblue", command=self.toggle_connection)
        self.btn_connect.grid(row=0, column=4, padx=10)

        # --- Khu vực Điều khiển ---
        frame_ctrl = tk.LabelFrame(self.root, text="Điều khiển", padx=10, pady=10)
        frame_ctrl.pack(fill="x", padx=10, pady=5)

        self.btn_start = tk.Button(frame_ctrl, text="▶ BẬT HỆ THỐNG", bg="lightgreen", width=25, state=tk.DISABLED, command=self.send_start)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(frame_ctrl, text="■ DỪNG HỆ THỐNG", bg="salmon", width=25, state=tk.DISABLED, command=self.send_stop)
        self.btn_stop.pack(side=tk.RIGHT, padx=10)

        # --- Khu vực Giám sát (Terminal) ---
        frame_mon = tk.LabelFrame(self.root, text="Giám sát Dữ liệu", padx=10, pady=10)
        frame_mon.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_terminal = scrolledtext.ScrolledText(frame_mon, wrap=tk.WORD, height=12, state=tk.DISABLED, bg="black", fg="lime")
        self.txt_terminal.pack(fill="both", expand=True)

        self.btn_clear = tk.Button(frame_mon, text="Xóa màn hình", command=self.clear_terminal)
        self.btn_clear.pack(pady=5)

    def toggle_connection(self):
        if self.serial_port is None or not self.serial_port.is_open:
            # Thực hiện kết nối
            com = self.com_entry.get()
            baud = self.baud_entry.get()
            try:
                self.serial_port = serial.Serial(com, int(baud), timeout=1)
                self.btn_connect.config(text="Ngắt kết nối", bg="orange")
                self.btn_start.config(state=tk.NORMAL)
                self.btn_stop.config(state=tk.NORMAL)
                self.com_entry.config(state=tk.DISABLED)
                self.baud_entry.config(state=tk.DISABLED)
                
                # Bắt đầu luồng đọc dữ liệu
                self.is_reading = True
                self.read_thread = threading.Thread(target=self.read_from_port)
                self.read_thread.daemon = True
                self.read_thread.start()
                self.log(f"Đã kết nối thành công với {com} ({baud} bps)\n")
            except serial.SerialException as e:
                messagebox.showerror("Lỗi Kết Nối", f"Không thể mở cổng {com}. Lỗi: {e}")
        else:
            # Ngắt kết nối
            self.is_reading = False
            self.serial_port.close()
            self.btn_connect.config(text="Kết nối", bg="lightblue")
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
            self.com_entry.config(state=tk.NORMAL)
            self.baud_entry.config(state=tk.NORMAL)
            self.log(f"Đã ngắt kết nối\n")

    def read_from_port(self):
        while self.is_reading and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore')
                    if data:
                        # Dùng root.after để cập nhật an toàn vào GUI từ thread khác
                        self.root.after(0, self.log, data.strip())
            except OSError:
                break
            except serial.SerialException:
                break

    def send_start(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b'1')
            self.log(">>> GỬI LỆNH: BẬT\n", color="yellow")

    def send_stop(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(b'0')
            self.log(">>> GỬI LỆNH: DỪNG\n", color="red")

    def log(self, message, color="lime"):
        self.txt_terminal.config(state=tk.NORMAL)
        self.txt_terminal.insert(tk.END, message + "\n")
        self.txt_terminal.see(tk.END)
        self.txt_terminal.config(state=tk.DISABLED)

    def clear_terminal(self):
        self.txt_terminal.config(state=tk.NORMAL)
        self.txt_terminal.delete(1.0, tk.END)
        self.txt_terminal.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = tk.Tk()
    dashboard = STM32Dashboard(app)
    app.mainloop()