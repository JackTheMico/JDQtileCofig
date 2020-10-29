# -*- coding: utf-8 -*-
import os
import re
import subprocess
import socket

from libqtile import bar, hook, layout
from libqtile.command import lazy
from libqtile.config import Drag, Group, Key, Screen, ScratchPad, DropDown, Match
from libqtile.widget import (Battery, BatteryIcon, Clock, CurrentLayout, CurrentLayoutIcon,
                             GroupBox, Notify, Prompt, Sep, Systray, TaskList,
                             TextBox, LaunchBar, Wallpaper, Cmus, Pacman, 
                             # ImapWidget
                             )
# from libqtile.extension.dmenu import DmenuRun
from libqtile.extension.window_list import WindowList
from libqtile.extension import CommandSet

DEBUG = os.environ.get("DEBUG")
HOME = os.path.expanduser("~") + "/"

GREY = "#444444"
DARK_GREY = "#333333"
BLUE = "#007fcf"
DARK_BLUE = "#005083"
ORANGE = "#dd6600"
DARK_ORANGE = "#582c00"


def window_to_prev_group():
    @lazy.function
    def __inner(qtile):
        i = qtile.groups.index(qtile.currentGroup)
        if qtile.currentWindow and i != 0:
            group = qtile.groups[i - 1].name
            qtile.currentWindow.togroup(group)

    return __inner


def window_to_next_group():
    @lazy.function
    def __inner(qtile):
        i = qtile.groups.index(qtile.currentGroup)
        if qtile.currentWindow and i != len(qtile.groups):
            group = qtile.groups[i + 1].name
            qtile.currentWindow.togroup(group)

    return __inner


def window_to_prev_screen():
    @lazy.function
    def __inner(qtile):
        i = qtile.screens.index(qtile.currentScreen)
        if i != 0:
            group = qtile.screens[i - 1].group.name
            qtile.currentWindow.togroup(group)

    return __inner


def window_to_next_screen():
    @lazy.function
    def __inner(qtile):
        i = qtile.screens.index(qtile.currentScreen)
        if i + 1 != len(qtile.screens):
            group = qtile.screens[i + 1].group.name
            qtile.currentWindow.togroup(group)

    return __inner


def switch_screens():
    @lazy.function
    def __inner(qtile):
        i = qtile.screens.index(qtile.currentScreen)
        group = qtile.screens[i - 1].group
        qtile.currentScreen.setGroup(group)

    return __inner


@hook.subscribe.client_new
def set_floating(window):
    floating_types = ["notification", "toolbar", "splash", "dialog"]
    floating_roles = ["EventDialog", "Msgcompose", "Preferences"]
    floating_names = ["Terminator Preferences", "首选项", "设置", "scrcpy"]

    def judgeby_names(window_name):
        for name in floating_names:
            if name in window_name:
                return True

    if (window.window.get_wm_type() in floating_types
            or window.window.get_wm_window_role() in floating_roles
            or judgeby_names(window.window.get_name())
            or window.window.get_wm_transient_for()):
        window.floating = True


def init_keys():
    keys = [
        Key([mod], "p", lazy.screen.prev_group(skip_managed=True)),
        Key([mod], "n", lazy.screen.next_group(skip_managed=True)),
        # Key([mod, "shift"], "Left", window_to_prev_group()),
        # Key([mod, "shift"], "Right", window_to_next_group()),
        # Key([mod, "mod1"], "Left", lazy.prev_screen()),
        # Key([mod, "mod1"], "Right", lazy.next_screen()),
        # Key([mod, "shift", "mod1"], "Left", window_to_prev_screen()),
        # Key([mod, "shift", "mod1"], "Right", window_to_next_screen()),
        # Key([mod, "shift"], "t", switch_screens()),
        # Key([mod, "shift"], "l", lazy.group.next_window()),
        # Key([mod, "shift"], "h", lazy.group.prev_window()),
        Key([mod], "space", lazy.next_layout()),
        Key([mod], "h", lazy.layout.left()),
        Key([mod], "j", lazy.layout.up()),
        Key([mod], "k", lazy.layout.down()),
        Key([mod], "l", lazy.layout.right()),
        Key([mod], "bracketleft", lazy.layout.swap_left()),
        Key([mod], "bracketright", lazy.layout.swap_right()),
        Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
        Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
        Key([mod, "shift"], "h", lazy.layout.shuffle_left()),
        Key([mod, "shift"], "l", lazy.layout.shuffle_right()),
        Key([mod, "control"], "j", lazy.layout.grow_down()),
        Key([mod, "control"], "k", lazy.layout.grow_up()),
        Key([mod, "control"], "h", lazy.layout.grow_left()),
        Key([mod, "control"], "l", lazy.layout.grow_right()),
        Key([mod, "control"], "n", lazy.layout.normalize()),
        Key([mod], "o", lazy.layout.maximize()),
        # Key([mod, "shift"], "space", lazy.layout.flip()),
        Key([mod], "Return", lazy.layout.toggle_split()),
        # Key([mod], "Return", lazy.spawn(terminal)),
        Key([mod], "f", lazy.window.toggle_floating()),
        Key([mod], "r", lazy.spawncmd()),
        # yaourt i3lock
        Key([mod],"BackSpace", lazy.spawn("i3lock -i /home/dlwxxxdlw/Pictures/wallpapers/2.png")),
        Key([mod], "u", lazy.spawn(browser_chromium)),
        # Key([mod], "x", lazy.spawn(browser_firefox)),
        Key([mod], "m", lazy.spawn(package_manager)),
        Key([mod], "b", lazy.spawn(file_manager)),
        Key([mod], "x", lazy.window.kill()),
        Key([mod, "control"], "r", lazy.restart()),
        Key([mod, "control"], "q", lazy.shutdown()),
        Key([mod, "control"], "c", lazy.spawn(rofi_run)),
        Key([mod, "control"], "w", lazy.spawn(rofi_window)),
        # Key([mod, "shift"], 'r', lazy.run_extension(DmenuRun(
        #     dmenu_prompt=">",
        #     dmenu_font="DejaVu Sans Mono,14",
        #     background="#15181a",
        #     foreground="#00ff00",
        #     selected_background="#079822",
        #     selected_foreground="#fff",
        #     # dmenu_height=24,  # Only supported by some dmenu forks
        # ))),
        # Key([mod, "control"], 'm', lazy.run_extension(CommandSet(
        #     commands={
        #         'play': 'cmus-remote -p',
        #         'pause': 'cmus-remote -u',
        #         'stop': 'cmus-remote -s',
        #         'prev': 'cmus-remote -r',
        #         'next': 'cmus-remote -n',
        #         'repeat': 'cmus-remote -R',
        #         'shuffle': 'cmus-remote -S',
        #         '5up': 'cmus-remote -v +5%',
        #         '5down': 'cmus-remote -v -5%',
        #         '10down': 'cmus-remote -v -10%',
        #         '10up': 'cmus-remote -v +10%',
        #         '15up': 'cmus-remote -v +15%',
        #         '15down': 'cmus-remote -v -15%',
        #         '20down': 'cmus-remote -v -20%',
        #         '20up': 'cmus-remote -v +20%',
        #     }
        # ))),
        Key([mod, "control"], 'p', lazy.run_extension(CommandSet(
            commands={
                'shutdown': 'ps aux|grep "picom"|grep -v grep|awk "{print $2}"|xargs kill -9',
                '90': 'picom -bc --active-opacity 0.9',
                '85': 'picom -bc --active-opacity 0.85',
                '80': 'picom -bc --active-opacity 0.8',
                '75': 'picom -bc --active-opacity 0.75',
                '70': 'picom -bc --active-opacity 0.7',
                '65': 'picom -bc --active-opacity 0.65',
                '60': 'picom -bc --active-opacity 0.6',
                '55': 'picom -bc --active-opacity 0.55',
                '50': 'picom -bc --active-opacity 0.5',
            }
        ))),
        # Key([mod, "shift"], 'w', lazy.run_extension(WindowList(
        #     dmenu_prompt=">",
        #     dmenu_font="DejaVu Sans Mono,14",
        #     background="#15181a",
        #     foreground="#00ff00",
        #     selected_background="#079822",
        #     selected_foreground="#fff",
        # ))),
        # region this "scrot" app can use -s to select an area of screen
        # Key([], "Print", lazy.spawn("scrot")),
        # Key([mod], "s", lazy.spawn("scrot -s '%Y-%m-%d_$wx$h.png' -e 'mv $f /home/dlwxxxdlw/Screenshots/'")),
        # Key([mod, "control"], "s", lazy.spawn("scrot -s '/mnt/d/Jack\ Deng/Documents/org/screenshots/%Y-%m-%d_$wx$h.png'")),
        Key([mod], "s", lazy.spawn("scrot '/mnt/d/Jack\ Deng/Documents/org/screenshots/%Y-%m-%d_$wx$h.png'")),
        # Key([], "Scroll_Lock", lazy.spawn(HOME + ".local/bin/i3lock -d")),
        # endregion
        # Key([mod], "Delete", lazy.spawn("amixer set Master toggle")),
        # Key([mod], "Prior", lazy.spawn("amixer set Master 5+")),
        # Key([mod], "Next", lazy.spawn("amixer set Master 5-")),
        # Key([mod], "Insert",
        #     lazy.spawn(HOME + ".local/bin/spotify-dbus playpause")),
        # Key([mod], "End", lazy.spawn(HOME + ".local/bin/spotify-dbus next")),
        # Key([mod], "Home",
        #     lazy.spawn(HOME + ".local/bin/spotify-dbus previous")),
    ]
    if DEBUG:
        keys += [
            Key(["mod1"], "Tab", lazy.layout.next()),
            Key(["mod1", "shift"], "Tab", lazy.layout.previous())
        ]
    return keys


def init_mouse():
    return [
        Drag(
            [mod],
            "Button1",
            lazy.window.set_position_floating(),
            start=lazy.window.get_position()),
        Drag(
            [mod],
            "Button3",
            lazy.window.set_size_floating(),
            start=lazy.window.get_size())
    ]


def init_groups():
    def _inner(key, name):
        keys.append(Key([mod], key, lazy.group[name].toscreen()))
        keys.append(Key([mod, "control"], key, lazy.window.togroup(name)))
        if name == "01":
            if not is_running("alacritty"):
                return Group(name, spawn="alacritty")
        elif name == "02":
            if not is_running("emacs"):
                return Group(name, spawn="emacs")
        elif name == "12":
            if not is_running("clashy"):
                return Group(name, spawn="clashy")
        # elif name == "03":
        #     if not is_running("chromium"):
        #         return Group(name, spawn="chromium")
        # elif name == "12":
        #     if not is_running("switchhosts"):
        #         return Group(name, spawn="switchhosts")
        # elif name == "12":
        #     if not is_running("trojan-qt5"):
        #         return Group(name, spawn="trojan-qt5")
        return Group(name)

    # groups = [("dead_grave", "00")]
    groups = [(str(i), "0" + str(i)) for i in range(1, 10)]
    groups += [("0", "10"), ("minus", "11"), ("equal", "12")]
    res_groups = [_inner(*i) for i in groups]
    res_groups += [
        ScratchPad("scratchpad",
                   [DropDown("scratch", "alacritty", height=0.55, opacity=0.35)])
    ]
    keys.append(
        Key([mod], "d", lazy.group["scratchpad"].dropdown_toggle("scratch")))
    return res_groups


def init_floating_layout():
    return layout.Floating(border_focus=BLUE)


def init_widgets():
    prompt = "{0}@{1}: ".format(os.environ["USER"], hostname)
    widgets = [
        Prompt(
            prompt=prompt,
            font="DejaVu Sans Mono for Powerline Bold",
            padding=10,
            background=GREY),
        TextBox(
            text="◤",
            fontsize=25,
            padding=-1,
            foreground=ORANGE,
            background=DARK_GREY),
        CurrentLayout(),
        CurrentLayoutIcon(scale=0.6, padding=-4),
        TextBox(text=" ", padding=2),
        GroupBox(
            fontsize=12,
            font="DejaVu Sans Mono for Powerline Bold",
            padding=4,
            borderwidth=1,
            urgent_border=DARK_BLUE,
            disable_drag=True,
            highlight_method="block",
            this_screen_border=DARK_BLUE,
            other_screen_border=DARK_ORANGE,
            this_current_screen_border=BLUE,
            other_current_screen_border=ORANGE),
        TextBox(
            text="◤",
            fontsize=25,
            padding=-1,
            foreground=ORANGE,
            background=GREY),
        TaskList(
            fontsize=13,
            font="DejaVu Sans Mono for Powerline Bold",
            borderwidth=0,
            highlight_method="block",
            background=GREY,
            border=BLUE,
            urgent_border=DARK_BLUE),
        Cmus(
            fontsize=13,
            font="DejaVu Sans Mono for Powerline Bold",
        ),
        # ImapWidget(
        #     server="imap.si-tech.com.cn",
        #     font="DejaVu Sans Mono for Powerline Bold",
        #     fontsize=13,
        #     update_interval=360,
        #     user="denglw@si-tech.com.cn"
        # ),
        # Pacman(
        #     fontsize=13,
        #     font="DejaVu Sans Mono for Powerline Bold",
        # ),
        Systray(background=DARK_ORANGE),
        Wallpaper(
            directory="/home/dlwxxxdlw/Pictures/wallpapers",
            fontsize=13,
            font="DejaVu Sans Mono for Powerline Bold",
            label="(´･_･`)",
            random_selection=True,
            wallpaper_command=['feh', '--bg-max']
        ),
        # LaunchBar needs some dependencies, use yaourt to install them
        # LaunchBar(
        #     progs=[
            # (  # yaourt thunderbird virtualbox
            #     'thunderbird', 'thunderbird', 'launch thunderbird'),
            # ('virtualbox', 'virtualbox', 'launch virtualbox'),
                # ('thunar', 'thunar', 'launch thunar'),
                # ('terminator', 'terminator', 'launch terminator'),
            # (
            #     'aria',  # get this from github
            #     'firefox --new-tab ~/Downloads/aria-ng/index.html',
            #     'aria'),
            # ('shutter', 'shutter', 'launch shutter'),
                # ('ss', 'ss-qt5', 'launch shadowsocks-qt5'),
            # ('Tim', '/opt/deepinwine/apps/Deepin-TIM/run.sh', 'launch Tim'),
            # ('Thunder', '/opt/deepinwine/apps/Deepin-ThunderSpeed/run.sh', 'launch Thunder')
            # ],
            # fontsize=13,
            # font="DejaVu Sans Mono for Powerline Bold",
                  # ),
        TextBox(
            text="◤",
            fontsize=25,
            padding=-1,
            foreground=ORANGE,
            background=DARK_GREY),
        # TextBox(text=" ⚠", foreground=BLUE, fontsize=18),
        Notify(
            fontsize=16,
            font="DejaVu Sans Mono for Powerline Bold",
            background=BLUE
        ),
        # TextBox(
        #     text="⌚", 
        #     foreground=BLUE, 
        #     fontsize=16,
        #     font="DejaVu Sans Mono for Powerline Bold",
        # ),
        Clock(
            fontsize=13,
            font="DejaVu Sans Mono for Powerline Bold",
            format="%A %d-%m-%Y %H:%M"
        )
    ]
    if hostname in ("spud", "saiga"):
        widgets[-2:-2] = [
            TextBox(text=" ↯", foreground=BLUE, fontsize=14),
            Battery(update_delay=2)
        ]
    if DEBUG:
        widgets += [Sep(), CurrentLayout()]
    return widgets


def init_top_bar():
    return bar.Bar(widgets=init_widgets(), size=22, opacity=1)


def init_widgets_defaults():
    return dict(font="DejaVu", fontsize=11, padding=2, background=DARK_GREY)


def init_screens(num_screens):
    for _ in range(num_screens - 1):
        screens.insert(0, Screen())


def init_layouts(num_screens):
    margin = 0
    if num_screens > 1:
        margin = 8
    layouts.extend([
        layout.Tile(
            ratio=0.5,
            margin=margin,
            border_focuts="#ff0000",
            border_width=4,
            border_normal="#111111",
            border_focus=BLUE)
    ])


# very hacky, much ugly
def main(qtile):
    num_screens = len(qtile.conn.pseudoscreens)
    init_screens(num_screens)
    init_layouts(num_screens)


def is_running(process):
    if "nohup" in process:
        index = process.index(">")
        process = process[6:index]
    s = subprocess.Popen(["ps", "axuw"], stdout=subprocess.PIPE)
    for x in s.stdout:
        if re.search(process, x.decode()):
            return True
    return False


def execute_once(process):
    """
    execute a application once
    :Keyword Arguments:
     process -- application
    :return: None
    """
    if not is_running(process):
        return subprocess.Popen(process.split())


@hook.subscribe.startup
def startup():
    """
    start the applications when qtile startup
    :return: None
    """
    # execute_once("nm-applet")  # yaourt network manager applet
    # execute_once("fcitx &")  # yaourt fcitx
    execute_once("picom -bc --active-opacity 0.8")
    # execute_once("nohup clash >> /dev/null &")
    # execute_once("nohup ss-local -c /home/dlwxxxdlw/.config/shadowsocks/bandwagong.json start > /dev/null 2>ss-local.log &")
    # execute_once("nohup ss-local -c /home/dlwxxxdlw/.config/shadowsocks/config.json start > /dev/null 2>ss-local.log &")
    # execute_once("privoxy /home/dlwxxxdlw/.config/privoxy/config")
    # execute_once("nohup albert > /dev/null 2>albert.log &")
    # execute_once("ss-qt5")
    # execute_once("aria2c --conf-path=/home/dlwxxxdlw/.config/aria2/aria2.conf")
    # execute_once("source /home/dlwxxxdlw/.bashrc")
    pass


if __name__ in ["config", "__main__"]:
    if HOME + ".local/bin" not in os.environ["PATH"]:
        os.environ["PATH"] = HOME + ".local/bin:{}".format(os.environ["PATH"])

    mod = "mod3"
    # mod = "mod1"
    browser_chromium = "chromium"  # yaourt chromium
    browser_firefox = "firefox"  # yaourt firefox
    # terminal = "roxterm"  # yaourt roxterm
    terminal = "alacritty"  # yaourt roxterm
    package_manager = "octopi"
    file_manager = "nautilus"
    rofi_run = "rofi -show run"
    rofi_window = "rofi -show window"
    hostname = socket.gethostname()
    # follow_mouse_focus = True # not sure what this means
    # never set "cursor_warp" True ,it will make your mouse
    # back to screen center when you clicked in the virtualbox
    cursor_warp = False

    keys = init_keys()
    mouse = init_mouse()
    # not sure what this means yet
    # focus_on_window_activation = "smart"
    groups = init_groups()
    floating_layout = init_floating_layout()
    layouts = [
        layout.Max(),
        layout.Bsp(
            border_focuts="#ff0000",
            border_width=4,
        ),
        layout.MonadTall(
            border_focuts="#ff0000",
            border_width=4,
        ),
        layout.Matrix(
            border_focuts="#ff0000",
            border_width=4,
        ),
    ]
    screens = [Screen(top=init_top_bar())]
    widget_defaults = init_widgets_defaults()
    # region don't know how to use Dmenu
    # Dmenu(command=["shutdown", "reboot"], dmenu_font="DejaVu Sans Mono"),
    # endregion

    if DEBUG:
        layouts += [
            floating_layout,
            layout.Stack(),
            layout.Zoomy(),
            layout.Matrix(),
            layout.TreeTab(),
            layout.MonadTall(),
            layout.RatioTile(),
            layout.Slice(
                'left',
                192,
                name='slice-test',
                role='gnome-terminal',
                fallback=layout.Slice(
                    'right',
                    256,
                    role='gimp-dock',
                    fallback=layout.Stack(stacks=1)))
        ]
