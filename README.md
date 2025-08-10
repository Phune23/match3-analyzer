# 🎮 Match-3 Level Analyzer

**Match-3 Level Analyzer** là công cụ phân tích dữ liệu màn chơi cho các game dạng *match-3* (Candy Crush, Toon Blast...).  
Dự án sử dụng thuật toán **Greedy Solver** để mô phỏng gameplay và tính toán điểm độ khó cho từng màn chơi một cách tự động.

---

## 🌐 Demo Online
Bạn có thể trải nghiệm trực tiếp trên Hugging Face Spaces:  
🔗 **[Match-3 Analyzer Demo](https://huggingface.co/spaces/Phune23/match3-analyzer)**

---

## 🎯 Mục tiêu dự án

- **Đánh giá độ khó tự động** của từng màn chơi để cân bằng progression curve hợp lý
- **Phát hiện màn quá dễ / quá khó** trong chuỗi màn chơi để điều chỉnh kịp thời
- **Tối ưu trải nghiệm người chơi** bằng cách điều chỉnh level design dựa trên dữ liệu
- **Tiết kiệm thời gian testing** bằng việc tự động hóa quá trình phân tích

---

## ⚡ Tính năng chính

### 🧠 Thuật toán thông minh
- **Greedy Solver** mô phỏng best move selection và cascade effects
- **Efficiency scoring** tính toán hiệu suất phá block theo từng loại
- **Multi-level analysis** xử lý hàng loạt màn chơi cùng lúc

### 📊 Báo cáo chi tiết
- Xuất kết quả **CSV** với các metrics chi tiết
- **Biểu đồ trực quan** về độ khó theo progression
- **Heatmap** hiển thị các vùng khó/dễ trên grid

### 🎮 Tương thích rộng rãi
- Hỗ trợ nhiều loại block (A-Z, số, ký tự đặc biệt)
- Xử lý **obstacles** và **power-ups**
- Tương thích với format dữ liệu phổ biến

---

## 🚀 Cài đặt & Chạy

### 📋 Yêu cầu hệ thống
- Python 3.7+
- RAM: 2GB+
- Storage: 100MB+ (cho cache và output files)

### 1️⃣ Clone repository
```bash
git clone https://github.com/username/match3-level-analyzer.git
cd match3-level-analyzer
```

### 2️⃣ Cài đặt dependencies
```bash
pip install -r requirements.txt
```

Hoặc cài thủ công:
```bash
pip install streamlit pandas matplotlib numpy seaborn plotly
```

### 3️⃣ Chạy ứng dụng
```bash
streamlit run streamlit_app.py
```

### 4️⃣ Mở trình duyệt
Truy cập: `http://localhost:8501`

---

## 📋 Format dữ liệu đầu vào

### Cấu trúc CSV
File CSV cần có các cột bắt buộc sau:

| Cột | Mô tả | Ví dụ |
|-----|-------|-------|
| `LevelID` | ID màn chơi | 1, 2, 3... |
| `GridRows` | Số hàng | 8, 9, 10 |
| `GridCols` | Số cột | 8, 9, 10 |
| `Grid` | Ma trận game (text) | "A B C\nB A C\n..." |
| `MoveLimit` | Giới hạn nước đi | 20, 25, 30 |
| `BlockTypes` | Các loại block | "A,B,C,D,E" |
| `Traps` | Obstacles (optional) | "X,Y,Z" |

### Ví dụ Grid format
```
A B C A B
B A B C A  
C B A B C
A C B A B
B A C B A
```

### Sample CSV
```csv
LevelID,GridRows,GridCols,Grid,MoveLimit,BlockTypes,Traps
1,5,5,"A B C A B
B A B C A
C B A B C  
A C B A B
B A C B A",25,"A,B,C",""
2,6,6,"A B C D A B
B C D A B C
C D A B C D
D A B C D A
A B C D A B
B C D A B C",30,"A,B,C,D","X"
```

---

## 📊 Kết quả phân tích

### Output files
- **`analysis_results.csv`** → Chi tiết metrics từng màn chơi
- **`difficulty_by_level.png`** → Biểu đồ độ khó theo Level ID  
- **`efficiency_heatmap.png`** → Heatmap hiệu suất các vùng grid
- **`summary_report.txt`** → Báo cáo tổng hợp

### Metrics được tính toán
- **Difficulty Score** (0-100): Điểm độ khó tổng thể
- **Clear Efficiency**: Hiệu suất clear blocks (%)
- **Move Utilization**: Tỷ lệ sử dụng moves hiệu quả
- **Cascade Potential**: Khả năng tạo combo cascading
- **Balance Score**: Mức độ cân bằng distribution

---

## 🔧 Cấu hình nâng cao

### Tùy chỉnh thuật toán
```python
# config.py
SOLVER_CONFIG = {
    'max_depth': 3,
    'cascade_bonus': 1.5,
    'efficiency_weight': 0.7,
    'balance_threshold': 0.8
}
```

### Custom scoring weights
```python
DIFFICULTY_WEIGHTS = {
    'clear_efficiency': 0.3,
    'move_usage': 0.25, 
    'cascade_factor': 0.2,
    'grid_complexity': 0.25
}
```

## 🤝 Đóng góp

### Các cách đóng góp
1. **Bug reports**: Tạo issue với chi tiết lỗi
2. **Feature requests**: Đề xuất tính năng mới
3. **Code contributions**: Submit pull requests
4. **Documentation**: Cải thiện docs và examples

### Development setup
```bash
# Clone và setup môi trường dev
git clone https://github.com/username/match3-level-analyzer.git
cd match3-level-analyzer
pip install -r requirements-dev.txt
pre-commit install
```

### Coding standards
- Follow PEP 8
- Add docstrings cho functions
- Write unit tests cho new features
- Update README nếu cần

---

## 🆘 Troubleshooting

### Lỗi thường gặp

**Q: Import error khi chạy streamlit**
```bash
# A: Cài lại dependencies
pip uninstall streamlit pandas matplotlib
pip install streamlit pandas matplotlib --upgrade
```

**Q: CSV parsing error**
```
# A: Kiểm tra encoding và format
- File phải là UTF-8 encoding
- Grid column phải có line breaks đúng format
- Không có trailing commas
```

**Q: Out of memory với file lớn**
```
# A: Process theo batch
python analyzer.py --batch-size 50 --input large_file.csv
```

### Debug mode
```bash
streamlit run streamlit_app.py --server.enableCORS false --logger.level debug
```

---

## 📚 Tài liệu tham khảo

### Academic papers
- "Automated Difficulty Assessment in Match-3 Games" (2023)
- "Greedy Algorithms for Puzzle Game Analysis" (2022)

### Industry resources  
- King Digital Entertainment Level Design Guidelines
- Unity Match-3 Toolkit Documentation

### Related tools
- [Match-3 Generator](https://github.com/example/m3-generator)
- [Game Analytics Toolkit](https://github.com/example/game-analytics)

---

## 📧 Liên hệ & Hỗ trợ

### Author
- **Name**: Phune23  
- **Email**: phutranbs23@gmail.com
- **LinkedIn**: [Phune23](https://www.linkedin.com/in/phu-tran-bui-son-03061a315)

### Links
- **GitHub**: [match3-analyzer](https://github.com/Phune23/match3-analyzer)
- **Demo**: [match3-analyzer](https://huggingface.co/spaces/Phune23/match3-analyzer)
---

## ⭐ Ủng hộ dự án

Nếu dự án này hữu ích cho bạn:
- ⭐ **Star this repository** 
- 🐛 **Report bugs** và suggest features
- 🔄 **Share** với đồng nghiệp
- 💝 **Contribute** code hoặc documentation

**Made with ❤️ for the game development community**
