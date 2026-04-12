"""
src/interface/streamlit/components/timers.py
=============================================
Componente de temporizador en tiempo real vía JavaScript puro.
El timer corre segundo a segundo sin necesidad de rerun de Streamlit.
"""
from streamlit.components.v1 import html as st_html

_TIMER_ID_COUNTER = [0]  # mutable counter para IDs únicos de timers


def _render_live_timer(start_epoch: float, label: str = "",
                       font_size: str = "1.1rem", height: int = 40,
                       color: str = "#FFD700", bold: bool = True,
                       align: str = "right"):
    """Renderiza un temporizador en tiempo real usando JavaScript puro.

    El timer corre segundo a segundo sin necesidad de rerun de Streamlit.
    """
    _TIMER_ID_COUNTER[0] += 1
    _tid = f"tmr_{_TIMER_ID_COUNTER[0]}"
    _w = "font-weight:700;" if bold else ""
    _html = f"""
    <style>
      body {{ margin:0; padding:0; background:transparent; overflow:hidden; }}
    </style>
    <div style="text-align:{align};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
      <span style="color:{color};font-size:{font_size};{_w}letter-spacing:0.5px;">
        {label}<span id="{_tid}">0:00</span>
      </span>
    </div>
    <script>
    (function() {{
      var start = {start_epoch} * 1000;
      var el = document.getElementById('{_tid}');
      function tick() {{
        var diff = Math.floor((Date.now() - start) / 1000);
        if (diff < 0) diff = 0;
        var h = Math.floor(diff / 3600);
        var m = Math.floor((diff % 3600) / 60);
        var s = diff % 60;
        if (h > 0) {{
          el.textContent = h + 'h ' + String(m).padStart(2,'0') + 'm ' + String(s).padStart(2,'0') + 's';
        }} else if (m > 0) {{
          el.textContent = m + ':' + String(s).padStart(2,'0');
        }} else {{
          el.textContent = s + 's';
        }}
      }}
      tick();
      setInterval(tick, 1000);
    }})();
    </script>
    """
    st_html(_html, height=height)
