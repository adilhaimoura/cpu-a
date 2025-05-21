#!/usr/bin/env python3
# Author : "Adil Haimoura 21/05/2025"
# Just Another system information tool
# add to it info as you needed and branch it you are 100% free to use and modify
import subprocess
import re
import gi
import requests
import tempfile
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio

LOGO_URLS = {
    "intel": "https://worldvectorlogo.com/download/intel-logo.svg",
    "kingston": "https://cdnlogo.com/downloadfile.html?key=bG9nb3Mvay81Mi9raW5nc3Rvbi5zdmc%3D",
    "hewlett-packard": "https://worldvectorlogo.com/download/hp-hewlett-packard.svg",
    "nvidia": "https://upload.wikimedia.org/wikipedia/en/thumb/2/21/Nvidia_logo.svg/200px-Nvidia_logo.svg.png",
    "asrock": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/ASRock_logo.svg/200px-ASRock_logo.svg.png",
    "asus": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/ASUS_Logo.svg/200px-ASUS_Logo.svg.png",
    "msi": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0e/MSI_Logo.svg/200px-MSI_Logo.svg.png",
}

def download_logo_texture(vendor):
    for key in LOGO_URLS:
        if key in vendor.lower():
            try:
                response = requests.get(LOGO_URLS[key], timeout=5)
                response.raise_for_status()
                temp_path = os.path.join(tempfile.gettempdir(), f"{key}_logo.png")
                with open(temp_path, "wb") as f:
                    f.write(response.content)
                return Gdk.Texture.new_from_file(Gio.File.new_for_path(temp_path))  # ✅ Fixed here
            except Exception as e:
                print(f"Logo download failed for {key}: {e}")
    return None
    
class InfoTab(Gtk.Box):
    def __init__(self, title, content, vendor_hint=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_margin_start(15)
        self.set_margin_end(15)
        self.set_size_request(800, -1)

        # Left: Text content
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        label = Gtk.Label(label=content)
        label.set_wrap(True)
        label.set_xalign(0)
        label.set_hexpand(True)
        label.set_selectable(True)
        label.set_tooltip_text(content)  # ✅ Tooltip added
        text_box.append(label)

        # Right: Logo or Suggestion
        logo_texture = download_logo_texture(vendor_hint or "")
        if logo_texture:
            picture = Gtk.Picture.new_for_paintable(logo_texture)
            picture.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
            picture.set_size_request(150, 100)
            logo_box = Gtk.Box()
            logo_box.append(picture)
        else:
            suggestion = vendor_hint.lower() if vendor_hint else "unknown"
            msg = f'No logo.\nTo add:\n"{suggestion}": "URL_HERE"'
            placeholder = Gtk.Label(label=msg)
            placeholder.set_wrap(True)
            placeholder.set_size_request(150, 100)
            placeholder.set_tooltip_text("Add this key to LOGO_URLS at top of script.")
            placeholder.set_valign(Gtk.Align.CENTER)
            placeholder.set_halign(Gtk.Align.CENTER)
            logo_box = Gtk.Box()
            logo_box.append(placeholder)

        self.append(text_box)
        self.append(logo_box)

class CPUAApp(Gtk.Application):
    def on_about_activate(self, action, param):
        about_dialog = Gtk.AboutDialog(
            modal=True,
            transient_for=self.get_active_window(),
        )
        about_dialog.set_name("CPU-A")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("This tool provides a GUI for `dmidecode` and `lshw`, showing detailed hardware info in a clean, tabbed layout with vendor logos.")
        about_dialog.set_license_type(Gtk.License.MIT_X11)
        about_dialog.set_website("https://github.com/your-repo/cpu-a")
        about_dialog.set_authors(["Adil Haimoura"])
        about_dialog.show()

    def __init__(self):
        super().__init__(application_id="com.example.cpu_a")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("CPU-A")
        window.set_default_size(800, 600)
         # Header bar with menu
        header = Gtk.HeaderBar()
        window.set_titlebar(header)

        menu_button = Gtk.MenuButton()
        menu_model = Gio.Menu()
        menu_model.append("About", "app.about")
        menu = Gtk.PopoverMenu.new_from_model(menu_model)
        menu_button.set_popover(menu)
        header.pack_end(menu_button)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about_activate)
        self.add_action(action)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        window.set_child(main_box)

        info_bar = Gtk.Label(label="This program shows decoded hardware info from `dmidecode` and `lshw`.")
        info_bar.set_margin_top(10)
        info_bar.set_margin_bottom(10)
        info_bar.set_margin_start(10)
        info_bar.set_margin_end(10)
        info_bar.set_xalign(0)
        info_bar.set_css_classes(["heading"])
        main_box.append(info_bar)
        
        notebook = Gtk.Notebook()
        window.set_child(notebook)

        sections = self.get_dmidecode_sections()
        known_tabs = {
            "Processor": None,
            "Memory Device": None,
            "BIOS Information": None,
            "System Information": None,
            "Base Board Information": None,
        }

        for section_title, entries in sections.items():
            matched_key = next((k for k in known_tabs if k in section_title), None)
            if not matched_key:
                continue
            text = "\n\n".join(entries)
            vendor = self.detect_vendor(text)
            tab = InfoTab(matched_key, text, vendor)
            notebook.append_page(tab, Gtk.Label(label=matched_key))

        gpu_info, gpu_vendor = self.get_gpu_info()
        gpu_tab = InfoTab("GPU", gpu_info, gpu_vendor)
        notebook.append_page(gpu_tab, Gtk.Label(label="GPU"))

        window.present()

    def detect_vendor(self, text):
        matches = re.findall(r"endor: (.*)|Manufacturer: (.*)", text)
        for m in matches:
            vendor = m[0] or m[1]
            if vendor:
                return vendor
        return ""

    def get_gpu_info(self):
        try:
            output = subprocess.check_output(["lshw", "-C", "display"], stderr=subprocess.DEVNULL, text=True)
            details = self.parse_lshw_display(output)
            vendor = self.detect_vendor(details)
            return (details, vendor)
        except Exception:
            try:
                output = subprocess.check_output("lspci | grep -i vga", shell=True, text=True)
                return (output.strip(), output.strip())
            except Exception:
                return ("GPU info not available", "")

    def parse_lshw_display(self, text):
        entries = []
        current = []
        for line in text.splitlines():
            if line.startswith("  *-display"):
                if current:
                    entries.append("\n".join(current))
                    current = []
            current.append(line.strip())
        if current:
            entries.append("\n".join(current))
        return "\n\n".join(entries)

    def get_dmidecode_sections(self):
        try:
            output = subprocess.check_output(["sudo", "dmidecode"], text=True)
        except subprocess.CalledProcessError:
            return {"Error": ["Failed to run dmidecode."]}

        section_map = {}
        current_title = ""
        current_data = []

        for line in output.splitlines():
            if line.startswith("Handle "):
                if current_title and current_data:
                    section_map.setdefault(current_title, []).append("\n".join(current_data))
                current_title = ""
                current_data = []
            elif line.strip() and not current_title:
                current_title = line.strip()
            else:
                current_data.append(line.strip())

        if current_title and current_data:
            section_map.setdefault(current_title, []).append("\n".join(current_data))

        return section_map

if __name__ == "__main__":
    app = CPUAApp()
    app.run([])

