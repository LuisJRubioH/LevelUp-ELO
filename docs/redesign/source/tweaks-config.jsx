/* tweaks-config.jsx — LevelUp-ELO landing tweaks (palette + theme) */
const { useTweaks, TweaksPanel, TweakSection, TweakColor, TweakToggle, TweakRadio } = window;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#8b5cf6",
  "brand": "#2dd4bf",
  "light": false,
  "glow": true,
  "pixel": "subtle"
}/*EDITMODE-END*/;

function lighten(hex, amt) {
  return "color-mix(in srgb, " + hex + " " + (100 - amt) + "%, white)";
}

function LandingTweaks() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  React.useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty("--accent", t.accent);
    root.style.setProperty("--accent-soft", lighten(t.accent, 35));
    root.style.setProperty("--accent-2", t.brand);
    root.style.setProperty("--accent-2-soft", lighten(t.brand, 40));
    root.style.setProperty("--glow-a", t.glow ? "color-mix(in srgb, " + t.accent + " 42%, transparent)" : "transparent");
    root.style.setProperty("--glow-b", t.glow ? "color-mix(in srgb, " + t.brand + " 30%, transparent)" : "transparent");
    root.classList.toggle("light", !!t.light);
    document.body.setAttribute("data-pixel", t.pixel);
  }, [t]);

  return (
    <TweaksPanel>
      <TweakSection label="Paleta" />
      <TweakColor
        label="Acento principal"
        value={t.accent}
        options={["#8b5cf6", "#6d5efc", "#d946ef", "#3b82f6"]}
        onChange={(v) => setTweak("accent", v)}
      />
      <TweakColor
        label="Color de marca"
        value={t.brand}
        options={["#2dd4bf", "#34d399", "#22d3ee", "#ffd700"]}
        onChange={(v) => setTweak("brand", v)}
      />
      <TweakSection label="Tema" />
      <TweakToggle label="Modo claro" value={t.light} onChange={(v) => setTweak("light", v)} />
      <TweakToggle label="Resplandor de fondo" value={t.glow} onChange={(v) => setTweak("glow", v)} />
      <TweakSection label="Detalle pixel-art" />
      <TweakRadio
        label="Intensidad"
        value={t.pixel}
        options={["subtle", "off"]}
        onChange={(v) => setTweak("pixel", v)}
      />
    </TweaksPanel>
  );
}

ReactDOM.createRoot(document.getElementById("tweaks-root")).render(<LandingTweaks />);
