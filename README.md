# CPU-A

**CPU-A** is a lightweight GTK4-based GUI utility that provides detailed system hardware information similar to CPU-Z on Windows.

It uses:
- `dmidecode` to extract low-level hardware info
- `lshw` to get details about your GPU and system
- Automatically fetches and displays vendor logos (Intel, AMD, NVIDIA, etc.)
- Tabs for CPU, GPU, Memory, and Motherboard
- Classic 800px-wide UI with black-on-gray theme for clarity and nostalgia

## 🔧 Requirements

- Python 3.10+
- GTK 4 and PyGObject
- `dmidecode`, `lshw`
- Internet access (for logo downloading)

## 🔧 Install Dependencies

On Debian/Ubuntu:

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 lshw dmidecode
pip install requests

Usage
chmod +x cpu-a.py
sudo ./cpu-a.py

Make the script executable:

chmod +x cpu-a.py
./cpu-a.py
You can also rename and move it to /usr/local/bin:

sudo mv cpu-a.py /usr/local/bin/cpu-a
sudo chmod +x /usr/local/bin/cpu-a
Programmed by Adil Haimoura
free opensource utility
