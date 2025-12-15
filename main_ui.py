import wx
import wx.adv
import calendar
from datetime import date

from todo_backend import TaskManager
from calendar_backend import CalendarManager

# =============================
# THEME
# =============================
BG = "#0B0B0B"
PANEL = "#161616"
CARD = "#1E1E1E"
TEXT = "#FFFFFF"
SUBTEXT = "#AAAAAA"
ACCENT = "#c6fa74"


# =============================
# FEATURE CARD
# =============================
class FeatureCard(wx.Panel):
    def __init__(self, parent, title, subtitle, on_click=None):
        super().__init__(parent)
        self.on_click = on_click

        self.SetBackgroundColour(ACCENT)  # border color
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        outer = wx.BoxSizer(wx.VERTICAL)

        self.inner = wx.Panel(self)
        self.inner.SetBackgroundColour(CARD)

        content = wx.BoxSizer(wx.VERTICAL)

        t = wx.StaticText(self.inner, label=title)
        t.SetForegroundColour(TEXT)
        t.SetFont(wx.Font(
            15, wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))

        st = wx.StaticText(self.inner, label=subtitle)
        st.SetForegroundColour(SUBTEXT)

        content.Add(t, 0, wx.LEFT | wx.TOP | wx.EXPAND, 18)
        content.Add(st, 0, wx.LEFT | wx.TOP | wx.EXPAND, 6)
        content.AddStretchSpacer()

        self.inner.SetSizer(content)
        outer.Add(self.inner, 1, wx.EXPAND | wx.ALL, 1)

        self.SetSizer(outer)
        self.SetMinSize((-1, 140))

        # click bindings (panel + children)
        for w in (self, self.inner, t, st):
            w.Bind(wx.EVT_LEFT_DOWN, self._handle_click)

    def _handle_click(self, evt):
        if self.on_click:
            self.on_click()



# =============================
# STAT CARD (COMPACT)
# =============================
class StatCard(wx.Panel):
    def __init__(self, parent, title):
        super().__init__(parent)

        self.SetBackgroundColour(CARD)
        self.SetMinSize((800, 120))

        s = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label=title)
        self.title.SetForegroundColour(SUBTEXT)

        self.value = wx.StaticText(self, label="0")
        self.value.SetForegroundColour(TEXT)
        self.value.SetFont(wx.Font(
            24, wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))

        s.Add(self.title, 0, wx.ALL | wx.EXPAND, 10)
        s.Add(self.value, 0, wx.LEFT | wx.BOTTOM | wx.EXPAND, 18)

        self.SetSizer(s)

    def update(self, value):
        self.value.SetLabel(str(value))
        self.Layout()

        


# =============================
# CALENDAR GRID (STABLE)
# =============================
class CalendarGrid(wx.Panel):
    def __init__(self, parent, on_date_selected):
        super().__init__(parent)
        self.SetBackgroundColour(PANEL)

        self.on_date_selected = on_date_selected

        today = date.today()
        self.year = today.year
        self.month = today.month
        self.selected_day = today.day

        self.root = wx.BoxSizer(wx.VERTICAL)
        self.header = wx.BoxSizer(wx.HORIZONTAL)

        # IMPORTANT: FlexGridSizer (not GridSizer)
        self.grid = wx.FlexGridSizer(rows=0, cols=8, vgap=4, hgap=4)

        self.build_header()
        self.build_grid()

        self.root.Add(self.header, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.root.Add(self.grid, 0, wx.ALL, 10)

        self.SetSizer(self.root)

        

    # -------------------------
    # Helpers
    # -------------------------
    def clamp_day(self):
        last = calendar.monthrange(self.year, self.month)[1]
        if self.selected_day > last:
            self.selected_day = last

    def emit_date(self):
        self.clamp_day()
        date_str = f"{self.year}-{self.month:02d}-{self.selected_day:02d}"
        self.on_date_selected(date_str)

    # -------------------------
    # Header
    # -------------------------
    def nav_label(self, txt, handler):
        lbl = wx.StaticText(self, label=txt)
        lbl.SetForegroundColour(SUBTEXT)
        lbl.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS,
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl.Bind(wx.EVT_LEFT_DOWN, handler)
        lbl.Bind(wx.EVT_ENTER_WINDOW,
                 lambda e: lbl.SetForegroundColour(ACCENT))
        lbl.Bind(wx.EVT_LEAVE_WINDOW,
                 lambda e: lbl.SetForegroundColour(SUBTEXT))
        return lbl

    def build_header(self):
        self.header.Clear(True)

        prev = self.nav_label("‹", self.prev_month)
        nxt = self.nav_label("›", self.next_month)

        self.month_lbl = wx.StaticText(
            self, label=f"{calendar.month_name[self.month]} {self.year}"
        )
        self.month_lbl.SetForegroundColour(TEXT)
        self.month_lbl.SetFont(wx.Font(
            14, wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
        ))

        self.header.Add(prev, 0, wx.RIGHT, 14)
        self.header.Add(self.month_lbl)
        self.header.Add(nxt, 0, wx.LEFT, 14)

    # -------------------------
    # Grid
    # -------------------------
    def build_grid(self):
        self.grid.Clear(True)

        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            lbl = wx.StaticText(self, label=d)
            lbl.SetForegroundColour(SUBTEXT)
            self.grid.Add(lbl, 0, wx.ALIGN_CENTER)

        for week in calendar.monthcalendar(self.year, self.month):
            for d in week:
                if d == 0:
                    self.grid.Add(wx.Panel(self))
                else:
                    btn = wx.Button(self, label=str(d), size=(40, 40))
                    btn.day = d
                    btn.Bind(wx.EVT_BUTTON, self.on_day_clicked)

                    if d == self.selected_day:
                        btn.SetBackgroundColour(ACCENT)
                        btn.SetForegroundColour("#000000")
                    else:
                        btn.SetBackgroundColour(PANEL)
                        btn.SetForegroundColour(TEXT)

                    self.grid.Add(btn, 0, wx.ALIGN_CENTER)

        self.grid.Layout()
        self.root.Layout()
        self.Layout()

    # -------------------------
    # Events
    # -------------------------
    def on_day_clicked(self, evt):
        self.selected_day = evt.GetEventObject().day
        self.build_grid()
        self.emit_date()

    def prev_month(self, evt):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1

        self.month_lbl.SetLabel(f"{calendar.month_name[self.month]} {self.year}")
        self.build_grid()
        self.emit_date()

    def next_month(self, evt):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1

        self.month_lbl.SetLabel(f"{calendar.month_name[self.month]} {self.year}")
        self.build_grid()
        self.emit_date()


# =============================
# SIDEBAR
# =============================
class Sidebar(wx.Panel):
    def __init__(self, parent, pages):
        super().__init__(parent, size=(140, -1))
        self.pages = pages
        self.SetBackgroundColour("#000000")

        s = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="PLANNER")
        title.SetForegroundColour(TEXT)
        title.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        s.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 20)

        for name in ["Home", "ToDo", "Timetable"]:
            t = wx.StaticText(self, label=name)
            t.SetForegroundColour(TEXT)
            t.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            t.Bind(
                wx.EVT_LEFT_DOWN,
                lambda e, n=name.lower(): self.pages.show(n)
            )
            s.Add(t, 0, wx.ALL | wx.ALIGN_CENTER, 18)

        s.AddStretchSpacer()
        self.SetSizer(s)


# =============================
# HOME PAGE
# =============================
class HomePage(wx.Panel):
    def __init__(self, parent, cal_mgr, pages):
        super().__init__(parent)
        self.pages = pages
        self.cal_mgr = cal_mgr

        root = wx.BoxSizer(wx.VERTICAL)

        hdr = wx.StaticText(self, label="Welcome Back")
        hdr.SetForegroundColour(TEXT)
        hdr.SetFont(wx.Font(28, wx.FONTFAMILY_SWISS,
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        root.Add(hdr, 0, wx.ALL, 24)

        top = wx.BoxSizer(wx.HORIZONTAL)

        todo_card = FeatureCard(
            self,
            "To-Do List",
            "Your personal task manager.",
            on_click=lambda: self.pages.show("todo")
        )

        tt_card = FeatureCard(
            self,
            "Timetable",
            "Your schedule at a glance.",
            on_click=lambda: self.pages.show("timetable")
        )

        top.Add(todo_card, 1, wx.ALL | wx.EXPAND, 12)
        top.Add(tt_card, 1, wx.ALL | wx.EXPAND, 12)

        root.Add(top, 0, wx.EXPAND)

        body = wx.BoxSizer(wx.HORIZONTAL)

        self.calendar = CalendarGrid(self, self.on_date_selected)
        body.Add(self.calendar, 0, wx.ALL, 20)

        stats = wx.BoxSizer(wx.VERTICAL)
        self.tasks = StatCard(self, "Tasks Due Today")
        self.events = StatCard(self, "Events Today")

        stats.Add(self.tasks, 0, wx.ALL, 10)
        stats.Add(self.events, 0, wx.ALL, 10)

        body.Add(stats, 0, wx.TOP, 20)

        root.Add(body, 1, wx.EXPAND)
        self.SetSizer(root)
        # Trigger initial calendar update AFTER widgets exist
        today = f"{self.calendar.year}-{self.calendar.month:02d}-{self.calendar.selected_day:02d}"
        self.on_date_selected(today)


    def on_date_selected(self, date_str):
        data = self.cal_mgr.daily_overview(date_str)
        self.tasks.update(len(data["tasks"]))
        self.events.update(len(data["events"]))
        def on_right_click(self, evt):
            menu = wx.Menu()
            t1 = menu.Append(-1, "View To-Do")
            t2 = menu.Append(-1, "View Timetable")

            self.Bind(wx.EVT_MENU,
                  lambda e: self.open_page("todo"),
                  t1)
            self.Bind(wx.EVT_MENU,
                  lambda e: self.open_page("timetable"),
                  t2)

            self.PopupMenu(menu)

    def open_page(self, page):
        date_str = f"{self.calendar.year}-{self.calendar.month:02d}-{self.calendar.selected_day:02d}"

        if page == "todo":
            self.pages.get("todo").load_date(date_str)
        else:
            self.pages.get("timetable").load_date(date_str)

        self.pages.show(page)


# =============================
# PAGE CONTAINER
# =============================
class PageContainer(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._pages = {}  # ← renamed (IMPORTANT)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def add_page(self, name, page):
        page.Hide()
        self._pages[name] = page
        self.sizer.Add(page, 1, wx.EXPAND)

    def show(self, name):
        for p in self._pages.values():
            p.Hide()
        self._pages[name].Show()
        self.Layout()

    def get(self, name):
        return self._pages[name]

# -----------------------------
# FIXED CATEGORIES
# -----------------------------
CATEGORIES = {
    "General": "#c6fa74",
    "College": "#ff9f1c",
    "Personal": "#9b5de5"
}


# =============================
# ADD TASK DIALOG
# =============================
class AddTaskDialog(wx.Dialog):
    def __init__(self, parent, cal_mgr, date_str):
        super().__init__(parent, title="Add Task", size=(360, 320))
        self.cal_mgr = cal_mgr
        self.date_str = date_str

        panel = wx.Panel(self)
        panel.SetBackgroundColour(BG)

        s = wx.BoxSizer(wx.VERTICAL)

        # Title
        lbl_title = wx.StaticText(panel, label="Task Title")
        lbl_title.SetForegroundColour(TEXT)
        self.title_txt = wx.TextCtrl(panel)

        # Category
        lbl_cat = wx.StaticText(panel, label="Category")
        lbl_cat.SetForegroundColour(TEXT)
        self.cat_choice = wx.Choice(panel, choices=list(CATEGORIES.keys()))
        self.cat_choice.SetSelection(0)

        # Priority
        lbl_pr = wx.StaticText(panel, label="Priority")
        lbl_pr.SetForegroundColour(TEXT)
        self.pr_choice = wx.Choice(panel, choices=["Low", "Medium", "High"])
        self.pr_choice.SetSelection(1)

        # Buttons
        btns = wx.BoxSizer(wx.HORIZONTAL)
        add = wx.Button(panel, label="Add")
        cancel = wx.Button(panel, label="Cancel")
        add.Bind(wx.EVT_BUTTON, self.on_add)
        cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))

        btns.AddStretchSpacer()
        btns.Add(add, 0, wx.RIGHT, 10)
        btns.Add(cancel, 0)

        # Layout
        for w in (
            lbl_title, self.title_txt,
            lbl_cat, self.cat_choice,
            lbl_pr, self.pr_choice
        ):
            s.Add(w, 0, wx.EXPAND | wx.ALL, 8)

        s.AddStretchSpacer()
        s.Add(btns, 0, wx.EXPAND | wx.ALL, 12)

        panel.SetSizer(s)

    def on_add(self, evt):
        title = self.title_txt.GetValue().strip()
        if not title:
            wx.MessageBox("Task title required")
            return

        category = self.cat_choice.GetStringSelection()
        priority = self.pr_choice.GetSelection()  # 0,1,2

        self.cal_mgr.tm.add_task(
            title=title,
            deadline=self.date_str,
            category=category,
            priority=priority
        )
        self.EndModal(wx.ID_OK)


# =============================
# TASK ITEM
# =============================
class TaskItem(wx.Panel):
    def __init__(self, parent, task, color, on_toggle, on_delete):
        super().__init__(parent)
        self.task = task
        self.on_toggle = on_toggle
        self.on_delete = on_delete

        self.SetBackgroundColour(BG)

        outer = wx.BoxSizer(wx.HORIZONTAL)

        bar = wx.Panel(self, size=(6, -1))
        bar.SetBackgroundColour(color)

        chk = wx.CheckBox(self)
        chk.SetValue(task.done)
        chk.Bind(wx.EVT_CHECKBOX, self._toggle)

        title = wx.StaticText(self, label=task.title)
        title.SetForegroundColour(TEXT)

        outer.Add(bar, 0, wx.EXPAND)
        outer.Add(chk, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        outer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(outer)
        self.SetMinSize((-1, 44))

        # Right-click delete
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)
        title.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)
        chk.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)

    def _toggle(self, evt):
        self.on_toggle(self.task)

    def _on_right_click(self, evt):
        menu = wx.Menu()
        delete_item = menu.Append(wx.ID_ANY, "Delete")
        self.Bind(wx.EVT_MENU,
                  lambda e: self.on_delete(self.task),
                  delete_item)
        self.PopupMenu(menu)
        menu.Destroy()


# =============================
# TODO PAGE
# =============================
class TodoPage(wx.Panel):
    def __init__(self, parent, cal_mgr):
        super().__init__(parent)
        self.SetBackgroundColour(BG)
        self.cal_mgr = cal_mgr

        self.status_filter = "all"
        self.priority_filter = "all"
        self.search_text = ""

        root = wx.BoxSizer(wx.VERTICAL)

        # ---------- Header ----------
        header = wx.BoxSizer(wx.HORIZONTAL)

        self.title = wx.StaticText(self, label="To-Do")
        self.title.SetForegroundColour(TEXT)
        self.title.SetFont(wx.Font(26, wx.FONTFAMILY_SWISS,
                                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.date_picker = wx.adv.DatePickerCtrl(
            self, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
        )
        self.date_picker.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_change)

        filter_btn = wx.StaticText(self, label="☰")
        filter_btn.SetForegroundColour(TEXT)
        filter_btn.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS,
                                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        filter_btn.Bind(wx.EVT_LEFT_DOWN, self.show_filter_menu)

        self.search = wx.SearchCtrl(self, size=(200, -1))
        self.search.Bind(wx.EVT_TEXT, self.on_search)

        add_btn = wx.StaticText(self, label="+")
        add_btn.SetForegroundColour(ACCENT)
        add_btn.SetFont(wx.Font(26, wx.FONTFAMILY_SWISS,
                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        add_btn.Bind(wx.EVT_LEFT_DOWN, self.on_add_task)

        header.Add(self.title, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 20)
        header.Add(self.date_picker, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 16)
        header.Add(filter_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)
        header.AddStretchSpacer()
        header.Add(self.search, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        header.Add(add_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 24)

        root.Add(header, 0, wx.EXPAND)

        # ---------- Scroll ----------
        self.scroll = wx.ScrolledWindow(self)
        self.scroll.SetScrollRate(0, 20)
        self.scroll.SetBackgroundColour(BG)

        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll.SetSizer(self.scroll_sizer)

        root.Add(self.scroll, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.SetSizer(root)

        today = date.today().strftime("%Y-%m-%d")
        self.load_date(today)

    # ---------- Filters ----------
    def show_filter_menu(self, evt):
        menu = wx.Menu()

        status = wx.Menu()
        for lbl in ["All", "Active", "Completed"]:
            item = status.Append(wx.ID_ANY, lbl)
            self.Bind(wx.EVT_MENU,
                      lambda e, v=lbl.lower(): self.set_status(v),
                      item)

        priority = wx.Menu()
        for lbl, val in [("All", "all"), ("Low", 0), ("Medium", 1), ("High", 2)]:
            item = priority.Append(wx.ID_ANY, lbl)
            self.Bind(wx.EVT_MENU,
                      lambda e, v=val: self.set_priority(v),
                      item)

        menu.AppendSubMenu(status, "Status")
        menu.AppendSubMenu(priority, "Priority")

        self.PopupMenu(menu)
        menu.Destroy()

    def set_status(self, mode):
        self.status_filter = mode
        self.load_date(self.date)

    def set_priority(self, val):
        self.priority_filter = val
        self.load_date(self.date)

    def on_search(self, evt):
        self.search_text = self.search.GetValue().lower()
        self.load_date(self.date)

    # ---------- Actions ----------
    def on_add_task(self, evt):
        dlg = AddTaskDialog(self, self.cal_mgr, self.date)
        if dlg.ShowModal() == wx.ID_OK:
            self.load_date(self.date)
        dlg.Destroy()

    def toggle_done(self, task):
        task.done = not task.done
        self.cal_mgr.tm.save()
        self.load_date(self.date)

    def on_date_change(self, evt):
        d = evt.GetDate()
        date_str = f"{d.GetYear()}-{d.GetMonth()+1:02d}-{d.GetDay():02d}"
        self.load_date(date_str)

    # ---------- Load ----------
    def load_date(self, date_str):
        self.date = date_str
        y, m, d = date_str.split("-")
        self.title.SetLabel(f"To-Do · {d}-{m}-{y}")

        self.scroll_sizer.Clear(True)

        tasks = self.cal_mgr.tm.get_tasks_by_date(date_str)

        if self.status_filter == "active":
            tasks = [t for t in tasks if not t.done]
        elif self.status_filter == "completed":
            tasks = [t for t in tasks if t.done]

        if self.priority_filter != "all":
            tasks = [t for t in tasks if t.priority == int(self.priority_filter)]

        if self.search_text:
            tasks = [t for t in tasks if self.search_text in t.title.lower()]

        grouped = {}
        for t in tasks:
            grouped.setdefault(t.category, []).append(t)

        if not grouped:
            msg = wx.StaticText(self.scroll, label="No tasks for this day.")
            msg.SetForegroundColour(SUBTEXT)
            self.scroll_sizer.Add(msg, 0, wx.ALL, 40)
        else:
            for cat in CATEGORIES:
                if cat not in grouped:
                    continue
                hdr = wx.StaticText(self.scroll, label=cat)
                hdr.SetForegroundColour(CATEGORIES[cat])
                hdr.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS,
                                    wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                self.scroll_sizer.Add(hdr, 0, wx.LEFT | wx.TOP, 12)

                for t in grouped[cat]:
                    item = TaskItem(
                    self.scroll,
                    t,
                    CATEGORIES[cat],
                    self.toggle_done,
                    self.delete_task
                    )
                    self.scroll_sizer.Add(item, 0, wx.EXPAND | wx.BOTTOM, 8)
                    self.scroll.Layout()
                    self.scroll.FitInside()
                    self.scroll.Refresh()


    def delete_task(self, task):
        dlg = wx.MessageDialog(
            self,
            f"Delete task:\n\n{task.title}",
            "Confirm Delete",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        if dlg.ShowModal() == wx.ID_YES:
            # SAFE delete (no IDs, no assumptions)
            if task in self.cal_mgr.tm.tasks:
                self.cal_mgr.tm.tasks.remove(task)
                self.cal_mgr.tm.save()
            self.load_date(self.date)
        dlg.Destroy()


        self.scroll.Layout()
        self.scroll.FitInside()

# =============================
# TIMETABLE PAGE (CANVAS BASED)
# =============================
import wx
import wx.adv
from datetime import datetime, timedelta, date

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"]

CATEGORY_COLOR_CACHE = {
    "General": (120, 120, 120),
    "Work": (255, 159, 28),
    "Personal": (155, 93, 229),
    "College": (58, 134, 255)
}


# =============================
# TIMETABLE PAGE
# =============================
class TimetableAddDialog(wx.Dialog):
    def __init__(self, parent, default_date):
        super().__init__(parent, title="Add Event", size=(360, 340))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(BG)

        s = wx.BoxSizer(wx.VERTICAL)

        # Event title
        s.Add(wx.StaticText(panel, label="Event Title"), 0, wx.ALL, 6)
        self.name = wx.TextCtrl(panel)
        s.Add(self.name, 0, wx.EXPAND | wx.ALL, 6)

        # Date
        s.Add(wx.StaticText(panel, label="Date"), 0, wx.ALL, 6)
        self.date = wx.adv.DatePickerCtrl(panel)
        self.date.SetValue(
            wx.DateTime.FromDMY(
                default_date.day,
                default_date.month - 1,
                default_date.year
            )
        )
        s.Add(self.date, 0, wx.EXPAND | wx.ALL, 6)

        # Time row
        row = wx.BoxSizer(wx.HORIZONTAL)
        self.start = wx.TextCtrl(panel, value="09:00")
        self.end = wx.TextCtrl(panel, value="10:00")

        row.Add(wx.StaticText(panel, label="Start"), 0,
                wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        row.Add(self.start, 1, wx.RIGHT, 12)
        row.Add(wx.StaticText(panel, label="End"), 0,
                wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        row.Add(self.end, 1)

        s.Add(row, 0, wx.EXPAND | wx.ALL, 6)

        # Category
        s.Add(wx.StaticText(panel, label="Category"), 0, wx.ALL, 6)
        self.category = wx.Choice(panel, choices=list(CATEGORY_COLOR_CACHE.keys()))
        self.category.SetSelection(0)
        s.Add(self.category, 0, wx.EXPAND | wx.ALL, 6)

        # Buttons — ✅ CORRECT PARENT
        btns = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btns.AddButton(btn_ok)
        btns.AddButton(btn_cancel)
        btns.Realize()

        s.Add(btns, 0, wx.EXPAND | wx.ALL, 12)

        panel.SetSizer(s)
        s.Fit(self)

    def get_data(self):
        d = self.date.GetValue()
        return {
            "name": self.name.GetValue(),
            "date": f"{d.GetYear():04d}-{d.GetMonth()+1:02d}-{d.GetDay():02d}",
            "start": self.start.GetValue(),
            "end": self.end.GetValue(),
            "category": self.category.GetStringSelection()
        }

class TimetablePage(wx.Panel):
    def __init__(self, parent, cal_mgr):
        super().__init__(parent)
        self.SetBackgroundColour(BG)

        self.cal_mgr = cal_mgr
        self.selected_date = date.today()
        self.view_mode = "weekly"

        root = wx.BoxSizer(wx.VERTICAL)

        # ---------- HEADER PANEL (FIXED) ----------
        header_panel = wx.Panel(self)
        header_panel.SetBackgroundColour(BG)
        header = wx.BoxSizer(wx.HORIZONTAL)
        header_panel.SetSizer(header)

        title = wx.StaticText(header_panel, label="Timetable")
        title.SetForegroundColour(TEXT)
        title.SetFont(wx.Font(26, wx.FONTFAMILY_SWISS,
                              wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.view_choice = wx.Choice(header_panel, choices=["Weekly View", "Daily View"])
        self.view_choice.SetSelection(0)
        self.view_choice.Bind(wx.EVT_CHOICE, self.on_view_change)

        self.date_picker = wx.adv.DatePickerCtrl(header_panel)
        self.date_picker.Bind(wx.adv.EVT_DATE_CHANGED, self.on_date_change)

        add_btn = wx.Button(header_panel, label="+", size=(40, 40), style=wx.BORDER_NONE)
        add_btn.SetFont(wx.Font(26, wx.FONTFAMILY_SWISS,
                                wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        add_btn.SetForegroundColour(ACCENT)
        add_btn.SetBackgroundColour(BG)
        add_btn.Bind(wx.EVT_BUTTON, self.on_add_event)

        header.Add(title, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 20)
        header.AddStretchSpacer()
        header.Add(self.view_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)
        header.Add(self.date_picker, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)
        header.Add(add_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 24)

        root.Add(header_panel, 0, wx.EXPAND)

        # ---------- SCROLL ----------
        self.scroll = wx.ScrolledWindow(self)
        self.scroll.SetBackgroundColour(BG)
        self.scroll.SetScrollRate(0, 20)

        self.container = wx.BoxSizer(wx.VERTICAL)
        self.scroll.SetSizer(self.container)

        root.Add(self.scroll, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        self.SetSizer(root)

        self.refresh()

    # ---------- EVENTS ----------
    def on_view_change(self, evt):
        self.view_mode = "weekly" if self.view_choice.GetSelection() == 0 else "daily"
        self.refresh()

    def on_date_change(self, evt):
        d = self.date_picker.GetValue()
        self.selected_date = date(d.GetYear(), d.GetMonth() + 1, d.GetDay())
        self.refresh()

    def on_add_event(self, evt):
        dlg = TimetableAddDialog(self, self.selected_date)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        data = dlg.get_data()
        dlg.Destroy()

        try:
            self.cal_mgr.add_timetable_event(**data)
            self.cal_mgr.save_timetable()
            self.refresh()
        except ValueError as e:
            wx.MessageBox(str(e), "Error", wx.ICON_WARNING)

    # ---------- RENDER ----------
    def refresh(self):
        self.container.Clear(True)

        canvas = TimelineCanvas(
            self.scroll,
            self.cal_mgr,
            self.selected_date,
            mode=self.view_mode
        )

        self.container.Add(canvas, 1, wx.EXPAND)
        self.scroll.Layout()
        self.scroll.FitInside()


# =============================
# CANVAS TIMELINE (DISPLAY ONLY)
# =============================
class TimelineCanvas(wx.ScrolledWindow):
    Y_SCALE = 2
    LEFT_MARGIN = 70
    COL_WIDTH = 150
    COL_GAP = 14
    TOP_PAD = 28

    def __init__(self, parent, cal_mgr, base_date, mode="weekly"):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.cal_mgr = cal_mgr
        self.base_date = base_date
        self.mode = mode

        self._event_rects = []

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

        height = 24 * 60 * self.Y_SCALE + self.TOP_PAD * 2
        cols = 7 if mode == "weekly" else 1
        width = self.LEFT_MARGIN + cols * (self.COL_WIDTH + self.COL_GAP)

        self.SetVirtualSize((width, height))
        self.SetScrollRate(0, 20)

    def minutes(self, t):
        h, m = map(int, t.split(":"))
        return h * 60 + m

    def on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        self.PrepareDC(dc)
        dc.Clear()

        self._event_rects.clear()
        w, h = self.GetVirtualSize()

        # Background
        dc.SetBrush(wx.Brush(BG))
        dc.SetPen(wx.Pen(BG))
        dc.DrawRectangle(0, 0, w, h)

        # Hour grid
        dc.SetTextForeground(SUBTEXT)
        for hour in range(25):
            y = hour * 60 * self.Y_SCALE + self.TOP_PAD
            dc.DrawText(f"{hour:02d}:00", 8, y - 6)
            dc.SetPen(wx.Pen((60, 60, 60)))
            dc.DrawLine(self.LEFT_MARGIN, y, w, y)

        # Days
        if self.mode == "weekly":
            monday = self.base_date - timedelta(days=self.base_date.weekday())
            days = [monday + timedelta(days=i) for i in range(7)]
        else:
            days = [self.base_date]

        # Day headers
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS,
                           wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground(TEXT)
        for i, d in enumerate(days):
            x = self.LEFT_MARGIN + i * (self.COL_WIDTH + self.COL_GAP)
            dc.DrawText(d.strftime("%A"), x + 8, 6)

        # Events
        for i, d in enumerate(days):
            x = self.LEFT_MARGIN + i * (self.COL_WIDTH + self.COL_GAP)
            events = self.cal_mgr.timetable_for_date(d.strftime("%Y-%m-%d"))

            for ev in events:
                try:
                    s = self.minutes(ev["start"])
                    e = self.minutes(ev["end"])
                except Exception:
                    continue

                y = s * self.Y_SCALE + self.TOP_PAD
                duration = max(15, e - s)          # minimum 15 minutes
                h_e = duration * self.Y_SCALE


                rect = wx.Rect(x, y, self.COL_WIDTH, h_e)
                self._event_rects.append((rect, ev))

                color = CATEGORY_COLOR_CACHE.get(ev.get("category", "General"), (120, 120, 120))
                dc.SetBrush(wx.Brush(wx.Colour(*color)))
                dc.SetPen(wx.Pen(wx.Colour(80, 80, 80)))
                dc.DrawRoundedRectangle(rect, 6)

                dc.SetTextForeground(wx.BLACK)
                dc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS,
                                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                dc.DrawText(ev["name"][:20], rect.x + 8, rect.y + 8)

                dc.SetFont(wx.Font(
                    8,
                    wx.FONTFAMILY_SWISS,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL
                ))
                dc.DrawText(
                    f"{ev['start']} – {ev['end']}",
                    rect.x + 8,
                    rect.y + 26
                )

    # ---------- RIGHT CLICK DELETE ----------
    def on_right_click(self, evt):
        # Convert mouse position to logical (scrolled) coords
        mx, my = evt.GetPosition()
        lx, ly = self.CalcUnscrolledPosition(mx, my)

        for rect, ev in self._event_rects:
            if rect.Contains((lx, ly)):
                menu = wx.Menu()
                item_delete = menu.Append(wx.ID_ANY, "Delete")

                # bind to menu (correct)
                menu.Bind(
                    wx.EVT_MENU,
                    lambda e, ev=ev: self.delete_event(ev),
                    item_delete
                )

                self.PopupMenu(menu)
                menu.Destroy()
                return


    def delete_event(self, event):
        if wx.MessageBox(
            "Delete this event?",
            "Confirm",
            wx.YES_NO | wx.ICON_WARNING
        ) == wx.YES:
            self.cal_mgr.delete_timetable_event(event)
            self.cal_mgr.save_timetable()
            self.GetParent().GetParent().refresh()

# =============================
# MAIN FRAME
# =============================
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Executive Planner", size=(1200, 800))
        self.SetBackgroundColour(BG)

        tm = TaskManager()
        self.cal_mgr = CalendarManager(tm)

        # ✅ LOAD TIMETABLE AT STARTUP
        self.cal_mgr.load_timetable()

        root = wx.BoxSizer(wx.HORIZONTAL)

        pages = PageContainer(self)

        home = HomePage(pages, self.cal_mgr, pages)
        todo = TodoPage(pages, self.cal_mgr)
        timetable = TimetablePage(pages, self.cal_mgr)

        pages.add_page("home", home)
        pages.add_page("todo", todo)
        pages.add_page("timetable", timetable)

        pages.show("home")

        sidebar = Sidebar(self, pages)

        root.Add(sidebar, 0, wx.EXPAND)
        root.Add(pages, 1, wx.EXPAND)

        self.SetSizer(root)
        self.Centre()

# =============================
# APP ENTRY
# =============================
class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    App(False).MainLoop()
