#!/usr/bin/python3
import tkinter as tk
import subprocess
from time import sleep
from threading import Thread

fan_control_enabled = 'enabled'

def get_info():
    info_lines = subprocess.check_output("sensors").decode("utf-8").split("\n")
    result = []
    count = 0
    global fan_control_enabled
    for i in info_lines:
        if "Core" in i:
            result.append("Core %d: " % count +
                          i.split(":")[-1].split("(")[0].strip())
            count += 1

        if "fan" in i:
            result.append("Fan: " + i.split(":")[-1].strip())

    info_lines = subprocess.check_output(
        'sudo cat "/proc/acpi/ibm/fan"',
        shell=True).decode("utf-8").split("\n")
    for i in info_lines:
        if "status" in i:
            fan_control_enabled = i.split(":")[-1].strip()
            #print(fan_control_enabled == 'enabled')
            result.append("Status: " + fan_control_enabled)
    return result


def set_speed(speed=None):
    """
    Set speed of fan by changing level at /proc/acpi/ibm/fan
    speed: 0-7, auto, disengaged, full-speed
    """
    #print("set level to %r" % speed)
    return subprocess.check_output(
        'echo level {0} | sudo tee "/proc/acpi/ibm/fan"'.format(speed),
        shell=True).decode()

def toggle_fan_enabled():
    global fan_control_enabled
    fan_control_enabled = ('disabled'
                           if fan_control_enabled == 'enabled' else 'enabled')
    return subprocess.check_output(
        'echo {0} | sudo tee "/proc/acpi/ibm/fan"'.format(fan_control_enabled),
        shell=True).decode()


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.minsize(width=200, height=300)
        self.is_running = True
        global fan_control_enabled
        get_info()

        main_label = tk.Label(parent, text="")
        main_label.grid(row=0, column=0)

        row1 = tk.Frame()
        row1.grid()
        for i in range(8):
            tk.Button(row1, text=str(i),
                      command=lambda x=i: set_speed(x)).grid(row=0,
                                                             column=i + 1)

        row2 = tk.Frame()
        row2.grid()

        def exit_safely():
            self.is_running = False
            quit()

        def display_loop():
            while self.is_running:
                sleep(0.5)
                main_label["text"] = "\n".join(get_info())

        def refresh_control_btn(self):
            global fan_control_enabled
            toggle_fan_enabled()
            self.control_btn.configure(text=(
                'Disable' if fan_control_enabled == 'enabled' else 'Enable'))

        t = Thread(target=display_loop)
        t.setDaemon(True)
        t.start()

        self.control_btn = tk.Button(
            row2,
            text=('Disable' if fan_control_enabled == 'enabled' else 'Enable'),
            command=lambda: refresh_control_btn(self))
        self.control_btn.grid(row=0, column=0)

        tk.Button(row2, text="Auto",
                  command=lambda: set_speed("auto")).grid(row=0, column=1)
        tk.Button(row2, text="Full",
                  command=lambda: set_speed("full-speed")).grid(row=0,
                                                                column=2)
        tk.Button(row2, text="Exit",
                  command=lambda: exit_safely()).grid(row=0, column=3)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Thinkfan Control")
    MainApplication(root).grid()
    root.mainloop()
