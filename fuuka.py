import curses
import os
import subprocess

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Đường dẫn
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Thư mục
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # File
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Mục được chọn
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Thanh tìm kiếm

def get_search_input(stdscr, height, width):
    """Hiển thị thanh nhập liệu và lấy từ khóa tìm kiếm"""
    stdscr.clear()
    prompt = "Search: "
    stdscr.addstr(height - 1, 0, prompt, curses.color_pair(6) | curses.A_BOLD)
    curses.echo()
    search_term = stdscr.getstr(height - 1, len(prompt), width - len(prompt) - 1).decode('utf-8')
    curses.noecho()
    stdscr.clear()
    return search_term.strip()

def search_files(current_dir, search_term):
    """Tìm kiếm file/thư mục theo tên trong thư mục hiện tại"""
    all_items = os.listdir(current_dir)
    # Tìm kiếm theo tên (không phân biệt hoa thường)
    return [item for item in all_items if search_term.lower() in item.lower()]

def main(stdscr):
    # Khởi tạo curses
    curses.curs_set(0)  # Ẩn con trỏ
    if curses.has_colors():  # Kiểm tra terminal hỗ trợ màu
        init_colors()
    
    # Lấy đường dẫn hiện tại
    current_dir = os.getcwd()
    selected = 0
    show_hidden = False
    search_mode = False
    search_results = []
    
    while True:
        # Lấy danh sách file và thư mục
        if search_mode and search_results:
            items = search_results
        else:
            if show_hidden:
                items = os.listdir(current_dir)  # Hiện tất cả file, kể cả file ẩn
            else:
                items = [item for item in os.listdir(current_dir) if not item.startswith('.')]  # Ẩn file ẩn
            items.sort()
        
        # Xóa màn hình trước khi vẽ lại
        stdscr.clear()
        
        # Lấy kích thước màn hình
        height, width = stdscr.getmaxyx()
        
        # Hiển thị đường dẫn hiện tại với màu
        path_display = f">>{current_dir}"[:width-1]
        if curses.has_colors():
            stdscr.addstr(0, 0, path_display, curses.color_pair(1) | curses.A_BOLD)
        else:
            stdscr.addstr(0, 0, path_display)
        
        # Hiển thị nút "Show"
        if curses.has_colors():
            show_text = "Show"[:width-1]
            attrs = curses.color_pair(5) if selected == 0 else curses.color_pair(0) | curses.A_BOLD
            stdscr.addstr(1, 0, show_text, attrs)
            item_start_line = 2  # Bắt đầu danh sách file từ dòng 2
        else:
            stdscr.addstr(1, 0, "Show")
            item_start_line = 2
        
        # Hiển thị danh sách file/thư mục
        for i, item in enumerate(items):
            if i >= height - 3:  # Điều chỉnh giới hạn màn hình vì thêm "Show"
                break
            display_text = item[:width-1]
            attrs = 0
            if curses.has_colors():
                if i + 1 == selected:  # Điều chỉnh chỉ số selected vì thêm "Show"
                    attrs = curses.color_pair(5) | curses.A_BOLD
                elif os.path.isdir(os.path.join(current_dir, item)):
                    attrs = curses.color_pair(2)
                else:
                    attrs = curses.color_pair(3)
            stdscr.addstr(i + item_start_line, 0, display_text, attrs)
        
        # Làm mới màn hình
        stdscr.refresh()
        
        # Lấy input từ người dùng
        key = stdscr.getch()
        
        # Xử lý phím điều hướng
        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(items):
            selected += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Phím Enter
            if selected == 0:  # Nhấn Enter trên "Show"
                show_hidden = not show_hidden
                search_mode = False  # Tắt chế độ tìm kiếm khi thay đổi hiển thị
                selected = 0
                stdscr.clear()
            else:
                selected_path = os.path.join(current_dir, items[selected - 1])  # Điều chỉnh chỉ số
                if os.path.isdir(selected_path):
                    current_dir = os.path.abspath(selected_path)
                    selected = 0
                    search_mode = False  # Tắt chế độ tìm kiếm khi vào thư mục mới
                    stdscr.clear()
                elif os.path.isfile(selected_path):
                    curses.endwin()
                    subprocess.run(['micro', selected_path])
                    stdscr.clear()
                    stdscr.refresh()
        
        # Tìm kiếm bằng Ctrl+F (key 6 tương ứng với Ctrl+F trong ASCII)
        elif key == 6:
            search_term = get_search_input(stdscr, height, width)
            if search_term:
                search_results = search_files(current_dir, search_term)
                if search_results:
                    search_mode = True
                    selected = 1  # Đặt con trỏ vào kết quả đầu tiên
                else:
                    search_mode = False
            stdscr.clear()
        
        # Quay lại thư mục cha bằng phím q
        elif key == ord('q'):
            new_dir = os.path.dirname(current_dir)
            if new_dir != current_dir:
                current_dir = new_dir
                selected = 0
                search_mode = False  # Tắt chế độ tìm kiếm khi thay đổi thư mục
                stdscr.clear()
        
# Chạy chương trình
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception:
        pass