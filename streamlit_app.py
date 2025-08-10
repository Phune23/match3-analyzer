# streamlit_app.py — Match-3 Level Analyzer (Streamlit, HF Spaces friendly, smooth UI)

# ===== Writable dirs in HF Spaces =====
import os
os.environ["HOME"] = "/tmp"
os.environ["STREAMLIT_CONFIG_DIR"] = "/tmp/.streamlit"
os.environ["STREAMLIT_TELEMETRY"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["MPLCONFIGDIR"] = "/tmp/mpl"
os.makedirs("/tmp/.streamlit", exist_ok=True)
os.makedirs("/tmp/mpl", exist_ok=True)
with open("/tmp/.streamlit/config.toml", "w") as f:
    f.write("[server]\nheadless = true\nenableCORS = false\nenableXsrfProtection = false\nport = 8501\n")

# ===== Imports =====
import csv, io, random
from typing import List, Tuple
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# =================== Core match-3 ===================
def parse_grid(grid_text: str, rows: int, cols: int) -> list[list[str]]:
    lines = [ln.strip() for ln in (grid_text or "").strip().splitlines() if ln.strip()]
    grid: list[list[str]] = []
    for ln in lines:
        parts = [p.strip() for p in ln.split() if p.strip()]
        grid.append(parts)
    if len(grid) != int(rows) or any(len(r) != int(cols) for r in grid):
        raise ValueError(f"Grid size mismatch: expected {rows}x{cols}")
    return grid

def validate_grid_symbols(grid: list[list[str]], alphabet: list[str]) -> None:
    ok = set(alphabet)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val not in ok:
                raise ValueError(f"Invalid symbol '{val}' at ({r},{c}); allowed: {sorted(ok)}")

def clone_grid(g: list[list[str]]) -> list[list[str]]:
    return [row[:] for row in g]

def find_matches(grid: list[list[str]]) -> list[tuple[int,int]]:
    R, C = len(grid), len(grid[0])
    matched = [[False]*C for _ in range(R)]
    # horizontal
    for r in range(R):
        c = 0
        while c < C:
            k = c+1
            while k < C and grid[r][k] == grid[r][c]:
                k += 1
            if k - c >= 3:
                for x in range(c, k): matched[r][x] = True
            c = k
    # vertical
    for c in range(C):
        r = 0
        while r < R:
            k = r+1
            while k < R and grid[k][c] == grid[r][c]:
                k += 1
            if k - r >= 3:
                for x in range(r, k): matched[x][c] = True
            r = k
    return [(r,c) for r in range(R) for c in range(C) if matched[r][c]]

def apply_gravity_and_refill(grid: list[list[str]], alphabet: list[str], rng: random.Random) -> int:
    matched = find_matches(grid)
    if not matched: return 0
    for r,c in matched: grid[r][c] = None
    cleared = len(matched)
    R, C = len(grid), len(grid[0])
    for c in range(C):
        write_r = R-1
        for r in range(R-1, -1, -1):
            if grid[r][c] is not None:
                grid[write_r][c] = grid[r][c]; write_r -= 1
        for r in range(write_r, -1, -1):
            grid[r][c] = rng.choice(alphabet)
    return cleared

def all_adjacent_swaps(grid: list[list[str]]) -> list[tuple[tuple[int,int],tuple[int,int]]]:
    R, C = len(grid), len(grid[0]); moves = []
    for r in range(R):
        for c in range(C):
            if c+1 < C: moves.append(((r,c),(r,c+1)))
            if r+1 < R: moves.append(((r,c),(r+1,c)))
    return moves

def swap(g, a, b):
    (r1,c1),(r2,c2) = a,b
    g[r1][c1], g[r2][c2] = g[r2][c2], g[r1][c1]

def simulate_one_move(grid: list[list[str]], alphabet: list[str], rng: random.Random, max_cascades: int = 5):
    g = clone_grid(grid)
    best_score, best_move, best_grid = 0, None, None
    for a,b in all_adjacent_swaps(g):
        gg = clone_grid(g); swap(gg, a, b)
        total_cleared = 0
        for _ in range(max_cascades):
            cleared = apply_gravity_and_refill(gg, alphabet, rng)
            if cleared == 0: break
            total_cleared += cleared
        if total_cleared > best_score:
            best_score, best_move, best_grid = total_cleared, (a,b), gg
    if best_move is None: return grid, 0, None
    return best_grid, best_score, best_move

def greedy_solver(grid: list[list[str]], move_limit: int, alphabet: list[str], rng: random.Random, max_cascades: int):
    total_cleared, steps = 0, 0
    g = clone_grid(grid)
    for _ in range(int(move_limit)):
        g, cleared, mv = simulate_one_move(g, alphabet, rng, max_cascades)
        if mv is None: break
        total_cleared += cleared; steps += 1
    R, C = len(grid), len(grid[0])
    efficiency = total_cleared / float(R*C) if R*C > 0 else 0.0
    return {"steps_used": steps, "total_cleared": total_cleared, "efficiency": efficiency, "final_grid": g}

def compute_difficulty(block_types: int, traps: int, move_limit: int, efficiency: float) -> float:
    eff = max(0.0, min(1.0, float(efficiency)))
    return round(1.5*block_types + 3.0*traps - (move_limit/5.0) + (1.0 - eff)*5.0, 2)

def run_on_csv_bytes(csv_bytes: bytes, seed: int = 42, max_cascades: int = 5) -> pd.DataFrame:
    rng = random.Random(seed)
    text = csv_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    results = []
    for row in reader:
        level_id = (row.get("LevelID") or "").strip()
        grid_text = (row.get("Grid") or "").strip()
        rows = int(row.get("GridRows") or 0)
        cols = int(row.get("GridCols") or 0)
        move_limit = int(row.get("MoveLimit") or 10)
        block_types = int(row.get("BlockTypes") or 3)
        traps = int(row.get("Traps") or 0)
        alphabet = [chr(ord("A")+i) for i in range(max(1, block_types))]
        efficiency = 0.0; steps_used = 0; total_cleared = 0
        if grid_text:
            grid = parse_grid(grid_text, rows, cols)
            validate_grid_symbols(grid, alphabet)
            sim = greedy_solver(grid, move_limit, alphabet, rng, max_cascades)
            efficiency = sim["efficiency"]; steps_used = sim["steps_used"]; total_cleared = sim["total_cleared"]
        diff = compute_difficulty(block_types, traps, move_limit, efficiency)
        results.append({
            "LevelID": level_id, "Rows": rows, "Cols": cols,
            "MoveLimit": move_limit, "BlockTypes": block_types, "Traps": traps,
            "Efficiency": round(efficiency, 3), "StepsUsed": steps_used,
            "TotalCleared": total_cleared, "DifficultyScore": diff
        })
    def keyf():
        def inner(d):
            try: return int(d["LevelID"])
            except: return 10**9
        return inner
    results.sort(key=keyf())
    return pd.DataFrame(results)

# =================== UI ===================
SAMPLE_CSV = """LevelID,GridRows,GridCols,Grid,MoveLimit,BlockTypes,Traps,Objectives,Notes
1,5,5,"A B C A B
B A B C A
C B A B C
A C B A B
B A C B A",18,3,0,"Clear 30 cells","Intro level"
2,6,6,"A A B C D E
B C D E A B
C D E A B C
D E A B C D
E A B C D E
A B C D E A",20,5,1,"Reach 5000 points","Adds traps"
"""

st.set_page_config(page_title="Match-3 Level Analyzer", layout="wide")

# ==== Global CSS: ổn định viewport & bảng/đồ thị (anti-jitter) ====
st.markdown("""
<style>
/* Cỡ chữ nhẹ + line-height cho bảng */
html, body, [data-testid="stAppViewContainer"] { font-size: 17px !important; }
[data-testid="stDataFrame"] div[role="columnheader"],
[data-testid="stDataFrame"] div[role="gridcell"] {
  line-height: 1.6rem !important;
  padding-top: 6px !important;
  padding-bottom: 6px !important;
  font-size: 0.98rem !important;
}
[data-testid="stDataFrame"] div[role="columnheader"] p { white-space: nowrap !important; }

/* ——— Anti-jitter cho toàn trang ——— */
html, body { scrollbar-gutter: stable both-edges; overflow-y: scroll; } /* giữ chỗ cố định cho scrollbar dọc */
[data-testid="stAppViewContainer"] { overflow-x: clip; }                 /* chặn overflow ngang toàn cục */
.block-container { max-width: 1200px; margin: 0 auto; }                 /* khóa bề rộng hợp lý, tránh “chạm ngưỡng” */
* { transition-property: none !important; }                              /* tránh rung do transition width/left */

/* Wrapper cuộn ngang cục bộ cho bảng */
.table-wrap { overflow-x: auto; overscroll-behavior: contain; scrollbar-gutter: stable both-edges; }
.table-wrap [data-testid="stDataFrame"], .table-wrap table { white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

st.title("🎮 Match-3 Level Analyzer")

# Keep state
if "csv_bytes" not in st.session_state: st.session_state["csv_bytes"] = None
if "df" not in st.session_state: st.session_state["df"] = None

@st.cache_data(show_spinner=False)
def cached_run(csv_bytes: bytes, seed: int, max_cascades: int):
    return run_on_csv_bytes(csv_bytes, seed=seed, max_cascades=max_cascades)

# ---- Controls in a form (rerun only when submit) ----
with st.form("controls"):
    c1, c2 = st.columns([1,2])
    with c1:
        st.subheader("1) Input")
        seed = st.number_input("Random seed", value=42, step=1)
        max_cascades = st.number_input("Max cascades per move", value=5, min_value=1, max_value=20, step=1)

        tab_up, tab_sample = st.tabs(["Upload CSV", "Use Sample"])
        with tab_up:
            uploaded = st.file_uploader("Upload levels CSV", type=["csv"])
            if uploaded:
                st.session_state["csv_bytes"] = uploaded.read()
                st.success("CSV uploaded.")
        with tab_sample:
            if st.form_submit_button("Use sample CSV"):
                st.session_state["csv_bytes"] = SAMPLE_CSV.encode("utf-8")
                st.info("Using sample CSV.")

    with c2:
        st.subheader("2) Results (Press Run)")

    submitted = st.form_submit_button("▶️ Run Analysis")

# ---- Run / Render ----
if submitted and st.session_state["csv_bytes"]:
    try:
        st.session_state["df"] = cached_run(
            st.session_state["csv_bytes"], int(seed), int(max_cascades)
        )
    except Exception as e:
        st.error(f"Error: {e}")

if st.session_state["df"] is not None:
    df = st.session_state["df"].copy()

    # Pretty table to avoid overlapping text
    df_display = df.copy()
    df_display["EfficiencyPct"] = (df_display["Efficiency"].clip(upper=1.0) * 100).round(1)

    col_config = {
        "LevelID": st.column_config.NumberColumn("Level", format="%d", width="small"),
        "Rows": st.column_config.NumberColumn("Rows", width="small"),
        "Cols": st.column_config.NumberColumn("Cols", width="small"),
        "MoveLimit": st.column_config.NumberColumn("Moves", width="small"),
        "BlockTypes": st.column_config.NumberColumn("Types", width="small"),
        "Traps": st.column_config.NumberColumn("Traps", width="small"),
        "EfficiencyPct": st.column_config.NumberColumn("Efficiency (%)", format="%.1f", width="small"),
        "StepsUsed": st.column_config.NumberColumn("Steps", width="small"),
        "TotalCleared": st.column_config.NumberColumn("Cleared", width="medium"),
        "DifficultyScore": st.column_config.NumberColumn("Difficulty", format="%.2f", width="small"),
    }

    # === Ổn định bảng: bọc wrapper & tắt auto-fit container ===
    st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
    st.data_editor(
        df_display[[
            "LevelID","Rows","Cols","MoveLimit","BlockTypes","Traps",
            "EfficiencyPct","StepsUsed","TotalCleared","DifficultyScore"
        ]],
        hide_index=True,
        use_container_width=False,  # tránh loop co giãn
        height=440,
        column_config=col_config,
        disabled=True,              # chỉ đọc
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button(
        "⬇️ Download analysis_results.csv",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="analysis_results.csv",
        mime="text/csv",
    )

    # === Biểu đồ: kích thước cố định + không auto-fit container ===
    try:
        xs = df["LevelID"].astype(int).tolist()
        ys = df["DifficultyScore"].tolist()
        fig, ax = plt.subplots(figsize=(9, 4))  # cố định size để tránh giật
        ax.plot(xs, ys, marker="o")
        ax.set_xlabel("Level"); ax.set_ylabel("Difficulty Score"); ax.set_title("Difficulty by Level")
        st.pyplot(fig, use_container_width=False)

        png_out_path = "/tmp/difficulty_by_level.png"
        fig.savefig(png_out_path, dpi=160, bbox_inches="tight")
        with open(png_out_path, "rb") as fp:
            st.download_button(
                "⬇️ Download difficulty_by_level.png",
                data=fp.read(),
                file_name="difficulty_by_level.png",
                mime="image/png",
            )
    except Exception:
        st.warning("LevelID is not numeric; skipping chart.")
elif submitted and not st.session_state["csv_bytes"]:
    st.warning("Please upload a CSV or click 'Use sample CSV' before running.")

# --- About & How-to (Tiếng Việt) ---
with st.expander("ℹ️ Giới thiệu & Hướng dẫn sử dụng"):
    st.markdown("""
### 🎯 Match-3 Level Analyzer là gì?
Công cụ mô phỏng giải màn chơi match-3 bằng **greedy solver** (mỗi lượt chọn swap xóa được nhiều ô nhất, có tính **cascades**)
và tính **điểm độ khó** dựa trên thông tin level trong CSV.
### 🧪 Cách dùng nhanh
1. Ở panel bên trái, **Upload CSV** của bạn **hoặc** bấm **Use sample CSV** để dùng dữ liệu mẫu.
2. (Tuỳ chọn) Chỉnh **Random seed** và **Max cascades per move**.
3. Bấm **▶️ Run Analysis** để chạy.
4. Xem **bảng kết quả** và **biểu đồ độ khó**.
5. Bấm **Download** để tải **analysis_results.csv** (và PNG biểu đồ nếu cần).
### 📄 Định dạng CSV (tối thiểu)
- **LevelID**: mã màn chơi (nên để số để vẽ biểu đồ theo thứ tự).
- **GridRows, GridCols**: số hàng/cột.
- **Grid**: text nhiều dòng, mỗi dòng là một hàng; **các ô cách nhau bằng dấu cách** (ví dụ: `"A B C"`).
- **MoveLimit**: số bước cho phép.
- **BlockTypes**: số loại ký hiệu (A, B, C, …).
- **Traps**: số lượng bẫy (hiện dùng như tín hiệu tăng độ khó).
**Ví dụ ô Grid (5x5):**
A B C A B
B A B C A
C B A B C
A C B A B
B A C B A
### 📊 Công thức điểm độ khó (heuristic)
Difficulty = 1.5×BlockTypes + 3.0×Traps − (MoveLimit/5)
+ (1 − clamp(Efficiency, 0..1))×5
- Nhiều **BlockTypes** và **Traps** → **khó** hơn  
- **MoveLimit** cao → **dễ** hơn  
- **Efficiency** (tỷ lệ ô xoá được trong giới hạn bước) **thấp** → **khó** hơn
### 🤝 Gợi ý dùng trong review
- So sánh **DifficultyScore** giữa các màn để phát hiện màn **quá dễ/khó**.
- Kết hợp **StepsUsed / TotalCleared** để xem hành vi agent greedy.
- Tải **CSV kết quả** và **biểu đồ** để chia sẻ với đội thiết kế/cân bằng.
""")