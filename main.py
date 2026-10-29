import os
import sys

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect, pyqtSignal, QCoreApplication
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QPalette, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox,
    QTabWidget, QScrollArea, QGroupBox, QGridLayout, QCheckBox,
    QSpinBox, QFrame, QSizePolicy
)

from i18n import get_language, load_language, save_language, t
from models.save_file import HadesSaveFile


# ── Palette ───────────────────────────────────────────────────────────────────
# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK   = "#0b0b0e"
BG_PANEL  = "#121216"
BG_CARD   = "#18181d"
BG_INSET  = "#08080a"
GOLD      = "#cfa850"
GOLD_DIM  = "#5c4b1a"
GOLD_PALE = "#f1e3c0"
ORANGE    = "#d07020"
RED       = "#e64141"
TEXT      = "#f0f0f2"
TEXT_DIM  = "#a0a0b0"
BORDER    = "#222228"
BORDER_LT = "#33333c"
GREEN     = "#34c759"
BLUE      = "#007aff"

QSS = f"""
* {{
    font-family: 'SF Pro Display', 'Inter', system-ui;
    outline: none;
}}
QMainWindow, QDialog {{
    background-color: {BG_DARK};
}}
#mainWindowBackground {{
    background-position: center;
    background-repeat: no-repeat;
}}
#bgOverlay {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(11, 11, 14, 0.98), stop:0.3 rgba(11, 11, 14, 0.85), stop:0.7 rgba(11, 11, 14, 0.90), stop:1 rgba(11, 11, 14, 1.0));
}}
QWidget {{
    background-color: transparent;
    color: {TEXT};
    font-size: 13px;
}}
#welcomeDialog {{
    background-color: {BG_DARK};
}}

/* ─── Scrollbars ─────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 2px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_LT};
    border-radius: 1px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {GOLD}; }}

/* ─── Header ─────────────────────────────────────────────────── */
#titleBar {{
    background: {BG_DARK};
    border-bottom: 1px solid {BORDER};
}}
#appTitle {{
    font-size: 42px;
    font-weight: 900;
    color: {GOLD};
    letter-spacing: 24px;
}}
#appSubtitle {{
    font-size: 10px;
    color: {TEXT_DIM};
    letter-spacing: 8px;
    text-transform: uppercase;
}}

/* ─── Tabs ───────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: none;
    background: {BG_DARK};
}}
QTabWidget::tab-bar {{
    alignment: left;
    margin-left: 20px;
}}
QTabBar::tab {{
    background: transparent;
    color: {TEXT_DIM};
    border-bottom: 2px solid transparent;
    padding: 24px 30px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
}}
QTabBar::tab:selected {{
    color: {GOLD};
    border-bottom: 2px solid {GOLD};
}}

/* ─── Cards ──────────────────────────────────────────────────── */
QGroupBox {{
    background: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 20px;
    margin-top: 32px;
    padding: 30px;
    font-size: 10px;
    font-weight: 800;
    color: {TEXT_DIM};
    letter-spacing: 6px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top center;
    top: 12px;
    padding: 0 24px;
    background: {BG_PANEL};
}}

/* ─── Items ──────────────────────────────────────────────────── */
#resourceCard {{
    background: {BG_CARD};
    border-radius: 14px;
}}
#gameToggle {{
    padding: 10px 30px;
    font-size: 11px;
    font-weight: 900;
    border-radius: 22px;
    background: {BG_CARD};
    border: 1px solid {BORDER};
    color: {TEXT_DIM};
    letter-spacing: 2px;
}}
#gameToggle:checked, #langToggle:checked {{
    background: {GOLD};
    border-color: {GOLD};
    color: {BG_DARK};
}}
#langToggle {{
    padding: 10px 14px;
    font-size: 11px;
    font-weight: 900;
    border-radius: 22px;
    background: {BG_CARD};
    border: 1px solid {BORDER};
    color: {TEXT_DIM};
    letter-spacing: 1px;
}}

QPushButton {{
    background: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 14px;
    color: {TEXT};
    font-weight: 700;
    font-size: 11px;
    padding: 12px 28px;
    letter-spacing: 1px;
}}
QPushButton:hover {{
    background: {BORDER};
    border-color: {TEXT_DIM};
}}
#btnPrimary {{
    background: white;
    color: black;
    border: none;
    font-weight: 900;
}}
#btnPrimary:hover {{ background: {GOLD_PALE}; }}
"""

# ── Weapon definitions ────────────────────────────────────────────────────────
WEAPON_COLOR = {
    "SwordWeapon":  ("#e8a020", "#3a2810"),
    "SpearWeapon":  ("#50c8e0", "#0e2430"),
    "ShieldWeapon": ("#a060e0", "#1e1038"),
    "BowWeapon":    ("#60c060", "#102010"),
    "FistWeapon":   ("#e07050", "#3a1808"),
    "GunWeapon":    ("#8090d0", "#141830"),
}

WEAPONS = [
    {"key": "SwordWeapon",  "name": "STYGIUS",    "sub": "Sword of Damocles",        "icon": "⚔",
     "aspects": ["Zagreus", "Nemesis", "Poseidon", "Arthur"]},
    {"key": "SpearWeapon",  "name": "VARATHA",     "sub": "Eternal Spear",            "icon": "🔱",
     "aspects": ["Zagreus", "Achilles", "Hades", "Guan Yu"]},
    {"key": "ShieldWeapon", "name": "AEGIS",       "sub": "Shield of Chaos",          "icon": "🛡",
     "aspects": ["Zagreus", "Chaos", "Zeus", "Beowulf"]},
    {"key": "BowWeapon",    "name": "CORONACHT",   "sub": "Heart-Seeking Bow",        "icon": "🏹",
     "aspects": ["Zagreus", "Chiron", "Hera", "Rama"]},
    {"key": "FistWeapon",   "name": "MALPHON",     "sub": "Twin Fists of Malphon",    "icon": "✊",
     "aspects": ["Zagreus", "Talos", "Demeter", "Gilgamesh"]},
    {"key": "GunWeapon",    "name": "EXAGRYPH",    "sub": "Adamant Rail",             "icon": "⚡",
     "aspects": ["Zagreus", "Eris", "Hestia", "Lucifer"]},
]

# Boss rooms used by the Pact of Punishment bounties. The save stores the
# highest cleared heat in RecordClearedShrineThreshold, and each claimed
# heat level in RecordLastClearedShrineReward.
HEAT_BOSSES = [
    ("A_Boss",   "heat.furies",  "heat.furies_sub"),
    ("B_Boss01", "heat.hydra",   "heat.hydra_sub"),
    ("C_Boss01", "heat.theseus", "heat.theseus_sub"),
    ("D_Boss01", "heat.hades",   "heat.hades_sub"),
]

HEAT_REWARDS = {
    "SuperLockKeyDrop": "heat.reward.titan_blood",
    "SuperGemDrop": "heat.reward.diamond",
    "SuperGiftDrop": "heat.reward.ambrosia",
}


def _as_heat(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return None
    return None


def _stat_text(value):
    number = _as_heat(value)
    return "—" if number is None else str(number)


def _format_clear_time(value):
    seconds = _as_heat(value)
    if seconds is None or seconds <= 0:
        return "—"
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _boss_heat_text(threshold, reward_map):
    """Return highest heat, claimed heat levels, and a reward tooltip."""
    claimed = []
    if isinstance(reward_map, dict):
        for heat, reward in reward_map.items():
            number = _as_heat(heat)
            if number is None:
                continue
            claimed.append((number, reward))
        claimed.sort()
    top = _as_heat(threshold)
    if top is None and claimed:
        top = claimed[-1][0]
    if top is None and not claimed:
        return "—", "", ""
    headline = "—" if top is None else str(top)
    detail = ", ".join(str(number) for number, _reward in claimed)
    return headline, detail, _reward_tooltip(claimed)


def _reward_tooltip(claimed):
    lines = []
    for heat, reward in claimed:
        key = HEAT_REWARDS.get(str(reward))
        name = t(key) if key else str(reward)
        lines.append(t("heat.reward.line", heat=heat, reward=name))
    return "\n".join(lines)


class HeatReadout(QFrame):
    """One read-only cell: a headline number and an optional second line."""

    def __init__(self, accent, parent=None):
        super().__init__(parent)
        self.setObjectName("heatCell")
        self.setMinimumWidth(92)
        self.setMinimumHeight(58)
        self.setStyleSheet(
            f"QFrame#heatCell {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 10px; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(0)
        lay.addStretch()
        self.value = QLabel("—")
        self.value.setAlignment(Qt.AlignCenter)
        self.detail = QLabel("")
        self.detail.setAlignment(Qt.AlignCenter)
        self.detail.setWordWrap(True)
        self.detail.setVisible(False)
        self.detail.setStyleSheet(
            f"background: transparent; border: none; color: {TEXT_DIM}; "
            f"font-size: 10px; font-weight: 600;"
        )
        lay.addWidget(self.value)
        lay.addWidget(self.detail)
        lay.addStretch()
        self._accent = accent
        self._filled_style = (
            f"background: transparent; border: none; color: {accent}; "
            f"font-size: 16px; font-weight: 800;"
        )
        self._empty_style = (
            f"background: transparent; border: none; color: {TEXT_DIM}; "
            f"font-size: 16px; font-weight: 800;"
        )
        self.value.setStyleSheet(self._empty_style)

    def setToolTip(self, text):
        super().setToolTip(text)
        self.value.setToolTip(text)
        self.detail.setToolTip(text)

    def set_readout(self, value, detail=""):
        self.value.setText(value)
        self.value.setStyleSheet(self._empty_style if value == "—" else self._filled_style)
        self.detail.setText(detail)
        self.detail.setVisible(bool(detail))


class PipLevel(QWidget):
    """5 glowing dots indicating aspect level. Click to change."""
    MAX = 5
    valueChanged = pyqtSignal(int)

    def __init__(self, color=GOLD, parent=None):
        super().__init__(parent)
        self._level = 0
        self._color = QColor(color)
        self.setFixedSize(120, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(t("pip.tooltip"))

    def value(self):
        return self._level

    def set_value(self, v):
        self._level = max(0, min(self.MAX, int(v)))
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            w = self.width() / self.MAX
            clicked = int(e.x() / w) + 1
            self._level = 0 if clicked == self._level else clicked
            self.valueChanged.emit(self._level)
            self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = 8
        gap = (self.width() - self.MAX * r * 2) / (self.MAX + 1)
        y = self.height() / 2
        for i in range(self.MAX):
            x = gap + i * (r * 2 + gap) + r
            filled = i < self._level
            if filled:
                # glow
                glow = QColor(self._color)
                glow.setAlpha(60)
                p.setBrush(QBrush(glow))
                p.setPen(Qt.NoPen)
                p.drawEllipse(int(x - r - 3), int(y - r - 3), (r + 3) * 2, (r + 3) * 2)
                p.setBrush(QBrush(self._color))
                p.setPen(QPen(self._color.lighter(130), 1))
            else:
                p.setBrush(QBrush(QColor(BG_INSET)))
                p.setPen(QPen(QColor(BORDER_LT), 1))
            p.drawEllipse(int(x - r), int(y - r), r * 2, r * 2)


# ── Ornamental divider ────────────────────────────────────────────────────────
class OrnaDivider(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self.setFixedHeight(20)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(BORDER_LT)
        pen = QPen(c, 1)
        p.setPen(pen)
        w, h = self.width(), self.height()
        mid = h // 2
        if self._text:
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(self._text) + 20
            lx = (w - tw) // 2
            p.drawLine(20, mid, lx, mid)
            p.drawLine(lx + tw, mid, w - 20, mid)
            p.setPen(QPen(QColor(BORDER_LT)))
            p.drawText(QRect(lx, 0, tw, h), Qt.AlignCenter, self._text)
        else:
            p.drawLine(20, mid, w - 20, mid)
            # diamond
            d = 4
            p.setBrush(QBrush(c))
            p.setPen(Qt.NoPen)
            for xc in (w // 2,):
                pts = [(xc, mid - d), (xc + d, mid), (xc, mid + d), (xc - d, mid)]
                from PyQt5.QtGui import QPolygon
                from PyQt5.QtCore import QPoint
                poly = QPolygon([QPoint(x, y) for x, y in pts])
                p.drawPolygon(poly)


# ── Star-style level widget (for keepsakes) ───────────────────────────────
class StarLevel(QWidget):
    """3 stars indicating keepsake rank. Click to change."""
    MAX = 3
    valueChanged = pyqtSignal(int)

    def __init__(self, color=GOLD, parent=None):
        super().__init__(parent)
        self._level = 0
        self._color = QColor(color)
        self.setFixedSize(80, 22)
        self.setCursor(Qt.PointingHandCursor)

    def set_value(self, room_count):
        # 0-24 = Rank 1, 25-74 = Rank 2, 75+ = Rank 3
        if room_count < 25: self._level = 1
        elif room_count < 75: self._level = 2
        else: self._level = 3
        self.update()

    def value(self):
        # Map back to room counts for the game
        if self._level == 1: return 0
        if self._level == 2: return 25
        return 75

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            w = self.width() / self.MAX
            clicked = int(e.x() / w) + 1
            self._level = clicked
            self.valueChanged.emit(self.value())
            self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        for i in range(self.MAX):
            filled = i < self._level
            x = i * 24 + 12
            y = 11
            
            p.setPen(QPen(self._color if filled else QColor(BORDER_LT), 1))
            p.setBrush(QBrush(self._color if filled else Qt.NoBrush))
            
            # Simple star polygon
            pts = []
            for j in range(5):
                import math
                angle = math.radians(j * 144 - 90)
                pts.append((x + 8 * math.cos(angle), y + 8 * math.sin(angle)))
            
            from PyQt5.QtGui import QPolygon
            from PyQt5.QtCore import QPoint
            poly = QPolygon([QPoint(int(px), int(py)) for px, py in pts])
            p.drawPolygon(poly)


# ── Resource card ─────────────────────────────────────────────────────────────
class ResourceCard(QWidget):
    def __init__(self, icon, label, color=GOLD, parent=None):
        super().__init__(parent)
        self._color = color
        self.setObjectName("resourceCard")
        self.setStyleSheet(f"""
            #resourceCard {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 12)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(6)
        ico = QLabel(icon)
        ico.setStyleSheet(f"font-size: 22px; background: transparent;")
        top.addWidget(ico)
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"background: transparent; font-size: 9px; letter-spacing: 3px; color: {TEXT_DIM};")
        top.addWidget(lbl)
        top.addStretch()
        lay.addLayout(top)

        self.edit = QLineEdit()
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_INSET};
                border: 1px solid {BORDER};
                border-radius: 6px;
                color: {color};
                padding: 6px 10px;
                font-size: 20px;
                font-weight: bold;
                selection-background-color: {ORANGE};
            }}
            QLineEdit:focus {{ border: 1px solid {color}; }}
        """)
        lay.addWidget(self.edit)

    def value(self):
        try:
            return float(self.edit.text())
        except ValueError:
            return 0.0

    def set_value(self, v):
        self.edit.setText(str(int(v)) if v == int(v) else str(round(v, 2)))


# ── Aspect row with pips ──────────────────────────────────────────────────────
class AspectRow(QWidget):
    def __init__(self, index: int, name: str, color=GOLD, is_base=False, parent=None):
        super().__init__(parent)
        self.index = index
        self._is_base = is_base
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(14)

        # Lock icon
        self.lock = QLabel("🔒" if not is_base else "✦")
        self.lock.setStyleSheet(f"font-size: 13px; background: transparent; min-width: 20px;")
        lay.addWidget(self.lock)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"""
            background: transparent;
            font-size: 13px;
            {"color: " + color + "; font-weight: bold;" if is_base else "color: " + TEXT + ";"}
            min-width: 100px;
        """)
        lay.addWidget(name_lbl)

        self.pips = PipLevel(color)
        if is_base:
            self.pips.set_value(1)
        lay.addWidget(self.pips)

        self.spin = QSpinBox()
        self.spin.setRange(0, 5)
        self.spin.setFixedWidth(58)
        if is_base:
            self.spin.setEnabled(False)
            self.spin.setValue(1)
        lay.addWidget(self.spin)

        # Keep pips and spin in sync
        self.spin.valueChanged.connect(self._spin_changed)
        self.pips.valueChanged.connect(self.spin.setValue)

        if is_base:
            # grey out slightly
            pass

    def _spin_changed(self, v):
        self.pips.set_value(v)
        # update lock icon
        self.lock.setText("✦" if v > 0 else "🔒")

    def set_value(self, v):
        self.spin.setValue(int(v))
        self.pips.set_value(int(v))
        self.lock.setText("✦" if v > 0 or self._is_base else "🔒")

    def value(self):
        return self.spin.value()


# ── Weapon card ───────────────────────────────────────────────────────────────
class WeaponCard(QFrame):
    def __init__(self, info: dict, parent=None):
        super().__init__(parent)
        self.weapon_key = info["key"]
        color, bg = WEAPON_COLOR[info["key"]]

        # QFrame supports border/background in QSS properly
        self.setObjectName("weaponCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame#weaponCard {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {BG_CARD}, stop:1 {bg});
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QWidget()
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {bg}, stop:1 transparent);
            border-bottom: 1px solid {BORDER};
            border-radius: 0px;
        """)
        header.setFixedHeight(56)
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(16, 0, 16, 0)

        ico = QLabel(info["icon"])
        ico.setStyleSheet(f"font-size: 26px; background: transparent; color: {color};")
        hlay.addWidget(ico)
        hlay.addSpacing(8)

        v = QVBoxLayout()
        v.setSpacing(1)
        title = QLabel(info["name"])
        title.setStyleSheet(f"font-size: 15px; font-weight: 900; color: {color}; "
                        f"letter-spacing: 3px; background: transparent;")
        s = QLabel(info["sub"].upper())
        s.setStyleSheet(f"font-size: 9px; color: {TEXT_DIM}; letter-spacing: 2px; background: transparent;")
        v.addWidget(title)
        v.addWidget(s)
        hlay.addLayout(v)
        hlay.addStretch()

        self.unlock_check = QCheckBox(t("aspect.unlocked"))
        self.unlock_check.setStyleSheet(f"""
            QCheckBox {{ color: {color}; font-size: 11px; letter-spacing: 2px;
                         font-weight: bold; background: transparent; }}
            QCheckBox::indicator {{ border-color: {color}; }}
            QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}
        """)
        hlay.addWidget(self.unlock_check)
        hlay.addSpacing(10)

        btn_max = QPushButton("▲ MAX")
        btn_max.setFixedSize(70, 28)
        btn_max.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: 1px solid {color};
                border-radius: 5px;
                color: {color};
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: {color};
                color: {BG_DARK};
            }}
        """)
        btn_max.clicked.connect(self._max_all)
        hlay.addWidget(btn_max)
        # child widgets must be transparent so QFrame background shows through
        header.setAutoFillBackground(False)
        root.addWidget(header)

        # ── Aspects ──
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        blay = QVBoxLayout(body)
        blay.setContentsMargins(14, 8, 14, 12)
        blay.setSpacing(2)

        tag = QLabel(t("aspect.section"))
        tag.setStyleSheet(f"font-size: 9px; color: {TEXT_DIM}; letter-spacing: 3px; "
                          f"background: transparent; padding: 4px 0;")
        blay.addWidget(tag)

        self.aspect_rows = []
        for i, name in enumerate(info["aspects"]):
            row = AspectRow(i + 1, name, color=color, is_base=(i == 0))
            self.aspect_rows.append(row)
            blay.addWidget(row)
            if i < len(info["aspects"]) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet(f"color: {BORDER}; background: {BORDER}; max-height: 1px;")
                blay.addWidget(sep)

        root.addWidget(body)

    def _max_all(self):
        self.unlock_check.setChecked(True)
        for row in self.aspect_rows:
            row.set_value(5)

    def load(self, weapons_unlocked, weapon_unlocks):
        self.unlock_check.setChecked(bool(weapons_unlocked.get(self.weapon_key, False)))
        unlocks = weapon_unlocks.get(self.weapon_key, {})
        for row in self.aspect_rows:
            lvl = int(unlocks.get(float(row.index), 1 if row._is_base else 0))
            row.set_value(lvl)

    def save(self, weapons_unlocked, weapon_unlocks):
        weapons_unlocked[self.weapon_key] = self.unlock_check.isChecked()
        # Preserve any existing entries we don't know about, then overwrite ours
        existing = weapon_unlocks.get(self.weapon_key, {})
        unlocks = dict(existing)  # copy originals
        for row in self.aspect_rows:
            lvl = row.value()
            # Always store the value (even 0 removes it to keep save clean)
            if lvl > 0:
                unlocks[float(row.index)] = float(lvl)
            else:
                unlocks.pop(float(row.index), None)
        weapon_unlocks[self.weapon_key] = unlocks
        # Also mark weapon as touched/unlocked in WeaponsTouched if unlocking


# ── Badge widget ──────────────────────────────────────────────────────────────
class Badge(QWidget):
    def __init__(self, tag, value="—", parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 58)
        self.setStyleSheet(f"""
            Badge {{
                background: rgba(10,8,18,0.8);
                border: 1px solid {BORDER};
                border-top: 2px solid {GOLD_DIM};
                border-radius: 8px;
            }}
        """)
        v = QVBoxLayout(self)
        v.setContentsMargins(10, 6, 10, 6)
        v.setSpacing(2)
        self._top = QLabel(tag.upper())
        self._top.setStyleSheet(f"font-size: 8px; letter-spacing: 3px; color: {TEXT_DIM}; "
                                f"background: transparent;")
        self._top.setAlignment(Qt.AlignCenter)
        self._bot = QLabel(value)
        self._bot.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {GOLD}; "
                                f"background: transparent;")
        self._bot.setAlignment(Qt.AlignCenter)
        v.addWidget(self._top)
        v.addWidget(self._bot)

    def set_value(self, v):
        self._bot.setText(str(v))


# ── Welcome / Legal Dialog ────────────────────────────────────────────────────
from PyQt5.QtWidgets import QDialog

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✦ HSE ✦")
        self.setObjectName("welcomeDialog")
        self.setFixedSize(500, 480)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setStyleSheet(QSS)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(50, 50, 50, 50)
        lay.setSpacing(30)

        title = QLabel("HSE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {GOLD}; letter-spacing: 12px;")
        lay.addWidget(title)
        
        self.desc = QLabel()
        self.desc.setWordWrap(True)
        self.desc.setAlignment(Qt.AlignCenter)
        self.desc.setStyleSheet(f"color: {TEXT_DIM}; line-height: 160%; font-size: 13px;")
        lay.addWidget(self.desc)

        lay.addStretch()

        langs = QHBoxLayout()
        langs.setSpacing(12)
        langs.setAlignment(Qt.AlignCenter)
        self.btn_en = QPushButton("English")
        self.btn_es = QPushButton("Español")
        for btn, lang in ((self.btn_en, "en"), (self.btn_es, "es")):
            btn.setObjectName("langToggle")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, chosen=lang: self._choose_language(chosen))
            langs.addWidget(btn)
        lay.addLayout(langs)

        self.btn = QPushButton()
        self.btn.setObjectName("btnPrimary")
        self.btn.setFixedHeight(50)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self.accept)
        lay.addWidget(self.btn)

        self._apply_language()

    def _choose_language(self, lang):
        save_language(lang)
        self._apply_language()

    def _apply_language(self):
        self.desc.setText(t("welcome.body"))
        self.btn.setText(t("welcome.enter"))
        self.btn_en.setChecked(get_language() == "en")
        self.btn_es.setChecked(get_language() == "es")

# Hades writes saves under Documents\Saved Games\<game>\ProfileN.sav.
# Steam Cloud uses the same place: root "WinMyDocuments", path "Saved Games/Hades".
# The Documents folder can live off the system drive, so look it up instead of
# assuming it is under the user profile.
def _folder_guid(data1, data2, data3, data4):
    import ctypes

    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", ctypes.c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", ctypes.c_ubyte * 8),
        ]

    return GUID(data1, data2, data3, (ctypes.c_ubyte * 8)(*data4))


def _known_documents_dir():
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    folder_id = _folder_guid(
        0xFDD39AD0, 0x238F, 0x46AF,
        (0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7),
    )
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    ole32 = ctypes.WinDLL("ole32", use_last_error=True)
    shell32.SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(type(folder_id)),
        wintypes.DWORD,
        wintypes.HANDLE,
        ctypes.POINTER(ctypes.c_wchar_p),
    ]
    shell32.SHGetKnownFolderPath.restype = ctypes.c_long
    ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole32.CoTaskMemFree.restype = None
    out = ctypes.c_wchar_p()
    hr = shell32.SHGetKnownFolderPath(ctypes.byref(folder_id), 0, None, ctypes.byref(out))
    path = out.value
    if out:
        ole32.CoTaskMemFree(out)
    if hr != 0 or not path:
        return None
    return path


def _documents_dir():
    if sys.platform == "win32":
        known = _known_documents_dir()
        if known and os.path.isdir(known):
            return known
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            ) as key:
                personal, _typ = winreg.QueryValueEx(key, "Personal")
            if isinstance(personal, str) and os.path.isdir(personal):
                return personal
        except OSError:
            pass
    home_docs = os.path.join(os.path.expanduser("~"), "Documents")
    return home_docs if os.path.isdir(home_docs) else None


def hades_save_dir(game_name):
    """Return the existing save folder for 'Hades' or 'Hades II'."""
    candidates = []
    if sys.platform == "win32":
        docs = _documents_dir()
        if docs:
            candidates.append(os.path.join(docs, "Saved Games", game_name))
            candidates.append(os.path.join(docs, game_name))
        home_docs = os.path.join(os.path.expanduser("~"), "Documents")
        candidates.append(os.path.join(home_docs, "Saved Games", game_name))
        candidates.append(os.path.join(home_docs, game_name))
    else:
        candidates.append(os.path.expanduser(
            f"~/Library/Application Support/Supergiant Games/{game_name}"
        ))
    seen = set()
    for path in candidates:
        key = os.path.normcase(os.path.normpath(path))
        if key in seen:
            continue
        seen.add(key)
        if os.path.isdir(path):
            return path
    return None


def _is_profile_sav(name):
    stem, ext = os.path.splitext(name)
    if ext.lower() != ".sav" or not stem.lower().startswith("profile"):
        return False
    slot = stem[7:]
    return slot.isdigit() and slot != ""


def _active_profile_name(directory):
    """Hades writes the selected slot into a tiny SGB1 record named activeProfile."""
    try:
        with open(os.path.join(directory, "activeProfile"), "rb") as handle:
            data = handle.read(64)
    except OSError:
        return None
    if len(data) < 8 or not data.startswith(b"SGB1"):
        return None
    length = int.from_bytes(data[4:8], "little")
    if length <= 0 or len(data) < 8 + length:
        return None
    try:
        name = data[8:8 + length].decode("ascii")
    except UnicodeDecodeError:
        return None
    stem = name[:-4] if name.lower().endswith(".sav") else name
    if _is_profile_sav(stem + ".sav"):
        return stem
    return None


def preferred_profile_save(directory):
    """The profile the game has selected, or the newest ProfileN.sav."""
    if not directory or not os.path.isdir(directory):
        return None
    try:
        names = [name for name in os.listdir(directory) if _is_profile_sav(name)]
    except OSError:
        return None
    files = [
        os.path.join(directory, name)
        for name in names
        if os.path.isfile(os.path.join(directory, name))
    ]
    if not files:
        return None
    active = _active_profile_name(directory)
    if active:
        wanted = active.lower() + ".sav"
        for path in files:
            if os.path.basename(path).lower() == wanted:
                return path
    return max(files, key=os.path.getmtime)


# ── Main window ───────────────────────────────────────────────────────────────
class HadesEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.save_file: HadesSaveFile = None
        self.file_path: str = None

        self.setWindowTitle("HSE · Hades Save Editor")
        self.setMinimumSize(960, 700)
        self.resize(1100, 780)
        self.setStyleSheet(QSS)

        self.bg_widget = QWidget(self)
        self.bg_widget.setObjectName("mainWindowBackground")
        self.bg_widget.setGeometry(0, 0, 1100, 780)
        # Background is set dynamically in _on_game_toggled
        self.bg_overlay = QWidget(self.bg_widget)
        self.bg_overlay.setObjectName("bgOverlay")
        self.bg_overlay.setGeometry(0, 0, 1100, 780)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_title())
        root.addWidget(self._build_action_bar())
        root.addWidget(self._build_path_bar())

        self.tabs = QTabWidget()
        self.tabs.setEnabled(False)
        root.addWidget(self.tabs)
        self._rebuild_tabs()
        
        root.addWidget(self._build_footer())

    def _rebuild_tabs(self):
        self._heat_cells = {}
        self.tabs.clear()
        is_h2 = self.game_toggle.isChecked()
        if is_h2:
            self.tabs.addTab(self._tab_resources_h2(), t("tab.resources"))
            self.tabs.addTab(self._tab_weapons_h2(),   t("tab.weapons_h2"))
            self.tabs.addTab(self._tab_arcana_h2(),    t("tab.arcana"))
            self.tabs.addTab(self._tab_progress(),     t("tab.progress"))
        else:
            self.tabs.addTab(self._tab_resources(),      t("tab.resources"))
            self.tabs.addTab(self._tab_weapons(),         t("tab.weapons"))
            self.tabs.addTab(self._tab_heat(),            t("tab.heat"))
            self.tabs.addTab(self._tab_companions(),      t("tab.companions"))
            self.tabs.addTab(self._tab_items(),           t("tab.mirror"))
            self.tabs.addTab(self._tab_cosmetics_h1(),   t("tab.cosmetics"))
            self.tabs.addTab(self._tab_progress(),       t("tab.progress"))

    # ── Sections ──────────────────────────────────────────────────────────────
    def _build_title(self):
        w = QWidget()
        w.setObjectName("titleBar")
        w.setFixedHeight(88)
        h = QHBoxLayout(w)
        h.setContentsMargins(28, 0, 28, 0)

        # left text
        v = QVBoxLayout()
        v.setSpacing(2)
        v.addStretch()
        title = QLabel("HSE")
        title.setObjectName("appTitle")
        sub = QLabel("H A D E S   S A V E   E D I T O R   II")
        sub.setObjectName("appSubtitle")
        v.addWidget(title)
        v.addWidget(sub)
        v.addStretch()
        h.addLayout(v)
        h.addStretch()

        self._badge_ver = Badge("VERSION")
        self._badge_run = Badge("RUNS")
        self._badge_loc = Badge("LOCATION")
        for b in (self._badge_ver, self._badge_run, self._badge_loc):
            h.addWidget(b)
            h.addSpacing(10)
        return w

    def _build_action_bar(self):
        w = QWidget()
        w.setObjectName("actionBar")
        w.setFixedHeight(64)
        h = QHBoxLayout(w)
        h.setContentsMargins(24, 8, 24, 8)
        h.setSpacing(12)

        # Game Selector
        self.game_toggle = QPushButton("HADES I")
        self.game_toggle.setCheckable(True)
        self.game_toggle.setObjectName("gameToggle")
        self.game_toggle.toggled.connect(self._on_game_toggled)
        h.addWidget(self.game_toggle)
        h.addSpacing(10)

        self.btn_load = QPushButton(t("btn.load"))
        self.btn_load.setObjectName("btnPrimary")
        self.btn_load.clicked.connect(self._load)

        self.btn_save = QPushButton(t("btn.save"))
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._save)

        self.btn_max = QPushButton("✨  MAX")
        self.btn_max.setObjectName("btnMax")
        self.btn_max.setEnabled(False)
        self.btn_max.clicked.connect(self._max_all)

        btn_exit = QPushButton("✕")
        btn_exit.setObjectName("btnDanger")
        btn_exit.setFixedWidth(44)
        btn_exit.clicked.connect(self.close)

        for b in (self.btn_load, self.btn_save, self.btn_max):
            h.addWidget(b)
        h.addStretch()

        self.btn_en = QPushButton("English")
        self.btn_es = QPushButton("Español")
        for btn, lang in ((self.btn_en, "en"), (self.btn_es, "es")):
            btn.setObjectName("langToggle")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, chosen=lang: self._switch_language(chosen))
            h.addWidget(btn)
        self.btn_en.setChecked(get_language() == "en")
        self.btn_es.setChecked(get_language() == "es")
        h.addSpacing(8)
        h.addWidget(btn_exit)
        return w

    def _on_game_toggled(self, checked):
        name = "HADES II" if checked else "HADES I"
        self.game_toggle.setText(name)
        
        bg_path = "resources/HadesII_bg.png" if checked else "resources/HadesI_bg.png"
        self.bg_widget.setStyleSheet(f"border-image: url('{bg_path}');")
        
        self._rebuild_tabs()
        if not self.save_file:
            self._refresh_path_label()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_widget'):
            self.bg_widget.setGeometry(0, 0, self.width(), self.height())
            self.bg_overlay.setGeometry(0, 0, self.width(), self.height())


    def _build_path_bar(self):
        w = QWidget()
        w.setObjectName("pathBar")
        w.setFixedHeight(26)
        h = QHBoxLayout(w)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(8)
        k = QLabel(t("path.file"))
        k.setObjectName("pathKey")
        self._path_lbl = QLabel(t("path.none"))
        self._path_lbl.setObjectName("pathValue")
        h.addWidget(k)
        h.addWidget(self._path_lbl)
        h.addStretch()
        self._refresh_path_label()
        return w

    def _build_footer(self):
        w = QWidget()
        w.setFixedHeight(30)
        h = QHBoxLayout(w)
        h.setContentsMargins(24, 0, 24, 0)
        lbl = QLabel(t("footer"))
        lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; letter-spacing: 1px;")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        h.addWidget(lbl)
        return w

    # ── Tabs ──────────────────────────────────────────────────────────────────
    def _scroll_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {BG_DARK};")
        inner = QWidget()
        inner.setStyleSheet(f"background: {BG_DARK};")
        scroll.setWidget(inner)
        return scroll, inner

    def _tab_resources(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(20)

        grp = self._group(t("group.currencies"))
        grid = QGridLayout(grp)
        grid.setSpacing(14)

        resources = [
            ("🌑", "Darkness",     "darkness",     GOLD),
            ("💎", "Gems",         "gems",         "#60c0e0"),
            ("💠", "Diamonds",     "diamonds",     "#a080f0"),
            ("🍯", "Nectar",       "nectar",       "#e08020"),
            ("🍇", "Ambrosia",     "ambrosia",     "#c050a0"),
            ("🗝", "Chthonic Keys","chthonic_key", "#80a0c0"),
            ("🩸", "Titan Blood",  "titan_blood",  "#c03020"),
        ]
        self._res = {}
        for i, (icon, label, key, color) in enumerate(resources):
            card = ResourceCard(icon, label, color)
            self._res[key] = card
            grid.addWidget(card, i // 4, i % 4)

        lay.addWidget(grp)

        grp2 = self._group(t("group.modes"))
        h2 = QHBoxLayout(grp2)
        h2.setSpacing(32)
        self.chk_god  = self._fancy_check(t("mode.god"),   GOLD)
        self.chk_hell = self._fancy_check(t("mode.hell"),  RED)
        h2.addWidget(self.chk_god)
        h2.addWidget(self.chk_hell)
        h2.addStretch()
        lay.addWidget(grp2)
        lay.addStretch()
        return scroll

    def _tab_weapons(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 16, 24, 24)
        lay.setSpacing(4)

        hint = QLabel(t("aspect.hint"))
        hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; letter-spacing: 1px; "
                           f"padding: 8px 0 14px 0; background: transparent;")
        lay.addWidget(hint)

        self._weapon_cards = []
        for i, info in enumerate(WEAPONS):
            card = WeaponCard(info)
            self._weapon_cards.append(card)
            lay.addWidget(card)
            if i < len(WEAPONS) - 1:
                lay.addWidget(OrnaDivider())

        lay.addStretch()
        return scroll

    def _tab_heat(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 16, 24, 24)
        lay.setSpacing(12)

        hint = QLabel(t("heat.hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; letter-spacing: 0.4px; "
            f"padding: 8px 0 6px 0; background: transparent;"
        )
        lay.addWidget(hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 2)
        for col in range(1, 8):
            grid.setColumnStretch(col, 1)

        headers = [
            (t("heat.weapon"), ""),
            (t("heat.clears"), ""),
            (t("heat.best"), ""),
            (t("heat.fastest"), ""),
        ]
        headers.extend((t(title_key), t(sub_key)) for _room, title_key, sub_key in HEAT_BOSSES)
        for col, (title, subtitle) in enumerate(headers):
            grid.addWidget(self._heat_header(title, subtitle), 0, col)

        self._heat_cells = {}
        for row, info in enumerate(WEAPONS, start=1):
            accent, _bg = WEAPON_COLOR[info["key"]]
            grid.addWidget(self._heat_weapon_label(info, accent), row, 0)
            clears = HeatReadout(accent)
            best = HeatReadout(GOLD)
            fastest = HeatReadout(TEXT)
            bosses = {}
            grid.addWidget(clears, row, 1)
            grid.addWidget(best, row, 2)
            grid.addWidget(fastest, row, 3)
            for col, (room, _title_key, _sub_key) in enumerate(HEAT_BOSSES, start=4):
                cell = HeatReadout(GOLD)
                bosses[room] = cell
                grid.addWidget(cell, row, col)
            self._heat_cells[info["key"]] = {
                "clears": clears,
                "best": best,
                "time": fastest,
                "bosses": bosses,
            }

        lay.addLayout(grid)
        lay.addStretch()

        if self.save_file is not None:
            gs = self.save_file.lua_state._active_state.get("GameState", {})
            if isinstance(gs, dict):
                self._fill_heat(gs)
        return scroll

    def _heat_header(self, title, subtitle=""):
        text = title if not subtitle else f"{title}\n{subtitle}"
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; font-weight: 800; letter-spacing: 1px;"
            f"background: transparent; padding: 2px 4px;"
        )
        return lbl

    def _heat_weapon_label(self, info, accent):
        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(1)
        name = QLabel(f"{info['icon']}  {info['name']}")
        name.setStyleSheet(
            f"color: {accent}; font-size: 13px; font-weight: 800; letter-spacing: 1px; "
            f"background: transparent;"
        )
        sub = QLabel(info["sub"])
        sub.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; background: transparent;")
        lay.addWidget(name)
        lay.addWidget(sub)
        return wrap

    def _fill_heat(self, gs):
        cells = getattr(self, "_heat_cells", None)
        if not cells or not isinstance(gs, dict):
            return
        thresholds = gs.get("RecordClearedShrineThreshold") or {}
        rewards = gs.get("RecordLastClearedShrineReward") or {}
        clears = gs.get("TimesClearedWeapon") or {}
        best = gs.get("WeaponRecordsShrinePoints") or {}
        times = gs.get("WeaponRecordsClearTime") or {}
        for info in WEAPONS:
            key = info["key"]
            row = cells[key]
            weapon_thresholds = thresholds.get(key, {}) if isinstance(thresholds, dict) else {}
            weapon_rewards = rewards.get(key, {}) if isinstance(rewards, dict) else {}
            if not isinstance(weapon_thresholds, dict):
                weapon_thresholds = {}
            if not isinstance(weapon_rewards, dict):
                weapon_rewards = {}
            row["clears"].set_readout(_stat_text(clears.get(key) if isinstance(clears, dict) else None))
            row["best"].set_readout(_stat_text(best.get(key) if isinstance(best, dict) else None))
            row["time"].set_readout(_format_clear_time(times.get(key) if isinstance(times, dict) else None))
            for room, _title_key, _sub_key in HEAT_BOSSES:
                headline, detail, tip = _boss_heat_text(
                    weapon_thresholds.get(room), weapon_rewards.get(room)
                )
                row["bosses"][room].set_readout(headline, detail)
                row["bosses"][room].setToolTip(tip)

    def _tab_progress(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(20)

        grp = self._group(t("group.run_stats"))
        grid = QGridLayout(grp)
        grid.setSpacing(14)
        meta_res = [
            ("🏃", t("stat.runs"),     "runs",                "#80c080"),
            ("🌑", t("stat.darkness"), "active_meta_points",  GOLD),
            ("🏛", t("stat.shrine"),   "active_shrine_points","#a0b0f0"),
        ]
        self._meta = {}
        for i, (icon, label, key, color) in enumerate(meta_res):
            card = ResourceCard(icon, label, color)
            self._meta[key] = card
            grid.addWidget(card, 0, i)
        lay.addWidget(grp)

        grp2 = self._group(t("group.game_flags"))
        h2 = QHBoxLayout(grp2)
        h2.setSpacing(28)
        self.chk_aspects = self._fancy_check(t("flagbar.aspects"), "#c0a0f0")
        self.chk_gun     = self._fancy_check(t("flagbar.gun"), "#8090d0")
        h2.addWidget(self.chk_aspects)
        h2.addWidget(self.chk_gun)
        h2.addStretch()
        lay.addWidget(grp2)
        lay.addStretch()
        return scroll

    def _tab_companions(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(20)

        # ── NPCs / Companions ──
        NPCS = [
            ("NPC_Cerberus_01",        "🐺", "Cerberus",         "#e8a020"),
            ("NPC_Achilles_01",        "⚔", "Achilles",         "#e06040"),
            ("NPC_Nyx_01",             "🌙", "Nyx",              "#a060e0"),
            ("NPC_Hades_01",           "💀", "Hades",            "#c03020"),
            ("NPC_FurySister_01",      "😤", "Megaera",          "#d04060"),
            ("NPC_Thanatos_01",        "⚖", "Thanatos",         "#80b0e0"),
            ("NPC_Dusa_01",            "🐍", "Dusa",             "#60c080"),
            ("NPC_Orpheus_01",         "🎵", t("name.orpheus"),    "#c090f0"),
            ("NPC_Eurydice_01",        "🌿", t("name.eurydice"),   "#80e080"),
            ("NPC_Hypnos_01",          "💤", "Hypnos",           "#7090a0"),
            ("NPC_Sisyphus_01",        "🪨", t("name.sisyphus"),   "#a0b080"),
            ("NPC_Skelly_01",          "💀", "Skelly",           "#d0c0a0"),
            ("NPC_Patroclus_01",       "🛡", t("name.patroclus"),  "#a0c0e0"),
            ("NPC_Charon_01",          "⛵", t("name.charon"),     "#c0a040"),
        ]
        grp_npc = self._group(t("group.relationships"))
        g_lay = QGridLayout(grp_npc)
        g_lay.setSpacing(10)
        self._npc_spin = {}
        for i, (key, icon, label, color) in enumerate(NPCS):
            cell = QWidget()
            cell.setStyleSheet(f"""
                QWidget {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 7px;
                }}
            """)
            c_lay = QHBoxLayout(cell)
            c_lay.setContentsMargins(10, 6, 10, 6)
            c_lay.setSpacing(8)
            ico = QLabel(icon)
            ico.setStyleSheet(f"font-size: 20px; background: transparent; color: {color};")
            c_lay.addWidget(ico)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"background: transparent; font-size: 12px; min-width: 80px; color: {TEXT};")
            c_lay.addWidget(lbl)
            c_lay.addStretch()
            spin = QSpinBox()
            spin.setRange(0, 99)
            spin.setFixedWidth(68)
            spin.setStyleSheet(f"""
                QSpinBox {{ background: {BG_INSET}; border: 1px solid {BORDER};
                            border-radius: 5px; color: {color}; font-weight: bold;
                            font-size: 14px; padding: 3px 6px; }}
                QSpinBox:focus {{ border: 1px solid {color}; }}
            """)
            c_lay.addWidget(spin)
            self._npc_spin[key] = spin
            g_lay.addWidget(cell, i // 2, i % 2)
        lay.addWidget(grp_npc)

        # ── Important Flags ──
        FLAGS = [
            ("AspectsUnlocked",   "🗡",  t("flag.aspects"),     "#c0a0f0"),
            ("GunUnlocked",       "⚡",  t("flag.gun"),         "#8090d0"),
            ("FistUnlocked",      "✊",  t("flag.fists"),       "#e08060"),
            ("SkellyUnlocked",    "💀",  t("flag.skelly"),      "#d0c090"),
            ("MetEurydice",       "🌿",  t("flag.eurydice"),    "#70d070"),
            ("MetHades",          "👑",  t("flag.hades"),       "#e05050"),
            ("AllowFlashback",    "💭",  t("flag.flashbacks"),  "#8090b0"),
            ("SwapMetaupgradesEnabled", "🔄", t("flag.mirror_swap"), "#60b0c0"),
        ]
        grp_flags = self._group(t("group.unlock_flags"))
        fl_grid = QGridLayout(grp_flags)
        fl_grid.setSpacing(10)
        self._flag_checks = {}
        for i, (key, icon, label, color) in enumerate(FLAGS):
            chk = self._fancy_check(f"{icon}  {label}", color)
            self._flag_checks[key] = chk
            fl_grid.addWidget(chk, i // 2, i % 2)
        lay.addWidget(grp_flags)

        # ── Quest status ──
        QUESTS = [
            ("WeaponAspects",       "🗡",  t("quest.weapon_aspects")),
            ("WeaponUnlocks",       "🔓",  t("quest.weapon_unlocks")),
            ("FirstClear",          "🏆",  t("quest.first_clear")),
            ("MeetOlympians",       "⚡",  t("quest.olympians")),
            ("MeetChthonicGods",    "🌑",  t("quest.chthonic")),
            ("AresUpgrades",        "⚔",  t("quest.ares")),
            ("AthenaUpgrades",      "🛡",  t("quest.athena")),
            ("AphroditeUpgrades",   "💕",  t("quest.aphrodite")),
            ("DionysusUpgrades",    "🍇",  t("quest.dionysus")),
            ("DemeterUpgrades",     "❄",  t("quest.demeter")),
            ("ArtemisUpgrades",     "🏹",  t("quest.artemis")),
            ("PoseidonUpgrades",    "🌊",  t("quest.poseidon")),
            ("ZeusUpgrades",        "⚡",  t("quest.zeus")),
            ("HermesUpgrades",      "🪶",  t("quest.hermes")),
            ("OrpheusRelease",      "🎵",  t("quest.orpheus")),
            ("LegendaryUpgrades",   "✨",  t("quest.legendary")),
            ("CosmeticsSmall",      "🎨",  t("quest.cosmetics")),
            ("CodexSmall",          "📖",  t("quest.codex")),
            ("MiniBossKills",       "💀",  t("quest.miniboss")),
            ("KeepsakesQuest",      "🎁",  t("quest.keepsakes")),
        ]
        grp_q = self._group(t("group.quests"))
        q_grid = QGridLayout(grp_q)
        q_grid.setSpacing(8)
        self._quest_checks = {}
        for i, (key, icon, label) in enumerate(QUESTS):
            chk = QCheckBox(f"{icon}  {label}")
            chk.setStyleSheet(f"""
                QCheckBox {{ color: {TEXT}; font-size: 12px; background: transparent; }}
                QCheckBox::indicator {{ width: 18px; height: 18px;
                    border: 2px solid {BORDER_LT}; border-radius: 4px;
                    background: {BG_INSET}; }}
                QCheckBox::indicator:checked {{ background: {GOLD_DIM};
                    border-color: {GOLD}; }}
            """)
            self._quest_checks[key] = chk
            q_grid.addWidget(chk, i // 3, i % 3)
        lay.addWidget(grp_q)
        lay.addStretch()
        return scroll

    def _tab_cosmetics_h1(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(20)

        hint = QLabel(t("cosmetics.hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; padding-bottom: 6px;")
        lay.addWidget(hint)

        COSMETICS_SECTIONS = [
            (t("cos.decor"), [
                ("Cosmetic_SouthHallTrimGrey",   t("cos.trim_grey")),
                ("Cosmetic_SouthHallTrimBrown",  t("cos.trim_brown")),
                ("Cosmetic_SouthHallTrimRed",    t("cos.trim_red")),
                ("Cosmetic_SouthHallTrimPurple", t("cos.trim_purple")),
                ("Cosmetic_DrapesBlue",          t("cos.drapes_blue")),
                ("Cosmetic_DrapesRed",           t("cos.drapes_red")),
                ("Cosmetic_HouseCandles01",      t("cos.candles")),
                ("Cosmetic_LaurelsRed",          t("cos.laurels")),
                ("Cosmetic_NorthHallCouch",      t("cos.couch_north")),
                ("Cosmetic_SouthHallFlowers",    t("cos.flowers")),
                ("Cosmetic_SouthHallFlowersA",   t("cos.flowers_alt")),
                ("Cosmetic_WallWeaponBident",    t("cos.bident")),
                ("Cosmetic_ClearFur",           t("cos.fur")),
                ("Cosmetic_MusicPlayer",        t("cos.music_player")),
                ("Cosmetic_UISkinDefault",      t("cos.ui_skin")),
                ("HouseCouch02A",               t("cos.main_couch")),
                ("HouseLyre01",                 t("cos.lyre")),
                ("HousePoster01",               t("cos.poster")),
                ("HouseRug03B",                 t("cos.rug")),
                ("HouseWaterBowl01",            t("cos.bowl")),
            ]),
            (t("cos.gameplay"), [
                ("BreakableValue1",    t("cos.breakable1")),
                ("BreakableValue2",    t("cos.breakable2")),
                ("BreakableValue3",    t("cos.breakable3")),
                ("ChallengeSwitches1", t("cos.switches1")),
                ("ChallengeSwitches2", t("cos.switches2")),
                ("HealthFountainHeal1", t("cos.fountain1")),
                ("HealthFountainHeal2", t("cos.fountain2")),
                ("FishingUnlockItem",  t("cos.fishing")),
                ("QuestLog",           t("cos.quest_log")),
                ("CodexBoonList",      t("cos.codex_boons")),
            ]),
            (t("cos.story"), [
                ("OfficeDoorUnlockItem", t("cos.office_door")),
                ("OrpheusUnlockItem",    t("cos.orpheus")),
                ("GhostAdminDesk",       t("cos.admin_desk")),
                ("PostBossGiftRack",     t("cos.gift_rack")),
            ]),
            (t("cos.reprieves"), [
                ("TartarusReprieve",  t("cos.tartarus")),
                ("AsphodelReprieve",  t("cos.asphodel")),
                ("ElysiumReprieve",   t("cos.elysium")),
            ]),
            (t("cos.music"), [
                ("/Music/MusicPlayer/MainThemeMusicPlayer",      t("cos.theme")),
                ("/Music/MusicPlayer/EurydiceSong1MusicPlayer",  t("cos.eurydice_song")),
                ("/Music/MusicPlayer/MusicExploration4MusicPlayer", t("cos.exploration")),
            ]),
        ]

        self._cosmetic_checks = {}
        for section_title, items in COSMETICS_SECTIONS:
            grp = self._group(section_title)
            grid = QGridLayout(grp)
            grid.setSpacing(8)
            for i, (key, label) in enumerate(items):
                chk = self._fancy_check(label, GOLD)
                self._cosmetic_checks[key] = chk
                grid.addWidget(chk, i // 3, i % 3)
            lay.addWidget(grp)

        lay.addStretch()
        return scroll

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _group(self, title):
        g = QGroupBox(title)
        return g

    def _fancy_check(self, text, color):
        c = QCheckBox(text)
        c.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px; font-weight: bold;
                letter-spacing: 1px; color: {color};
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 22px; height: 22px;
                border: 2px solid {color};
                border-radius: 6px;
                background: {BG_INSET};
            }}
            QCheckBox::indicator:checked {{
                background: {color};
                border-color: {color};
            }}
        """)
        return c

    def _game_save_name(self):
        return "Hades II" if self.game_toggle.isChecked() else "Hades"

    def _hades_dir(self):
        found = hades_save_dir(self._game_save_name())
        return found if found else os.path.expanduser("~")

    def _dialog_start(self):
        directory = hades_save_dir(self._game_save_name())
        if not directory:
            return os.path.expanduser("~")
        return preferred_profile_save(directory) or directory

    def _refresh_path_label(self):
        if self.save_file:
            if self.file_path:
                self._path_lbl.setText(self.file_path)
            return
        directory = hades_save_dir(self._game_save_name())
        newest = preferred_profile_save(directory) if directory else None
        if newest:
            self._path_lbl.setText(t("path.found", path=newest))
        elif directory:
            self._path_lbl.setText(t("path.found_dir", path=directory))
        else:
            game_sub = "HADES II" if self.game_toggle.isChecked() else "HADES"
            self._path_lbl.setText(t("path.mode", game=game_sub))
        self._path_lbl.setToolTip(self._path_lbl.text())

    # ── Items tab (Mirror + Keepsakes) ────────────────────────────────────────
    def _tab_items(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(20)

        # Mirror upgrades
        MIRROR = [
            ("HealthMetaUpgrade",             "❤",  t("mirror.health"),          10, "#c03030"),
            ("AmmoMetaUpgrade",               "🔵",  t("mirror.ammo"),            6,  "#4080c0"),
            ("ExtraChanceMetaUpgrade",        "♻",  t("mirror.extra_chance"),    1,  "#60a060"),
            ("ExtraChanceReplenishMetaUpgrade","♻", t("mirror.extra_replenish"), 1,  "#50c060"),
            ("StaminaMetaUpgrade",            "💨",  t("mirror.stamina"),         1,  "#80c0f0"),
            ("RareBoonDropMetaUpgrade",       "⭐",  t("mirror.rare"),            40, "#c0a030"),
            ("EpicBoonDropMetaUpgrade",       "💫",  t("mirror.epic"),            40, "#a030c0"),
            ("GodEnhancementMetaUpgrade",     "⚡",  t("mirror.privileged"),      1,  "#a0a0f0"),
            ("DuoRarityBoonDropMetaUpgrade",  "🔗",  t("mirror.duo"),             40, "#f09030"),
            ("BackstabMetaUpgrade",           "🗡",  t("mirror.backstab"),        5,  "#e06020"),
            ("FirstStrikeMetaUpgrade",        "⚡",  t("mirror.first_strike"),    5,  "#e0c020"),
            ("PerfectDashMetaUpgrade",        "✨",  t("mirror.perfect_dash"),    5,  "#30c0f0"),
            ("MoneyMetaUpgrade",              "💰",  t("mirror.money"),           5,  "#c0c040"),
            ("DarknessHealMetaUpgrade",       "🌑",  t("mirror.darkness_heal"),   5,  "#8040a0"),
            ("DoorHealMetaUpgrade",           "🚪",  t("mirror.door_heal"),       5,  "#309050"),
            ("InterestMetaUpgrade",           "👜",  t("mirror.interest"),        5,  "#c0a040"),
            ("RerollMetaUpgrade",             "🎲",  t("mirror.reroll"),          5,  "#6090d0"),
            ("ReloadAmmoMetaUpgrade",         "🔄",  t("mirror.reload"),          5,  "#4090c0"),
            ("RunProgressRewardMetaUpgrade",  "🏆",  t("mirror.run_progress"),    5,  "#d06030"),
        ]
        grp_mirror = self._group(t("group.mirror"))
        m_grid = QGridLayout(grp_mirror)
        m_grid.setSpacing(10)
        self._mirror_spin = {}
        for i, (key, icon, label, maxv, color) in enumerate(MIRROR):
            cell = QWidget()
            cell.setStyleSheet(f"""
                QWidget {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 7px;
                }}
            """)
            c = QHBoxLayout(cell)
            c.setContentsMargins(10, 6, 10, 6)
            c.setSpacing(6)
            ico = QLabel(icon)
            ico.setStyleSheet(f"font-size: 18px; background: transparent; color: {color};")
            c.addWidget(ico)
            lbl = QLabel(label)
            lbl.setWordWrap(False)
            lbl.setStyleSheet(f"background: transparent; font-size: 11px; color: {TEXT}; min-width: 200px;")
            c.addWidget(lbl)
            c.addStretch()
            spin = QSpinBox()
            spin.setRange(0, maxv)
            spin.setFixedWidth(62)
            spin.setStyleSheet(f"""
                QSpinBox {{ background: {BG_INSET}; border: 1px solid {BORDER};
                            border-radius: 5px; color: {color}; font-weight: bold;
                            font-size: 13px; padding: 2px 5px; }}
                QSpinBox:focus {{ border: 1px solid {color}; }}
            """)
            c.addWidget(spin)
            lim = QLabel(f" / {maxv}")
            lim.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; background: transparent;")
            c.addWidget(lim)
            self._mirror_spin[key] = spin
            m_grid.addWidget(cell, i // 2, i % 2)
        lay.addWidget(grp_mirror)

        # Mapping Trait -> Gift NPC Key for unlocking
        KS_NPC = {
            "MaxHealthKeepsakeTrait": "NPC_Cerberus_01",
            "ForceArtemisBoonTrait": "ArtemisUpgrade",
            "ForceAphroditeBoonTrait": "AphroditeUpgrade",
            "ForceAresBoonTrait": "AresUpgrade",
            "ForceAthenaBoonTrait": "AthenaUpgrade",
            "ForceDionysusBoonTrait": "DionysusUpgrade",
            "ForceZeusBoonTrait": "ZeusUpgrade",
            "ForceHermesBoonTrait": "HermesUpgrade",
            "ForcePoseidonBoonTrait": "PoseidonUpgrade",
            "ForceDemeterBoonTrait": "DemeterUpgrade",
            "PerfectClearDamageBonusTrait": "NPC_Dusa_01",
            "BonusMoneyTrait": "NPC_Charon_01",
            "ReincarnationTrait": "NPC_Sisyphus_01",
            "MoveSpeedKeepsakeTrait": "NPC_Thanatos_01",
            "RapidBoonsKeepsakeTrait": "NPC_Orpheus_01",
            "TemporaryInvulnerabilityTrait": "NPC_Eurydice_01",
            "HealingItemKeepsakeTrait": "NPC_Skelly_01", # Skelly gives Lucky Tooth
            "ForceBlessedTrait": "NPC_Skelly_01",
            "RoomMoneyBonusTrait": "NPC_Patroclus_01",
            "ForceAchillesBoonTrait": "NPC_Achilles_01",
            "GodModeFasterLockPickTrait": "ChaosUpgrade", # Chaos doesn't have an upgrade key? Usually it's Gift[NPC_Chaos_01]
        }

        # Keepsakes — all Hades keepsakes by their KeepsakeChambers trait name
        KEEPSAKES = [
            ("MaxHealthKeepsakeTrait",         "🐶", "Old Spiked Collar",          "Cerberus",  "#e8a020", "NPC_Cerberus_01"),
            ("ForceArtemisBoonTrait",           "🏹", "Adamant Arrowhead",          t("name.artemis"),   "#60d060", "ArtemisUpgrade"),
            ("ForceAphroditeBoonTrait",         "🌹", "Eternal Rose",              t("name.aphrodite"), "#f060a0", "AphroditeUpgrade"),
            ("ForceAresBoonTrait",              "⚔",  "Blood-Filled Vial",         "Ares",      "#c03020", "AresUpgrade"),
            ("ForceAthenaBoonTrait",            "🛡",  "Owl Pendant",               t("name.athena"),    "#60a0e0", "AthenaUpgrade"),
            ("ForceDionysusBoonTrait",          "🍇", "Overflowing Cup",           t("name.dionysus"),  "#c050c0", "DionysusUpgrade"),
            ("ForceZeusBoonTrait",              "⚡",  "Thunder Signet",            "Zeus",      "#d0c020", "ZeusUpgrade"),
            ("ForceHermesBoonTrait",            "🪶", "Lambent Plume",             "Hermes",    "#d0d090", "HermesUpgrade"),
            ("ForcePoseidonBoonTrait",          "🌊", "Conch Shell",               t("name.poseidon"),  "#3090d0", "PoseidonUpgrade"),
            ("ForceDemeterBoonTrait",           "❄",  "Pom Blossom",               t("name.demeter"),   "#80b0d0", "DemeterUpgrade"),
            ("PerfectClearDamageBonusTrait",   "🐍", "Harpy Feather Duster",      "Dusa",      "#60c080", "NPC_Dusa_01"),
            ("BonusMoneyTrait",                "💰", "Charon's Obol",             t("name.charon"),    "#c0a040", "NPC_Charon_01"),
            ("ReincarnationTrait",             "💀", "Shattered Shackle",         t("name.sisyphus"),  "#909090", "NPC_Sisyphus_01"),
            ("MoveSpeedKeepsakeTrait",         "💨", "Pierced Butterfly",         "Thanatos",  "#80b0e0", "NPC_Thanatos_01"),
            ("RapidBoonsKeepsakeTrait",        "🎵", "Lyre of Orpheus",           t("name.orpheus"),   "#c090f0", "NPC_Orpheus_01"),
            ("TemporaryInvulnerabilityTrait",  "🌿", "Evergreen Acorn",           t("name.eurydice"),  "#80e080", "NPC_Eurydice_01"),
            ("HealingItemKeepsakeTrait",       "🍷", "Nectar / Bracer",           t("name.sisyphus_achilles"), "#a0b080", "NPC_Sisyphus_01"),
            ("ForceBlessedTrait",              "🦴", "Lucky Tooth",               "Skelly",    "#d0c090", "NPC_Skelly_01"),
            ("RoomMoneyBonusTrait",            "🛡",  "Black Shawl",               t("name.patroclus"), "#a0c0e0", "NPC_Patroclus_01"),
            ("ForceAchillesBoonTrait",         "⚔",  "Broken Spearpoint",         "Achilles",  "#e06040", "NPC_Achilles_01"),
        ]
        grp_ks = self._group(t("group.keepsakes"))
        ks_grid = QGridLayout(grp_ks)
        ks_grid.setSpacing(8)
        self._ks_spin = {}
        self._ks_unlock = {}
        for i, (key, icon, label, source, color, npc_key) in enumerate(KEEPSAKES):
            cell = QWidget()
            cell.setStyleSheet(f"""
                QWidget {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 7px;
                }}
            """)
            c = QHBoxLayout(cell)
            c.setContentsMargins(8, 4, 8, 4)
            c.setSpacing(6)
            
            chk = QCheckBox()
            chk.setToolTip(t("keepsake.unlocked"))
            chk.setStyleSheet(f"QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {color}; border-radius: 3px; }} QCheckBox::indicator:checked {{ background: {color}; }}")
            c.addWidget(chk)
            self._ks_unlock[key] = (chk, npc_key)

            ico = QLabel(icon)
            ico.setStyleSheet(f"font-size: 16px; background: transparent; color: {color};")
            c.addWidget(ico)
            info_v = QVBoxLayout()
            info_v.setSpacing(0)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"background: transparent; font-size: 12px; color: {TEXT}; font-weight: bold;")
            src = QLabel(source)
            src.setStyleSheet(f"background: transparent; font-size: 9px; color: {color}; letter-spacing: 1px;")
            info_v.addWidget(lbl)
            info_v.addWidget(src)
            c.addLayout(info_v)
            c.addStretch()
            
            self.stars = StarLevel(color)
            c.addWidget(self.stars)
            
            spin = QSpinBox()
            spin.setRange(0, 9999)
            spin.setFixedWidth(65)
            spin.setStyleSheet(f"""
                QSpinBox {{ background: {BG_INSET}; border: 1px solid {BORDER};
                            border-radius: 5px; color: {color}; font-weight: bold;
                            font-size: 12px; padding: 2px 4px; }}
                QSpinBox:focus {{ border: 1px solid {color}; }}
            """)
            c.addWidget(spin)
            
            # Sync stars and spin
            spin.valueChanged.connect(self.stars.set_value)
            self.stars.valueChanged.connect(spin.setValue)
            
            self._ks_spin[key] = spin
            ks_grid.addWidget(cell, i // 2, i % 2)
        lay.addWidget(grp_ks)
        lay.addStretch()
        return scroll

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _load(self):
        opts = QFileDialog.Options()
        opts |= QFileDialog.DontUseNativeDialog
        path, _ = QFileDialog.getOpenFileName(
            self, t("dialog.load_title"), self._dialog_start(),
            t("dialog.filter"), options=opts
        )
        if not path:
            return
        try:
            self.save_file = HadesSaveFile.from_file(path)
            self.file_path = path
            self._populate()
            self.tabs.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.btn_max.setEnabled(True)
            self._path_lbl.setText(path)
        except Exception as e:
            QMessageBox.critical(self, t("dialog.load_error"), str(e))

    def _populate(self):
        sf = self.save_file
        gs = sf.lua_state._active_state.get("GameState", {})
        is_h2 = self.game_toggle.isChecked()

        self._badge_ver.set_value(sf.version)
        self._badge_run.set_value(sf.runs)
        self._badge_loc.set_value(sf.location.replace("Location_", ""))

        if is_h2:
            res = gs.get("Resources", {})
            for key, card in self._res_h2.items():
                card.set_value(int(res.get(key, 0)))
            
            # Armas y Herramientas — usar WorldUpgradesAdded como fuente real
            wua = gs.get("WorldUpgradesAdded", {})
            wu  = gs.get("WeaponsUnlocked", {})
            for wua_key, (chk, wu_key) in self._w_h2.items():
                chk.setChecked(wua_key in wua or wu_key in wu)
            for wua_key, (chk, wu_key) in self._t_h2.items():
                chk.setChecked(wua_key in wua or wu_key in wu)
            
            mus = gs.get("MetaUpgradeState", {})
            for key, chk in self._arcana_checks.items():
                card_data = mus.get(key, {})
                chk.setChecked(bool(card_data.get("Unlocked", False)))
        else:
            for key, val in {
                "darkness":      sf.lua_state.darkness,
                "gems":          sf.lua_state.gems,
                "diamonds":      sf.lua_state.diamonds,
                "nectar":        sf.lua_state.nectar,
                "ambrosia":      sf.lua_state.ambrosia,
                "chthonic_key":  sf.lua_state.chthonic_key,
                "titan_blood":   sf.lua_state.titan_blood,
            }.items():
                self._res[key].set_value(val or 0)

            self.chk_god.setChecked(bool(sf.god_mode_enabled))
            self.chk_hell.setChecked(bool(sf.hell_mode_enabled))

            wu  = gs.get("WeaponsUnlocked", {})
            wul = gs.get("WeaponUnlocks", {})
            for card in self._weapon_cards:
                card.load(wu, wul)

            self._fill_heat(gs)

            # Companions tab
            gift = gs.get("Gift", {})
            for key, spin in self._npc_spin.items():
                val = gift.get(key, {}).get("Value", 0) if isinstance(gift.get(key), dict) else 0
                spin.setValue(int(val))

            flags = gs.get("Flags", {})
            for key, chk in self._flag_checks.items():
                chk.setChecked(bool(flags.get(key, False)))

            quest = gs.get("QuestStatus", {})
            for key, chk in self._quest_checks.items():
                status = quest.get(key, "")
                chk.setChecked(status in ("CashedOut", "Completed"))

            # Items tab
            meta_ups = gs.get("MetaUpgrades", {})
            for key, spin in self._mirror_spin.items():
                spin.setValue(int(meta_ups.get(key, 0)))

            kc = gs.get("KeepsakeChambers", {})
            for key, spin in self._ks_spin.items():
                spin.setValue(int(kc.get(key, 0)))

            for key, (chk, npc_key) in self._ks_unlock.items():
                val = gift.get(npc_key, {}).get("Value", 0) if isinstance(gift.get(npc_key), dict) else 0
                chk.setChecked(val > 0)

            # Cosméticos — leer desde CosmeticsAdded
            cosmetics_added = gs.get("CosmeticsAdded", {})
            for key, chk in self._cosmetic_checks.items():
                chk.setChecked(bool(cosmetics_added.get(key, False)))

        self._meta["runs"].set_value(sf.runs)
        self._meta["active_meta_points"].set_value(sf.active_meta_points)
        self._meta["active_shrine_points"].set_value(sf.active_shrine_points)

    def _collect(self):
        sf = self.save_file
        gs = sf.lua_state._active_state.setdefault("GameState", {})
        is_h2 = self.game_toggle.isChecked()

        sf.runs                 = int(self._meta["runs"].value())
        sf.active_meta_points   = int(self._meta["active_meta_points"].value())
        sf.active_shrine_points = int(self._meta["active_shrine_points"].value())

        if is_h2:
            res = gs.setdefault("Resources", {})
            lifes = gs.setdefault("LifetimeResources", {})
            for key, card in self._res_h2.items():
                val = float(card.value())
                res[key] = val
                # In Hades II, we must also update LifetimeResources for the game to recognize unlocks
                if key not in ("Money"):
                    lifes[key] = max(lifes.get(key, 0), val)
            
            # Armas: escribir en WeaponsUnlocked, WeaponUnlocks Y WorldUpgradesAdded+Revealed
            wu  = gs.setdefault("WeaponsUnlocked", {})
            wul = gs.setdefault("WeaponUnlocks", {})
            wua = gs.setdefault("WorldUpgradesAdded", {})
            wur = gs.setdefault("WorldUpgradesRevealed", {})
            wuv = gs.setdefault("WorldUpgradesViewed", {})
            for wua_key, (chk, wu_key) in self._w_h2.items():
                if chk.isChecked():
                    wu[wu_key]   = 1.0
                    wul[wu_key]  = 1.0
                    wua[wua_key] = 1.0
                    wur[wua_key] = 1.0
                    wuv[wua_key] = 1.0
                else:
                    wu.pop(wu_key, None)
                    wul.pop(wu_key, None)
                    wua.pop(wua_key, None)
            for wua_key, (chk, wu_key) in self._t_h2.items():
                if chk.isChecked():
                    wu[wu_key]   = 1.0
                    wul[wu_key]  = 1.0
                    wua[wua_key] = 1.0
                    wur[wua_key] = 1.0
                    wuv[wua_key] = 1.0
                else:
                    wu.pop(wu_key, None)
                    wul.pop(wu_key, None)
                    wua.pop(wua_key, None)
            
            mus = gs.setdefault("MetaUpgradeState", {})
            for key, chk in self._arcana_checks.items():
                if key not in mus: mus[key] = {"Level": 1.0, "AdjacencyBonuses": {}}
                val = 1.0 if chk.isChecked() else 0.0
                mus[key]["Unlocked"] = val
                mus[key]["Equipped"] = val
        else:
            sf.lua_state.darkness     = self._res["darkness"].value()
            sf.lua_state.gems         = self._res["gems"].value()
            sf.lua_state.diamonds     = self._res["diamonds"].value()
            sf.lua_state.nectar       = self._res["nectar"].value()
            sf.lua_state.ambrosia     = self._res["ambrosia"].value()
            sf.lua_state.chthonic_key = self._res["chthonic_key"].value()
            sf.lua_state.titan_blood  = self._res["titan_blood"].value()

            sf.god_mode_enabled  = self.chk_god.isChecked()
            sf.hell_mode_enabled = self.chk_hell.isChecked()

            wu  = gs.setdefault("WeaponsUnlocked", {})
            wul = gs.setdefault("WeaponUnlocks", {})
            for card in self._weapon_cards:
                card.save(wu, wul)

            flags = gs.setdefault("Flags", {})
            for key, chk in self._flag_checks.items():
                flags[key] = chk.isChecked()

            gift = gs.setdefault("Gift", {})
            for key, spin in self._npc_spin.items():
                if key not in gift or not isinstance(gift[key], dict):
                    gift[key] = {"Value": float(spin.value()), "NewTraits": {}}
                else:
                    gift[key]["Value"] = float(spin.value())

            quest = gs.setdefault("QuestStatus", {})
            for key, chk in self._quest_checks.items():
                if chk.isChecked(): quest[key] = "CashedOut"
                else: quest.pop(key, None)

            meta_ups   = gs.setdefault("MetaUpgrades", {})
            meta_state = gs.setdefault("MetaUpgradeState", {})
            for key, spin in self._mirror_spin.items():
                val = float(spin.value())
                meta_ups[key] = val
                meta_state[key] = val

            kc = gs.setdefault("KeepsakeChambers", {})
            for key, spin in self._ks_spin.items():
                kc[key] = float(spin.value())

            for key, (chk, npc_key) in self._ks_unlock.items():
                if chk.isChecked():
                    if npc_key not in gift or not isinstance(gift[npc_key], dict):
                        gift[npc_key] = {"Value": 1.0, "NewTraits": {}}
                    elif gift[npc_key].get("Value", 0) == 0: gift[npc_key]["Value"] = 1.0
                else:
                    if npc_key in gift and isinstance(gift[npc_key], dict): gift[npc_key]["Value"] = 0.0

            # Cosméticos — escribir en Cosmetics + CosmeticsAdded + CosmeticsViewed
            cosmetics      = gs.setdefault("Cosmetics", {})
            cosmetics_add  = gs.setdefault("CosmeticsAdded", {})
            cosmetics_view = gs.setdefault("CosmeticsViewed", {})
            for key, chk in self._cosmetic_checks.items():
                if chk.isChecked():
                    cosmetics[key]      = "visible"
                    cosmetics_add[key]  = True
                    cosmetics_view[key] = True
                else:
                    # Si no está marcado, quitar de CosmeticsAdded pero mantener en Cosmetics como pending
                    cosmetics_add.pop(key, None)
                    if key in cosmetics:
                        cosmetics[key] = "pending"


    def _save(self):
        opts = QFileDialog.Options()
        opts |= QFileDialog.DontUseNativeDialog
        path, _ = QFileDialog.getSaveFileName(
            self, t("dialog.save_title"),
            self.file_path or self._dialog_start(),
            t("dialog.filter"), options=opts
        )
        if not path:
            return
        try:
            self._collect()
            self.save_file.to_file(path)
            self.file_path = path
            self._path_lbl.setText(path)
            QMessageBox.information(self, t("dialog.saved_title"), t("dialog.saved_body", path=path))
        except Exception as e:
            QMessageBox.critical(self, t("dialog.save_error"), str(e))

    def _max_all(self):
        pass  # merged below

    def _max_all(self):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle(t("dialog.max_title"))
        box.setText(t("dialog.max_body"))
        yes = box.addButton(t("dialog.yes"), QMessageBox.YesRole)
        box.addButton(t("dialog.no"), QMessageBox.NoRole)
        box.exec_()
        if box.clickedButton() is not yes:
            return

        is_h2 = self.game_toggle.isChecked()
        if is_h2:
            for card in self._res_h2.values():
                card.set_value(99999)
            for chk in self._w_h2.values():
                chk[0].setChecked(True)
            for chk in self._t_h2.values():
                chk[0].setChecked(True)
            for chk in self._arcana_checks.values():
                chk.setChecked(True)
        else:
            # ─ Recursos
            for card in self._res.values():
                card.set_value(99999)

            # ─ Armas y aspectos (incluyendo el aspecto oculto 4)
            for wc in self._weapon_cards:
                wc._max_all()
            self.chk_aspects.setChecked(True)
            self.chk_gun.setChecked(True)

            # ─ Afinidad NPCs (necesaria para aspectos ocultos)
            for spin in self._npc_spin.values():
                spin.setValue(10)

            # ─ Flags (AspectsUnlocked etc)
            for chk in self._flag_checks.values():
                chk.setChecked(True)

            # ─ Quests completadas
            for chk in self._quest_checks.values():
                chk.setChecked(True)

            # ─ Espejo al máximo
            for key, spin in self._mirror_spin.items():
                spin.setValue(spin.maximum())

            # ─ Recuerdos (keepsakes) al máximo
            for spin in self._ks_spin.values():
                spin.setValue(500)

            # ─ Forzar desbloqueo de aspectos ocultos directamente en el GameState
            # (sin necesidad de haber tenido las conversaciones previas)
            if self.save_file:
                gs = self.save_file.lua_state._active_state.setdefault("GameState", {})

                # Flag global de aspectos (Nyx da la sangre de titán para aspectos)
                flags = gs.setdefault("Flags", {})
                flags["AspectsUnlocked"] = True

                # Cada aspecto oculto (slot 4) se desbloquea con sangre de titán en WeaponUnlocks
                # y con el Gift del NPC correspondiente
                WEAPONS_H1 = ["SwordWeapon", "SpearWeapon", "ShieldWeapon",
                               "BowWeapon", "FistWeapon", "GunWeapon"]
                wul = gs.setdefault("WeaponUnlocks", {})
                for wk in WEAPONS_H1:
                    if wk not in wul:
                        wul[wk] = {}
                    # Asegurar slots 1-4 desbloqueados (slot 4 = aspecto oculto)
                    for slot in [1.0, 2.0, 3.0, 4.0]:
                        if slot not in wul[wk]:
                            wul[wk][slot] = 1.0

                # Gift de NPCs que habilitan los aspectos ocultos (mínimo valor 6 para
                # activar el diálogo de revelación que el juego comprueba internamente)
                ASPECT_GIFTS = [
                    "NPC_Achilles_01", "NPC_Nyx_01", "NPC_Thanatos_01",
                    "NPC_Charon_01", "NPC_Sisyphus_01",
                ]
                gift = gs.setdefault("Gift", {})
                for npc in ASPECT_GIFTS:
                    if npc not in gift or not isinstance(gift.get(npc), dict):
                        gift[npc] = {"Value": 6.0, "NewTraits": {}}
                    else:
                        gift[npc]["Value"] = max(float(gift[npc].get("Value", 0)), 6.0)

                # QuestStatus para WeaponAspects (sin esto el juego no muestra el aspecto)
                quest = gs.setdefault("QuestStatus", {})
                quest["WeaponAspects"] = "CashedOut"

                # ─ Cosméticos de la tienda (todos los conocidos de Hades 1)
                ALL_COSMETICS = [
                    "Cosmetic_SouthHallTrimGrey", "Cosmetic_SouthHallTrimBrown",
                    "Cosmetic_SouthHallTrimRed", "Cosmetic_SouthHallTrimPurple",
                    "Cosmetic_DrapesBlue", "Cosmetic_DrapesRed",
                    "Cosmetic_HouseCandles01", "Cosmetic_LaurelsRed",
                    "Cosmetic_NorthHallCouch", "Cosmetic_SouthHallFlowers",
                    "Cosmetic_SouthHallFlowersA", "Cosmetic_WallWeaponBident",
                    "Cosmetic_ClearFur", "Cosmetic_UISkinDefault", "Cosmetic_MusicPlayer",
                    "HouseCouch02A", "HouseLyre01", "HousePoster01",
                    "HouseRug03B", "HouseWaterBowl01",
                    "BreakableValue1", "BreakableValue2", "BreakableValue3",
                    "ChallengeSwitches1", "ChallengeSwitches2",
                    "OfficeDoorUnlockItem", "OrpheusUnlockItem", "FishingUnlockItem",
                    "GhostAdminDesk", "PostBossGiftRack", "QuestLog",
                    "HealthFountainHeal1", "HealthFountainHeal2",
                    "TartarusReprieve", "AsphodelReprieve", "ElysiumReprieve",
                    "CodexBoonList", "/Music/MusicPlayer/EurydiceSong1MusicPlayer",
                    "/Music/MusicPlayer/MainThemeMusicPlayer",
                    "/Music/MusicPlayer/MusicExploration4MusicPlayer",
                ]
                cosmetics     = gs.setdefault("Cosmetics", {})
                cosmetics_add = gs.setdefault("CosmeticsAdded", {})
                cosmetics_view = gs.setdefault("CosmeticsViewed", {})
                for c in ALL_COSMETICS:
                    cosmetics[c]      = "visible"
                    cosmetics_add[c]  = True
                    cosmetics_view[c] = True

                QMessageBox.information(
                    self, t("dialog.max_done_title"),
                    t("dialog.max_done_body")
                )

    def _tab_resources_h2(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(20)

        RESOURCES_H2 = [
            ("🌑", t("h2.ash"),    "MetaPoints",    GOLD),
            ("🧠", t("h2.psyche"), "Memories",      "#a080f0"),
            ("🦴", t("h2.bones"),  "Bones",         "#f0f0f2"),
            ("💰", t("h2.gold"),    "Money",         "#ffd700"),
            ("🧶", t("h2.fabric"), "FateFabric",    "#60c0e0"),
            ("⚒", t("h2.silver"), "Silver",        "#d0d0d0"),
            ("🥉", t("h2.bronze"), "Bronze",        "#cd7f32"),
            ("⛓", t("h2.iron"),   "OrestesIron",   "#708090"),
            ("🌙", t("h2.moon"),   "MoonDust",      "#40c0f0"),
            ("✨", t("h2.star"),   "StarDust",      "#ffe0a0"),
            ("🍎", t("h2.apple"),  "GoldenApple",   "#e04040"),
            ("🐑", t("h2.wool"),   "Wool",          "#f2f2f2"),
        ]
        grp = self._group(t("group.h2_resources"))
        grid = QGridLayout(grp)
        grid.setSpacing(14)
        self._res_h2 = {}
        for i, (icon, label, key, color) in enumerate(RESOURCES_H2):
            card = ResourceCard(icon, label, color)
            self._res_h2[key] = card
            grid.addWidget(card, i // 4, i % 4)
        lay.addWidget(grp)
        lay.addStretch()
        return scroll

    def _tab_arcana_h2(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(10)
        
        hint = QLabel(t("arcana.hint"))
        hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; padding-bottom: 10px;")
        lay.addWidget(hint)

        # Mapping key from GameState.MetaUpgradeState to localized names
        CARDS = [
            ("SorceryRegenUpgrade", "I - The Sorceress"),
            ("ManaOverTime",        "II - The Wayward Swift"),
            ("CardDraw",           "III - The Fates"),
            ("ScreenReroll",       "IV - The Queen"),
            ("StatusVulnerability","V - The Moon"),
            ("ChanneledCast",       "VI - The Night"),
            ("CastCount",          "VII - The Unseen"),
            ("MagicCrit",          "VIII - The Titan"),
            ("BonusDodge",         "IX - The Messenger"),
            ("TradeOff",           "X - The Centaur"),
            ("HealthRegen",        "XI - The Lovers"),
            ("RarityBoost",        "XII - The Furies"),
            ("LowHealthBonus",     "XIII - The Boatman"),
            ("ChanneledBlock",     "XIV - The Strength"),
            ("BonusHealth",        "XV - The Wheel"),
            ("StartingGold",       "XVI - The Guild"),
            ("EpicRarityBoost",    "XVII - The Divinity"),
            ("LastStand",          "XVIII - The Eternity"),
            ("SprintShield",       "XIX - The Guardian"),
            ("BonusRarity",        "XX - The Artificer"),
            ("DoorReroll",         "XXI - The Judgment"),
            ("MaxHealthPerRoom",   "XXII - The World")
        ]
        
        grp = self._group(t("group.arcana"))
        grid = QGridLayout(grp)
        self._arcana_checks = {}
        for i, (key, label) in enumerate(CARDS):
            chk = self._fancy_check(label, "#c0a0f0")
            self._arcana_checks[key] = chk
            grid.addWidget(chk, i // 3, i % 3)
        lay.addWidget(grp)
        lay.addStretch()
        return scroll

    def _tab_weapons_h2(self):
        scroll, inner = self._scroll_tab()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(24, 20, 24, 24)
        lay.setSpacing(20)

        # Each tuple: (display_name, color, world_upgrade_key, weapons_unlocked_key)
        # world_upgrade_key = key in WorldUpgradesAdded (the incantation result)
        # weapons_unlocked_key = key in WeaponsUnlocked (the in-run access flag)
        H2_WEAPONS_DATA = [
            (t("h2.staff"),  GOLD,      "WeaponStaffSwing", "StaffWeapon"),
            (t("h2.blades"), "#e06060",   "WeaponDagger",    "DaggerWeapon"),
            (t("h2.flames"), "#c080f0",   "WeaponTorch",     "TorchWeapon"),
            (t("h2.axe"),    "#60d0e0",   "WeaponAxe",       "AxeWeapon"),
            (t("h2.skull"),  "#8090b0",   "WeaponArcLob",    "LobWeapon"),
        ]
        grp = self._group(t("group.h2_weapons"))
        g_lay = QGridLayout(grp)
        g_lay.setSpacing(12)
        self._w_h2 = {}  # world_upgrade_key -> (chk, wu_key)
        for i, (label, color, wua_key, wu_key) in enumerate(H2_WEAPONS_DATA):
            chk = self._fancy_check(label, color)
            self._w_h2[wua_key] = (chk, wu_key)
            g_lay.addWidget(chk, i // 2, i % 2)
        lay.addWidget(grp)

        # Tools similarly use WorldUpgradesAdded for their "bought" state
        TOOLS = [
            (t("h2.pick"),   "#a0b0c0",   "WeaponPick",      "PickTool"),
            (t("h2.tablet"), "#e0e0a0",   "WeaponTablet",    "TabletTool"),
            (t("h2.shovel"), "#c0c0c0",   "WeaponShovel",    "ShovelTool"),
            (t("h2.rod"),    "#60a0f0",   "WeaponFishing",   "FishingTool"),
        ]
        grp2 = self._group(t("group.tools"))
        gt_lay = QGridLayout(grp2)
        gt_lay.setSpacing(12)
        self._t_h2 = {}  # world_upgrade_key -> (chk, wu_key)
        for i, (label, color, wua_key, wu_key) in enumerate(TOOLS):
            chk = self._fancy_check(label, color)
            self._t_h2[wua_key] = (chk, wu_key)
            gt_lay.addWidget(chk, i // 2, i % 2)
        lay.addWidget(grp2)
        lay.addStretch()
        return scroll

    def _switch_language(self, lang):
        self.btn_en.setChecked(get_language() == "en")
        self.btn_es.setChecked(get_language() == "es")
        if lang == get_language():
            return
        if self.save_file:
            try:
                self._collect()
            except Exception:
                pass
        save_language(lang)
        checked = self.game_toggle.isChecked()
        tabs_enabled = self.tabs.isEnabled()
        new = HadesEditor()
        new.save_file = self.save_file
        new.file_path = self.file_path
        if checked:
            new.game_toggle.setChecked(True)
        if new.save_file and tabs_enabled:
            new._populate()
            new.tabs.setEnabled(True)
            new.btn_save.setEnabled(True)
            new.btn_max.setEnabled(True)
            if new.file_path:
                new._path_lbl.setText(new.file_path)
        new.show()
        self.close()


# ── Entry ─────────────────────────────────────────────────────────────────────
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    QCoreApplication.setApplicationName("HSE")
    QCoreApplication.setOrganizationDomain("HADESEDITOR")
    app.setApplicationDisplayName("HSE")
    
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "Icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    app.setStyle("Fusion")
    load_language()

    welcome = WelcomeDialog()
    if welcome.exec_() == QDialog.Accepted:
        win = HadesEditor()
        win.show()
        # Initialize background safely
        win._on_game_toggled(False)
        sys.exit(app.exec_())
    else:
        sys.exit(0)
