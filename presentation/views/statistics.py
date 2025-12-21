# presentation/views/statistics.py
from presentation.keyboards.main_menu import get_single_back_keyboard
from data.icons import ICONS
from data.statistics_translations import STATS_TRANSLATIONS


def render_stats(statistics: list, fid: int):
    if not statistics or len(statistics) < 2:
        return f"{ICONS['warning']} Статистика відсутня", get_single_back_keyboard(f"detail:{fid}")

    stats_home = statistics[0]
    stats_away = statistics[1]

    if not stats_home or not stats_away:
        return f"{ICONS['warning']} Статистика поки недоступна", get_single_back_keyboard(f"detail:{fid}")

    team_home = stats_home.get("team", {}).get("name", "Команда 1")
    team_away = stats_away.get("team", {}).get("name", "Команда 2")

    def safe_value(val):
        if val is None:
            return "0"
        return str(val)

    # Фіксовані ширини — ключ до стабільності
    left_width = 8
    center_width = 28
    right_width = 8

    total_width = left_width + center_width + right_width + 6

    lines = []

    # Назви команд по центру (два рядки)
    lines.append(team_home.center(total_width))
    lines.append(team_away.center(total_width))

    # Порожній рядок замість роздільника — візуально відокремлює, але не ламає
    lines.append("")

    # Статистика
    for h, a in zip(stats_home.get("statistics", []), stats_away.get("statistics", [])):
        en_label = h.get("type", "—")
        ua_label = STATS_TRANSLATIONS.get(en_label, en_label)

        val_h = safe_value(h.get("value"))
        val_a = safe_value(a.get("value"))

        padded_h = val_h.rjust(left_width)
        padded_label = ua_label.center(center_width)
        padded_a = val_a.ljust(right_width)

        lines.append(f"{padded_h}  {padded_label}  {padded_a}")

    table_text = "<pre>" + "\n".join(lines) + "</pre>"

    header = f"<b>Статистика матчу</b>\n\n"
    full_text = header + table_text

    return full_text, get_single_back_keyboard(f"detail:{fid}")