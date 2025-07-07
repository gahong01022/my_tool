#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaTek 網路晶片寄存器解析器 GUI 版本
用於解析 debug 輸出中的寄存器值並顯示在視窗中
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re

class NetworkChipRegisterParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MediaTek 網路晶片寄存器解析器")
        self.root.geometry("1200x800")
        
        self.registers = {}
        self.setup_gui()
        
        # 預設寄存器資料
        self.load_default_data()
        
    def setup_gui(self):
        """設置圖形界面"""
        # 創建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 標題
        title_label = ttk.Label(main_frame, text="MediaTek 網路晶片寄存器解析器", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 左側：輸入區域
        input_frame = ttk.LabelFrame(main_frame, text="寄存器資料輸入", padding="5")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        # 輸入文字區域
        self.input_text = scrolledtext.ScrolledText(input_frame, width=50, height=25, 
                                                   font=("Consolas", 10))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 按鈕框架
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=0, pady=(5, 0))
        
        # 解析按鈕
        parse_button = ttk.Button(button_frame, text="解析寄存器", 
                                 command=self.parse_and_analyze)
        parse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 清除按鈕
        clear_button = ttk.Button(button_frame, text="清除輸入", 
                                 command=self.clear_input)
        clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 載入範例按鈕
        example_button = ttk.Button(button_frame, text="載入範例", 
                                   command=self.load_default_data)
        example_button.pack(side=tk.LEFT)
        
        # 右側：結果顯示區域
        result_frame = ttk.LabelFrame(main_frame, text="解析結果", padding="5")
        result_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 結果顯示區域
        self.result_text = scrolledtext.ScrolledText(result_frame, width=60, height=25, 
                                                    font=("Consolas", 10))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 底部狀態列
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def load_default_data(self):
        """載入預設的寄存器資料"""
        default_data = """RG_MII_REG_00       : 0x00001140
RG_MII_REG_01       : 0x00004169
RG_MII_REG_02       : 0x00003a2
RG_MII_REG_03       : 0x0000a411
RG_MII_REG_04       : 0x00001d01
RG_MII_REG_05       : 0x0000dd01
RG_MII_REG_06       : 0x0000000f
RG_MII_REG_07       : 0x00002801
RG_MII_REG_08       : 0x00004400
RG_MII_REG_09       : 0x00000200
RG_MII_REG_0a       : 0x000048ff
RG_ABILITY_2G5      : 0x00000081
RG_LINK_PARTNER_2G5 : 0x00000003
RG_MII_REF_CLK      : 0x0000000c
RG_PHY_ANA          : 0x01a01501
RG_HW_STRAP1        : 0x000f8000
RG_HW_STRAP2        : 0x00301105
RG_SYS_LINK_MODE    : 0x00000893
RG_FCM_CTRL         : 0x00000007
RG_SS_PAUSE_TIME    : 0x0000ff00
RG_MIN_IPG_NUM      : 0x05050505
RG_CSR_AN0          : 0x00000140
RG_SS_LINK_STATUS   : 0x0800b230
RG_LINK_PARTNER_AN  : 0x00000000
RG_FN_PWR_CTRL_STATUS : 0x00030008
RG_MD32_FW_READY    : 0x00000002
RG_RX_SYNC_CNT      : 0x00000001
RG_WHILE_LOOP_COUNT : 0x00b517a8"""
        
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, default_data)
        
    def clear_input(self):
        """清除輸入區域"""
        self.input_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("已清除")
        
    def parse_register_dump(self, dump_text):
        """解析寄存器轉儲文本"""
        self.registers = {}
        lines = dump_text.strip().split('\n')
        
        for line in lines:
            # 使用正規表達式匹配寄存器名稱和值
            match = re.match(r'^\s*(\w+)\s*:\s*(0x[0-9a-fA-F]+)', line)
            if match:
                reg_name = match.group(1)
                reg_value = match.group(2)
                try:
                    self.registers[reg_name] = int(reg_value, 16)
                except ValueError:
                    continue
        
        return len(self.registers)
    
    def parse_and_analyze(self):
        """解析並分析寄存器"""
        try:
            # 獲取輸入文本
            input_data = self.input_text.get(1.0, tk.END).strip()
            
            if not input_data:
                messagebox.showwarning("警告", "請先輸入寄存器資料")
                return
            
            # 解析寄存器
            reg_count = self.parse_register_dump(input_data)
            
            if reg_count == 0:
                messagebox.showerror("錯誤", "無法解析寄存器資料，請檢查格式")
                return
            
            # 清除結果區域
            self.result_text.delete(1.0, tk.END)
            
            # 執行分析
            result = self.analyze_all_registers()
            
            # 顯示結果
            self.result_text.insert(tk.END, result)
            
            # 更新狀態
            self.status_var.set(f"解析完成，共處理 {reg_count} 個寄存器")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"解析過程中發生錯誤：{str(e)}")
            self.status_var.set("解析失敗")
    
    def analyze_all_registers(self):
        """分析所有寄存器並返回結果字串"""
        result = []
        result.append("MediaTek 網路晶片寄存器分析報告")
        result.append("=" * 60)
        result.append("")
        
        # 分析 MII 寄存器
        mii_result = self.analyze_mii_registers()
        result.extend(mii_result)
        
        # 分析系統寄存器
        sys_result = self.analyze_system_registers()
        result.extend(sys_result)
        
        result.append("")
        result.append("=" * 60)
        result.append("分析完成")
        result.append("=" * 60)
        
        return '\n'.join(result)
    
    def analyze_mii_registers(self):
        """分析 MII 寄存器區塊"""
        result = []
        result.append("=" * 60)
        result.append("MII 寄存器區塊分析 (IEEE 802.3 PHY 控制)")
        result.append("=" * 60)
        
        mii_regs = {
            'RG_MII_REG_00': 'Basic Control Register',
            'RG_MII_REG_01': 'Basic Status Register', 
            'RG_MII_REG_02': 'PHY Identifier 1',
            'RG_MII_REG_03': 'PHY Identifier 2',
            'RG_MII_REG_04': 'Auto-Negotiation Advertisement',
            'RG_MII_REG_05': 'Auto-Negotiation Link Partner Ability',
            'RG_MII_REG_06': 'Auto-Negotiation Expansion',
            'RG_MII_REG_07': 'Auto-Negotiation Next Page TX',
            'RG_MII_REG_08': 'Auto-Negotiation Link Partner Next Page RX',
            'RG_MII_REG_09': '1000BASE-T Control Register',
            'RG_MII_REG_0a': '1000BASE-T Status Register'
        }
        
        for reg_name, description in mii_regs.items():
            if reg_name in self.registers:
                value = self.registers[reg_name]
                result.append(f"\n{reg_name}: {description}")
                result.append(f"值: 0x{value:08x} ({value})")
                
                if reg_name == 'RG_MII_REG_00':
                    result.extend(self._analyze_mii_control_reg(value))
                elif reg_name == 'RG_MII_REG_01':
                    result.extend(self._analyze_mii_status_reg(value))
                elif reg_name == 'RG_MII_REG_04':
                    result.extend(self._analyze_mii_advertisement_reg(value))
                elif reg_name == 'RG_MII_REG_05':
                    result.extend(self._analyze_mii_link_partner_reg(value))
        
        return result
    
    def _analyze_mii_control_reg(self, value):
        """分析 MII 控制寄存器 (REG_00)"""
        result = []
        result.append("  位元分析:")
        result.append(f"    [15] SW Reset: {'是' if value & (1<<15) else '否'}")
        result.append(f"    [14] Loopback: {'開啟' if value & (1<<14) else '關閉'}")
        result.append(f"    [13] Speed Select (LSB): {'是' if value & (1<<13) else '否'}")
        result.append(f"    [12] Auto-Negotiation Enable: {'開啟' if value & (1<<12) else '關閉'}")
        result.append(f"    [11] Power Down: {'Power Down' if value & (1<<11) else 'Normal operation'}")
        result.append(f"    [10] Isolate: {'是' if value & (1<<10) else 'Normal operation'}")
        result.append(f"    [9] Restart Auto-Negotiation: {'是' if value & (1<<9) else 'Normal operation'}")
        result.append(f"    [8] Duplex Mode: {'全雙工' if value & (1<<8) else '半雙工'}")
        result.append(f"    [7] Collision Test: {'開啟' if value & (1<<7) else '關閉'}")
        result.append(f"    [6] Speed Select (MSB): {'是' if value & (1<<6) else '否'}")
        
        # 速度判斷
        speed_bits = ((value >> 6) & 1) << 1 | ((value >> 13) & 1)
        speeds = {0: '10 Mbps', 1: '100 Mbps', 2: '1000 Mbps', 3: '保留'}
        result.append(f"    速度設定: {speeds.get(speed_bits, '未知')}")
        
        return result
    
    def _analyze_mii_status_reg(self, value):
        """分析 MII 狀態寄存器 (REG_01)"""
        result = []
        result.append("  位元分析:")
        result.append(f"    [15] 100BASE-T4 能力: {'支援' if value & (1<<15) else '不支援'}")
        result.append(f"    [14] 100BASE-X 全雙工: {'支援' if value & (1<<14) else '不支援'}")
        result.append(f"    [13] 100BASE-X 半雙工: {'支援' if value & (1<<13) else '不支援'}")
        result.append(f"    [12] 10BASE-T 全雙工: {'支援' if value & (1<<12) else '不支援'}")
        result.append(f"    [11] 10BASE-T 半雙工: {'支援' if value & (1<<11) else '不支援'}")
        result.append(f"    [8] Extended Status: {'支援' if value & (1<<8) else '不支援'}")
        result.append(f"    [7] MF Preamble Suppression: {'支援' if value & (1<<7) else '不支援'}")
        result.append(f"    [6] Auto-Negotiation Complete: {'完成' if value & (1<<6) else '未完成'}")
        result.append(f"    [5] Remote Fault: {'有' if value & (1<<5) else '無'}")
        result.append(f"    [4] Auto-Negotiation Ability: {'支援' if value & (1<<4) else '不支援'}")
        result.append(f"    [3] Link Status: {'連接' if value & (1<<3) else '斷開'}")
        result.append(f"    [2] Jabber Detect: {'檢測到' if value & (1<<2) else '正常'}")
        result.append(f"    [1] Extended Capability: {'支援' if value & (1<<1) else '不支援'}")
        
        return result
    
    def _analyze_mii_advertisement_reg(self, value):
        """分析自動協商廣告寄存器 (REG_04)"""
        result = []
        result.append("  位元分析:")
        result.append(f"    [15] Next Page: {'支援' if value & (1<<15) else '不支援'}")
        result.append(f"    [14] Remote Fault: {'有' if value & (1<<14) else '無'}")
        result.append(f"    [13] Asymmetric Pause: {'支援' if value & (1<<13) else '不支援'}")
        result.append(f"    [12] Pause: {'支援' if value & (1<<12) else '不支援'}")
        result.append(f"    [11] 100BASE-T4: {'支援' if value & (1<<11) else '不支援'}")
        result.append(f"    [10] 100BASE-TX 全雙工: {'支援' if value & (1<<10) else '不支援'}")
        result.append(f"    [9] 100BASE-TX 半雙工: {'支援' if value & (1<<9) else '不支援'}")
        result.append(f"    [8] 10BASE-T 全雙工: {'支援' if value & (1<<8) else '不支援'}")
        result.append(f"    [7] 10BASE-T 半雙工: {'支援' if value & (1<<7) else '不支援'}")
        result.append(f"    [4:0] 選擇器欄位: 0x{value & 0x1F:02x}")
        
        return result
    
    def _analyze_mii_link_partner_reg(self, value):
        """分析鏈路伙伴能力寄存器 (REG_05)"""
        result = []
        result.append("  位元分析:")
        result.append(f"    [15] Next Page: {'支援' if value & (1<<15) else '不支援'}")
        result.append(f"    [14] Acknowledge: {'確認' if value & (1<<14) else '未確認'}")
        result.append(f"    [13] Remote Fault: {'有' if value & (1<<13) else '無'}")
        result.append(f"    [12] Asymmetric Pause: {'支援' if value & (1<<12) else '不支援'}")
        result.append(f"    [11] Pause: {'支援' if value & (1<<11) else '不支援'}")
        result.append(f"    [10] 100BASE-T4: {'支援' if value & (1<<10) else '不支援'}")
        result.append(f"    [9] 100BASE-TX 全雙工: {'支援' if value & (1<<9) else '不支援'}")
        result.append(f"    [8] 100BASE-TX 半雙工: {'支援' if value & (1<<8) else '不支援'}")
        result.append(f"    [7] 10BASE-T 全雙工: {'支援' if value & (1<<7) else '不支援'}")
        result.append(f"    [6] 10BASE-T 半雙工: {'支援' if value & (1<<6) else '不支援'}")
        result.append(f"    [4:0] 選擇器欄位: 0x{value & 0x1F:02x}")
        
        return result
    
    def analyze_system_registers(self):
        """分析系統控制寄存器區塊"""
        result = []
        result.append("\n" + "=" * 60)
        result.append("系統控制寄存器區塊分析")
        result.append("=" * 60)
        
        system_regs = {
            'RG_ABILITY_2G5': '2.5G 能力寄存器',
            'RG_LINK_PARTNER_2G5': '2.5G 鏈路伙伴能力',
            'RG_MII_REF_CLK': 'MII 參考時鐘控制',
            'RG_PHY_ANA': 'PHY 類比控制',
            'RG_HW_STRAP1': '硬體綁定設定 1',
            'RG_HW_STRAP2': '硬體綁定設定 2',
            'RG_SYS_LINK_MODE': '系統鏈路模式',
            'RG_FCM_CTRL': '流量控制管理',
            'RG_SS_PAUSE_TIME': '暫停時間設定',
            'RG_MIN_IPG_NUM': '最小封包間隔',
            'RG_CSR_AN0': '自動協商控制狀態 0',
            'RG_SS_LINK_STATUS': '鏈路狀態',
            'RG_LINK_PARTNER_AN': '鏈路伙伴自動協商',
            'RG_FN_PWR_CTRL_STATUS': '功率控制狀態',
            'RG_MD32_FW_READY': 'MD32 韌體就緒',
            'RG_RX_SYNC_CNT': '接收同步計數器',
            'RG_WHILE_LOOP_COUNT': '迴圈計數器'
        }
        
        for reg_name, description in system_regs.items():
            if reg_name in self.registers:
                value = self.registers[reg_name]
                result.append(f"\n{reg_name}: {description}")
                result.append(f"值: 0x{value:08x} ({value})")
                
                if reg_name == 'RG_ABILITY_2G5':
                    result.extend(self._analyze_2g5_ability_reg(value))
                elif reg_name == 'RG_SYS_LINK_MODE':
                    result.extend(self._analyze_link_mode_reg(value))
                elif reg_name == 'RG_SS_LINK_STATUS':
                    result.extend(self._analyze_link_status_reg(value))
                elif reg_name == 'RG_FCM_CTRL':
                    result.extend(self._analyze_fcm_ctrl_reg(value))
        
        return result
    
    def _analyze_2g5_ability_reg(self, value):
        """分析 2.5G 能力寄存器"""
        result = []
        result.append("  位元分析:")
        result.append(f"    [7] 2.5G 全雙工: {'支援' if value & (1<<7) else '不支援'}")
        result.append(f"    [6] 2.5G 半雙工: {'支援' if value & (1<<6) else '不支援'}")
        result.append(f"    [5] 5G 全雙工: {'支援' if value & (1<<5) else '不支援'}")
        result.append(f"    [4] 5G 半雙工: {'支援' if value & (1<<4) else '不支援'}")
        result.append(f"    [3:0] 其他能力: 0x{value & 0xF:x}")
        
        return result
    
    def _analyze_link_mode_reg(self, value):
        """分析鏈路模式寄存器"""
        result = []
        result.append("  位元分析:")
        link_modes = {
            0: '10BASE-T 半雙工',
            1: '10BASE-T 全雙工', 
            2: '100BASE-TX 半雙工',
            3: '100BASE-TX 全雙工',
            4: '1000BASE-T 半雙工',
            5: '1000BASE-T 全雙工',
            6: '2.5GBASE-T',
            7: '5GBASE-T'
        }
        mode = value & 0x7
        result.append(f"    [2:0] 鏈路模式: {link_modes.get(mode, '未知模式')} ({mode})")
        result.append(f"    [8] 自動協商啟用: {'是' if value & (1<<8) else '否'}")
        result.append(f"    [9] 強制模式: {'是' if value & (1<<9) else '否'}")
        
        return result
    
    def _analyze_link_status_reg(self, value):
        """分析鏈路狀態寄存器"""
        result = []
        result.append("  位元分析:")
        result.append(f"    [0] 鏈路狀態: {'UP' if value & 1 else 'DOWN'}")
        result.append(f"    [1] 雙工模式: {'全雙工' if value & (1<<1) else '半雙工'}")
        result.append(f"    [4:2] 速度: {self._decode_speed((value >> 2) & 0x7)}")
        result.append(f"    [5] 自動協商完成: {'是' if value & (1<<5) else '否'}")
        result.append(f"    [6] 遠端故障: {'是' if value & (1<<6) else '否'}")
        result.append(f"    [7] 本地故障: {'是' if value & (1<<7) else '否'}")
        
        return result
    
    def _analyze_fcm_ctrl_reg(self, value):
        """分析流量控制管理寄存器"""
        result = []
        result.append("  位元分析:")
        result.append(f"    [0] TX 流量控制: {'啟用' if value & 1 else '停用'}")
        result.append(f"    [1] RX 流量控制: {'啟用' if value & (1<<1) else '停用'}")
        result.append(f"    [2] 暫停幀生成: {'啟用' if value & (1<<2) else '停用'}")
        result.append(f"    [3] 暫停幀檢測: {'啟用' if value & (1<<3) else '停用'}")
        result.append(f"    [15:8] 暫停時間: {(value >> 8) & 0xFF}")
        
        return result
    
    def _decode_speed(self, speed_code):
        """解碼速度值"""
        speeds = {
            0: '10 Mbps',
            1: '100 Mbps', 
            2: '1000 Mbps',
            3: '2500 Mbps',
            4: '5000 Mbps',
            5: '10000 Mbps'
        }
        return speeds.get(speed_code, f'未知速度 ({speed_code})')

def main():
    """主程序"""
    root = tk.Tk()
    app = NetworkChipRegisterParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()