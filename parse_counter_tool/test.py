import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re

class NetworkCounterParser:
    def __init__(self, root):
        self.root = root
        self.root.title("網絡計數器日誌解析器")
        self.root.geometry("1600x1000")
        
        # 存儲解析後的數據
        self.parsed_data = {
            'SS': {},
            'FCM': {},
            'MAC': {},
            'LS': {}
        }
        
        # HOST MAC 輸入框的變數
        self.host_mac_tx = tk.StringVar()
        self.host_mac_rx = tk.StringVar()
        
        self.setup_ui()
    
    def hex_to_decimal(self, value_str):
        """將16進位字符串轉換為10進位數字，如果不是16進位則直接返回原數字"""
        if not value_str:
            return 0
        
        value_str = value_str.strip()
        
        # 檢查是否為16進位格式 (0x... 或 0X...)
        if value_str.lower().startswith('0x'):
            try:
                return int(value_str, 16)
            except ValueError:
                return 0
        else:
            # 嘗試解析為10進位數字
            try:
                return int(value_str)
            except ValueError:
                return 0
    
    def format_display_value(self, value_str):
        """格式化顯示值，如果是16進位則顯示轉換結果"""
        if not value_str:
            return "0"
        
        value_str = value_str.strip()
        
        # 檢查是否為16進位格式
        if value_str.lower().startswith('0x'):
            try:
                decimal_value = int(value_str, 16)
                return f"{decimal_value}\n({value_str})"
            except ValueError:
                return "0"
        else:
            return value_str or "0"
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件輸入區域
        input_frame = ttk.LabelFrame(main_frame, text="輸入日誌數據", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(button_frame, text="載入文件", command=self.load_file).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="解析數據", command=self.parse_data).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="清除數據", command=self.clear_data).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="載入範例", command=self.load_example).grid(row=0, column=3)
        
        # 文本輸入區域
        self.text_input = scrolledtext.ScrolledText(input_frame, height=8, width=100)
        self.text_input.grid(row=1, column=0, pady=(5, 0), sticky=(tk.W, tk.E))
        
        # 流程圖顯示區域 - 增加高度以容納雙向流程
        flow_frame = ttk.LabelFrame(main_frame, text="計數器流程圖", padding="10")
        flow_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.create_flow_chart(flow_frame)
        
        # 詳細數據顯示區域
        detail_frame = ttk.LabelFrame(main_frame, text="詳細計數器數據", padding="5")
        detail_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 創建筆記本控件用於標籤頁
        self.notebook = ttk.Notebook(detail_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 為每個計數器類型創建標籤頁
        self.counter_frames = {}
        for counter_type in ['SS', 'FCM', 'MAC', 'LS']:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f"{counter_type} Counter")
            
            # 創建樹狀視圖
            tree = ttk.Treeview(frame, columns=('Value',), show='tree headings')
            tree.heading('#0', text='Counter Name')
            tree.heading('Value', text='Value')
            tree.column('#0', width=400)
            tree.column('Value', width=150)
            
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            self.counter_frames[counter_type] = tree
        
        # 配置權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=2)  # 給流程圖更多空間
        main_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(0, weight=1)
        flow_frame.columnconfigure(0, weight=1)
        flow_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        for counter_type in self.counter_frames:
            parent = self.counter_frames[counter_type].master
            parent.columnconfigure(0, weight=1)
            parent.rowconfigure(0, weight=1)
    
    def create_flow_chart(self, parent):
        # 創建Canvas來繪製流程圖
        self.canvas = tk.Canvas(parent, height=400, bg='white')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # HOST MAC 輸入區域
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Label(input_frame, text="HOST MAC Counters (支援16進位 0x...):").grid(row=0, column=0, columnspan=4, pady=(0, 5))
        
        ttk.Label(input_frame, text="TX:").grid(row=1, column=0, padx=(0, 5))
        ttk.Entry(input_frame, textvariable=self.host_mac_tx, width=20).grid(row=1, column=1, padx=(0, 20))
        
        ttk.Label(input_frame, text="RX:").grid(row=1, column=2, padx=(0, 5))
        ttk.Entry(input_frame, textvariable=self.host_mac_rx, width=20).grid(row=1, column=3)
        
        ttk.Button(input_frame, text="更新流程圖", command=self.draw_flow_chart).grid(row=1, column=4, padx=(20, 0))
        
        # 綁定輸入框變化事件
        self.host_mac_tx.trace('w', lambda *args: self.draw_flow_chart())
        self.host_mac_rx.trace('w', lambda *args: self.draw_flow_chart())
        
        # 繪製流程圖
        self.root.after(100, self.draw_flow_chart)  # 延遲繪製以確保canvas已初始化
    
    def get_counter_value(self, counter_type, counter_name):
        """獲取特定計數器的值"""
        return self.parsed_data.get(counter_type, {}).get(counter_name, 0)
    
    def check_tx_validation_rules(self, counter_type, key, value):
        """檢查TX方向的驗證規則，返回是否應該顯示為紅色"""
        if counter_type == 'SS':
            if 'Rx Start' in key:
                fcm_value = self.get_counter_value('FCM', 'Rx from System side_S')
                return value != fcm_value
            elif 'Rx Terminal' in key:
                fcm_value = self.get_counter_value('FCM', 'Rx from System side_T')
                return value != fcm_value
                
        elif counter_type == 'FCM':
            fcm_data = self.parsed_data.get('FCM', {})
            if 'Tx to Line side_S' in key:
                rx_system_s = self.get_counter_value('FCM', 'Rx from System side_S')
                ls_before_tx_s = self.get_counter_value('LS', '[Before EF] Tx to Line side_S')
                return value != rx_system_s or value != ls_before_tx_s
            elif 'Tx to Line side_T' in key:
                rx_system_t = self.get_counter_value('FCM', 'Rx from System side_T')
                ls_before_tx_t = self.get_counter_value('LS', '[Before EF] Tx to Line side_T')
                return value != rx_system_t or value != ls_before_tx_t
            elif 'Rx from System side_S' in key:
                ss_rx_start = self.get_counter_value('SS', 'Rx Start')
                return value != ss_rx_start
            elif 'Rx from System side_T' in key:
                ss_rx_terminal = self.get_counter_value('SS', 'Rx Terminal')
                return value != ss_rx_terminal
            elif 'Pause to Line side' in key:
                return value != 0
            elif 'Pause from System side' in key:
                return value != 0
                
        elif counter_type == 'ASIX MAC':
            if 'Tx Error from System side' in key:
                return value != 0
                
        elif counter_type == 'LS':
            if '[Before EF] Tx to Line side_S' in key:
                tx_line_s = self.get_counter_value('FCM', 'Tx to Line side_S')
                ls_after_tx_s = self.get_counter_value('LS', '[After EF] Tx to Line side_S')
                return value != tx_line_s or value != ls_after_tx_s
            elif '[Before EF] Tx to Line side_T' in key:
                tx_line_t = self.get_counter_value('FCM', 'Tx to Line side_T')
                ls_after_tx_t = self.get_counter_value('LS', '[After EF] Tx to Line side_T')
                return value != tx_line_t or value != ls_after_tx_t
            elif '[After EF] Tx to Line side_S' in key:
                ls_before_tx_s = self.get_counter_value('LS', '[Before EF] Tx to Line side_S')
                return value != ls_before_tx_s 
            elif '[After EF] Tx to Line side_T' in key:
                ls_before_tx_t = self.get_counter_value('LS', '[Before EF] Tx to Line side_T')
                return value != ls_before_tx_t
        
        return False
    
    def check_rx_validation_rules(self, counter_type, key, value):
        """檢查RX方向的驗證規則，返回是否應該顯示為紅色"""
        if counter_type == 'SS':
            if 'Tx Start' in key:
                fcm_value = self.get_counter_value('FCM', 'Tx to System side_S')
                return value != fcm_value
            elif 'Tx Terminal' in key:
                fcm_value = self.get_counter_value('FCM', 'Tx to System side_T')
                return value != fcm_value
                
        elif counter_type == 'FCM':
            if 'Rx from Line side_S' in key:
                tx_system_s = self.get_counter_value('FCM', 'Tx to System side_S')
                ls_after_rx_s = self.get_counter_value('LS', '[After EF] Rx from Line side_S')
                return value != tx_system_s or value != ls_after_rx_s
            elif 'Rx from Line side_T' in key:
                tx_system_t = self.get_counter_value('FCM', 'Tx to System side_T')
                ls_after_rx_t = self.get_counter_value('LS', '[After EF] Rx from Line side_T')
                return value != tx_system_t or value != ls_after_rx_t
            elif 'Tx to System side_S' in key:
                ss_tx_start = self.get_counter_value('SS', 'Tx Start')
                rx_line_s = self.get_counter_value('FCM', 'Rx from Line side_S')
                return value != ss_tx_start or value != rx_line_s
            elif 'Tx to System side_T' in key:
                ss_tx_terminal = self.get_counter_value('SS', 'Tx Terminal')
                rx_line_t = self.get_counter_value('FCM', 'Rx from Line side_T')
                return value != ss_tx_terminal or value != rx_line_t
            elif 'Pause from Line side' in key:
                return value != 0
            elif 'Pause to System side' in key:
                return value != 0
                
        elif counter_type == 'ASIX MAC':
            if 'Rx Error to System side' in key:
                return value != 0
                
        elif counter_type == 'LS':
            if '[After EF] Rx from Line side_S' in key:
                rx_line_s = self.get_counter_value('FCM', 'Rx from Line side_S')
                ls_before_rx_s = self.get_counter_value('LS', '[Before EF] Rx from Line side_S')
                return value != rx_line_s or value != ls_before_rx_s
            elif '[After EF] Rx from Line side_T' in key:
                ls_before_rx_t = self.get_counter_value('LS', '[Before EF] Rx from Line side_T')
                return value != ls_before_rx_t
            elif '[Before EF] Rx from Line side_S' in key:
                ls_after_rx_s = self.get_counter_value('LS', '[After EF] Rx from Line side_S')
                return value != ls_after_rx_s 
            elif '[Before EF] Rx from Line side_T' in key:
                ls_after_rx_t = self.get_counter_value('LS', '[After EF] Rx from Line side_T')
                return value != ls_after_rx_t
        
        return False
    
    def draw_flow_chart(self):
        self.canvas.delete("all")
        
        # 獲取Canvas實際尺寸
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas還未完全初始化
            self.root.after(100, self.draw_flow_chart)
            return
        
        # 計算位置
        box_width = 210
        box_height = 120
        host_mac_width = 120
        host_mac_height = 100  # 增加高度以容納兩行文字
        
        # 計算水平間距
        total_boxes_width = host_mac_width + 4 * box_width
        spacing = (canvas_width - total_boxes_width) // 6
        
        # HOST MAC 位置
        host_mac_x = spacing
        host_mac_y_tx = canvas_height // 4 - host_mac_height // 2
        host_mac_y_rx = 3 * canvas_height // 4 - host_mac_height // 2
        
        # 其他盒子的位置
        positions_tx = []
        positions_rx = []
        
        for i in range(4):
            x = host_mac_x + host_mac_width + spacing + i * (box_width + spacing)
            y_tx = canvas_height // 4 - box_height // 2
            y_rx = 3 * canvas_height // 4 - box_height // 2
            positions_tx.append((x, y_tx))
            positions_rx.append((x, y_rx))
        
        counter_types = ['SS', 'FCM', 'ASIX MAC', 'LS']
        colors = ['#FFE5E5', '#E5F3FF', '#E5FFE5', '#FFF5E5']
        border_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA726']
        
        # 繪製 HOST MAC
        # TX 方向
        self.canvas.create_rectangle(host_mac_x, host_mac_y_tx, 
                                   host_mac_x + host_mac_width, host_mac_y_tx + host_mac_height,
                                   fill='#F0F0F0', outline='#333333', width=3)
        self.canvas.create_text(host_mac_x + host_mac_width // 2, host_mac_y_tx + 15,
                              text="HOST MAC", font=('Arial', 10, 'bold'), fill='#333333')
        self.canvas.create_text(host_mac_x + host_mac_width // 2, host_mac_y_tx + 30,
                              text="TX", font=('Arial', 9, 'bold'), fill='#333333')
        
        # 顯示轉換後的TX值
        tx_display = self.format_display_value(self.host_mac_tx.get())
        # 分行顯示
        tx_lines = tx_display.split('\n')
        for i, line in enumerate(tx_lines):
            self.canvas.create_text(host_mac_x + host_mac_width // 2, host_mac_y_tx + 45 + i * 12,
                                  text=line, font=('Arial', 8), fill='#333333')
        
        # RX 方向
        self.canvas.create_rectangle(host_mac_x, host_mac_y_rx, 
                                   host_mac_x + host_mac_width, host_mac_y_rx + host_mac_height,
                                   fill='#F0F0F0', outline='#333333', width=3)
        self.canvas.create_text(host_mac_x + host_mac_width // 2, host_mac_y_rx + 15,
                              text="HOST MAC", font=('Arial', 10, 'bold'), fill='#333333')
        self.canvas.create_text(host_mac_x + host_mac_width // 2, host_mac_y_rx + 30,
                              text="RX", font=('Arial', 9, 'bold'), fill='#333333')
        
        # 顯示轉換後的RX值
        rx_display = self.format_display_value(self.host_mac_rx.get())
        # 分行顯示
        rx_lines = rx_display.split('\n')
        for i, line in enumerate(rx_lines):
            self.canvas.create_text(host_mac_x + host_mac_width // 2, host_mac_y_rx + 45 + i * 12,
                                  text=line, font=('Arial', 8), fill='#333333')
        
        # 繪製其他計數器框
        for i, (counter_type, color, border_color) in enumerate(zip(counter_types, colors, border_colors)):
            # TX 方向的框
            x_tx, y_tx = positions_tx[i]
            self.canvas.create_rectangle(x_tx, y_tx, x_tx + box_width, y_tx + box_height, 
                                       fill=color, outline=border_color, width=2)
            
            # RX 方向的框
            x_rx, y_rx = positions_rx[i]
            self.canvas.create_rectangle(x_rx, y_rx, x_rx + box_width, y_rx + box_height, 
                                       fill=color, outline=border_color, width=2)
            
            # 標題
            self.canvas.create_text(x_tx + box_width // 2, y_tx + 15, 
                                  text=counter_type, font=('Arial', 10, 'bold'), 
                                  fill=border_color)
            self.canvas.create_text(x_rx + box_width // 2, y_rx + 15, 
                                  text=counter_type, font=('Arial', 10, 'bold'), 
                                  fill=border_color)
            
            # 獲取對應的計數器數據
            if counter_type == 'ASIX MAC':
                counter_data = self.parsed_data.get('MAC', {})
            else:
                counter_data = self.parsed_data.get(counter_type, {})
            
            # TX 數據
            tx_data = self.get_tx_data(counter_type, counter_data)
            if tx_data:
                text_lines = []
                y_offset = y_tx + box_height // 2 + 5
                line_height = 12
                for j, (key, value) in enumerate(list(tx_data.items())[:6]):  # 限制顯示行數
                    text_color = '#FF0000' if self.check_tx_validation_rules(counter_type, key, value) else '#000000'
                    line_text = f"{key}: {value}"
                    
                    self.canvas.create_text(x_tx + box_width // 2, 
                                          y_offset - (len(list(tx_data.items())[:6]) - 1) * line_height // 2 + j * line_height,
                                          text=line_text, font=('Arial', 7), 
                                          anchor='center', fill=text_color)
            else:
                self.canvas.create_text(x_tx + box_width // 2, y_tx + box_height // 2 + 5, 
                                      text="TX: 無數據", font=('Arial', 8), anchor='center')
            
            # RX 數據
            rx_data = self.get_rx_data(counter_type, counter_data)
            if rx_data:
                text_lines = []
                y_offset = y_rx + box_height // 2 + 5
                line_height = 12
                for j, (key, value) in enumerate(list(rx_data.items())[:6]):  # 限制顯示行數
                    text_color = '#FF0000' if self.check_rx_validation_rules(counter_type, key, value) else '#000000'
                    line_text = f"{key}: {value}"
                    
                    self.canvas.create_text(x_rx + box_width // 2, 
                                          y_offset - (len(list(rx_data.items())[:6]) - 1) * line_height // 2 + j * line_height,
                                          text=line_text, font=('Arial', 7), 
                                          anchor='center', fill=text_color)
            else:
                self.canvas.create_text(x_rx + box_width // 2, y_rx + box_height // 2 + 5, 
                                      text="RX: 無數據", font=('Arial', 8), anchor='center')
        
        # 繪製箭頭 - TX 方向 (從左到右)
        # 從 HOST MAC TX 到第一個計數器
        self.canvas.create_line(host_mac_x + host_mac_width + 5, host_mac_y_tx + host_mac_height // 2,
                              positions_tx[0][0] - 5, positions_tx[0][1] + box_height // 2,
                              arrow=tk.LAST, width=2, fill='#FF4444')
        
        # 計數器之間的箭頭
        for i in range(3):
            start_x = positions_tx[i][0] + box_width + 5
            end_x = positions_tx[i + 1][0] - 5
            y = positions_tx[i][1] + box_height // 2
            self.canvas.create_line(start_x, y, end_x, y,
                                  arrow=tk.LAST, width=2, fill='#FF4444')
        
        # 繪製箭頭 - RX 方向 (從右到左) - 修改為與TX類似的格式
        # 從最後一個計數器到倒數第二個計數器
        for i in range(3, 0, -1):
            start_x = positions_rx[i][0] - 5
            end_x = positions_rx[i-1][0] + box_width + 5
            y = positions_rx[i][1] + box_height // 2
            self.canvas.create_line(start_x, y, end_x, y,
                                  arrow=tk.LAST, width=2, fill='#4444FF')
        
        # 最後一段箭頭從第一個計數器到HOST MAC RX
        self.canvas.create_line(positions_rx[0][0] - 5, positions_rx[0][1] + box_height // 2,
                              host_mac_x + host_mac_width + 5, host_mac_y_rx + host_mac_height // 2,
                              arrow=tk.LAST, width=2, fill='#4444FF')
        
        # 添加方向標籤
        self.canvas.create_text(canvas_width // 2-30, 20, text="TX 方向 (傳送)", 
                              font=('Arial', 12, 'bold'), fill='#FF4444')
        self.canvas.create_text(canvas_width // 2-30, canvas_height - 20, text="RX 方向 (接收)", 
                              font=('Arial', 12, 'bold'), fill='#4444FF')
    
    def get_tx_data(self, counter_type, counter_data):
        """提取TX相關的計數器數據"""
        tx_data = {}
        
        if counter_type == 'SS':
            # SS Counter TX: Rx Start, Rx Terminal
            for key, value in counter_data.items():
                if 'Rx Start' in key or 'Rx Terminal' in key:
                    tx_data[key] = value
                    
        elif counter_type == 'FCM':
            # FCM Counter TX: 除了RX方向的計數器以外的所有計數器
            rx_keys = {
                'Tx to System side_S', 'Tx to System side_T', 
                'Pause to System side', 'Pause from Line side',
                'Rx from Line side_S', 'Rx from Line side_T'
            }
            for key, value in counter_data.items():
                if not any(rx_key in key for rx_key in rx_keys):
                    tx_data[key] = value
                    
        elif counter_type == 'ASIX MAC':
            # MAC Counter TX: Tx Error from System side, Tx from System side
            for key, value in counter_data.items():
                if ('Tx Error from System side' in key or 
                    'Tx from System side' in key):
                    tx_data[key] = value
                    
        elif counter_type == 'LS':
            # LS Counter TX: 除了RX方向的計數器以外的所有計數器
            rx_keys = {
                'Rx_DEC', 'Rx from Line side_S', 'Rx from Line side_T'
            }
            for key, value in counter_data.items():
                if not any(rx_key in key for rx_key in rx_keys):
                    tx_data[key] = value
        
        return tx_data
    
    def get_rx_data(self, counter_type, counter_data):
        """提取RX相關的計數器數據"""
        rx_data = {}
        
        if counter_type == 'SS':
            # SS Counter RX: Tx Start, Tx Terminal
            for key, value in counter_data.items():
                if 'Tx Start' in key or 'Tx Terminal' in key:
                    rx_data[key] = value
                    
        elif counter_type == 'FCM':
            # FCM Counter RX: Tx to System side_S/T, Pause to System side, Pause from Line side,
            # Rx from Line side_S/T
            rx_keys = {
                'Tx to System side_S', 'Tx to System side_T', 
                'Pause to System side', 'Pause from Line side',
                'Rx from Line side_S', 'Rx from Line side_T'
            }
            for key, value in counter_data.items():
                if any(rx_key in key for rx_key in rx_keys):
                    rx_data[key] = value
                    
        elif counter_type == 'ASIX MAC':
            # MAC Counter RX: Rx Error to System side, Rx to System side
            for key, value in counter_data.items():
                if ('Rx Error to System side' in key or 
                    'Rx to System side' in key):
                    rx_data[key] = value
                    
        elif counter_type == 'LS':
            # LS Counter RX: Before EF_Rx_DEC, Before EF_Rx from Line side_S/T,
            # After EF_Rx from Line side_S/T
            rx_keys = {
                'Rx_DEC', 'Rx from Line side_S', 'Rx from Line side_T'
            }
            for key, value in counter_data.items():
                if any(rx_key in key for rx_key in rx_keys):
                    rx_data[key] = value
        
        return rx_data
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="選擇日誌文件",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, content)
                messagebox.showinfo("成功", "文件載入成功！")
            except Exception as e:
                messagebox.showerror("錯誤", f"載入文件失敗：{str(e)}")
    
    def load_example(self):
        example_data = """==========PHY[eth0.6] COUNTER===========
| <<SS Counter>>
| Tx Start                   :000667583 |
| Tx Terminal                :000667583 |
| Rx Start                   :000703812 |
| Rx Terminal                :000703812 |
| <<FCM counter>>
| Rx from Line side_S        :000667583 |
| Rx from Line side_T        :000667583 |
| Tx to System side_S        :000667583 |
| Tx to System side_T        :000667583 |
| Rx from System side_S      :000703812 |
| Rx from System side_T      :000703812 |
| Tx to Line side_S          :000703812 |
| Tx to Line side_T          :000703812 |
| Pause from Line side       :000000000 |
| Pause to System side       :000000000 |
| Pause from System side     :000000000 |
| Pause to Line side         :000000000 |
| <<MAC Counter>>
| Tx Error from System side  :000000000 |
| Rx Error to System side    :000000000 |
| Tx from System side        :000703812 |
| Rx to System side          :000667583 |
| <<LS counter>>
| Before EF
| Tx to Line side_S          :000703812 |
| Tx to Line side_T          :000703812 |
| Tx ENC                     :000703812 |
| Rx from Line side_S        :000667583 |
| Rx from Line side_T        :000667583 |
| Rx_DEC                     :000667583 |
| After EF
| Tx to Line side_S          :000703812 |
| Tx to Line side_T          :000703812 |
| Rx from Line side_S        :000667583 |
| Rx from Line side_T        :000667583 |"""
        
        self.text_input.delete(1.0, tk.END)
        self.text_input.insert(1.0, example_data)
        messagebox.showinfo("成功", "範例數據已載入！")
    
    def parse_data(self):
        content = self.text_input.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "請先輸入或載入日誌數據！")
            return
        
        try:
            self.parsed_data = {
                'SS': {},
                'FCM': {},
                'MAC': {},
                'LS': {}
            }
            
            lines = content.split('\n')
            current_counter_type = None
            current_section = None  # 用於LS counter的Before EF/After EF
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('='):
                    continue
                
                # 檢測計數器類型 - 更寬鬆的匹配
                if 'SS Counter' in line:
                    current_counter_type = 'SS'
                    current_section = None
                    continue
                elif 'FCM counter' in line:
                    current_counter_type = 'FCM'
                    current_section = None
                    continue
                elif 'MAC Counter' in line:
                    current_counter_type = 'MAC'
                    current_section = None
                    continue
                elif 'LS counter' in line:
                    current_counter_type = 'LS'
                    current_section = None
                    continue
                elif current_counter_type == 'LS' and 'Before EF' in line:
                    current_section = 'Before EF'
                    continue
                elif current_counter_type == 'LS' and 'After EF' in line:
                    current_section = 'After EF'
                    continue
                
                # 解析計數器數據 - 更靈活的模式匹配
                if current_counter_type and ':' in line:
                    # 嘗試多種匹配模式
                    patterns = [
                        r'\|\s*([^:]+?)\s*:\s*(\d+)\s*\|',  # 原始模式: | name :value |
                        r'\|\s*([^:]+?)\s*:\s*(\d+)',       # 簡化模式: | name :value
                        r'([^:]+?)\s*:\s*(\d+)',            # 最簡模式: name :value
                    ]
                    
                    matched = False
                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            counter_name = match.group(1).strip()
                            # 移除可能的前導豎線
                            counter_name = counter_name.lstrip('|').strip()
                            value = int(match.group(2))
                            
                            # 跳過空的計數器名稱或只包含特殊字符的名稱
                            if not counter_name or counter_name in ['<<', '>>', '|']:
                                break
                            
                            # 對於LS counter，如果有section，加上前綴
                            if current_counter_type == 'LS' and current_section:
                                counter_name = f"[{current_section}] {counter_name}"
                            
                            self.parsed_data[current_counter_type][counter_name] = value
                            matched = True
                            break
                    
                    # 如果沒有匹配到，輸出調試信息
                    if not matched and current_counter_type:
                        print(f"未匹配的行 ({current_counter_type}): {line}")
            
            self.update_display()
            
            # 顯示解析結果統計
            total_counters = sum(len(data) for data in self.parsed_data.values())
            messagebox.showinfo("解析完成", 
                              f"數據解析完成！\n"
                              f"SS Counter: {len(self.parsed_data['SS'])} 項\n"
                              f"FCM Counter: {len(self.parsed_data['FCM'])} 項\n"
                              f"MAC Counter: {len(self.parsed_data['MAC'])} 項\n"
                              f"LS Counter: {len(self.parsed_data['LS'])} 項\n"
                              f"總計: {total_counters} 項")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"解析數據失敗：{str(e)}")
    
    def update_display(self):
        # 更新流程圖
        self.draw_flow_chart()
        
        # 更新詳細數據表格
        for counter_type, tree in self.counter_frames.items():
            # 清除現有數據
            for item in tree.get_children():
                tree.delete(item)
            
            # 添加新數據
            counter_data = self.parsed_data.get(counter_type, {})
            for counter_name, value in counter_data.items():
                tree.insert('', 'end', text=counter_name, values=(value,))
    
    def clear_data(self):
        self.text_input.delete(1.0, tk.END)
        self.parsed_data = {
            'SS': {},
            'FCM': {},
            'MAC': {},
            'LS': {}
        }
        self.host_mac_tx.set("")
        self.host_mac_rx.set("")
        self.update_display()
        messagebox.showinfo("成功", "數據已清除！")

def main():
    root = tk.Tk()
    app = NetworkCounterParser(root)
    root.mainloop()

if __name__ == "__main__":
    main()