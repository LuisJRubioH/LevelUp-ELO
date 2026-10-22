import { type CSSProperties } from "react";
import { MathFormula } from "../../../components/Math/MathContent";

type SetStep = "naturals" | "integers" | "rationals" | "irrationals" | "reals";

type Props = {
  imageSrc: string;
  activeStep: SetStep;
  ariaLabel: string;
};

const SET_STEPS: Array<{ key: SetStep; label: string; math: string }> = [
  { key: "naturals", label: "Naturales", math: String.raw`\mathbb{N}` },
  { key: "integers", label: "Enteros", math: String.raw`\mathbb{Z}` },
  { key: "rationals", label: "Racionales", math: String.raw`\mathbb{Q}` },
  { key: "irrationals", label: "Irracionales", math: String.raw`\mathbb{R}\setminus\mathbb{Q}` },
  { key: "reals", label: "Reales", math: String.raw`\mathbb{R}` },
];

const SET_HOTSPOT_FRAMES = [
  { left: "21%", top: "71%", width: "22.8%", height: "8.2%" },
  { left: "24.5%", top: "59.7%", width: "22.4%", height: "7.8%" },
  { left: "28%", top: "48.4%", width: "22%", height: "7.8%" },
  { left: "31.5%", top: "37.1%", width: "21.6%", height: "7.8%" },
  { left: "35%", top: "25.8%", width: "21.2%", height: "7.8%" },
];

export function SetNodeScene({ imageSrc, activeStep, ariaLabel }: Props) {
  return (
    <figure className="set-node-scene" aria-label={ariaLabel}>
      <img src={imageSrc} alt="" aria-hidden="true" loading="lazy" />
      <ol className="set-node-static-buttons" aria-hidden="true">
        {SET_STEPS.map((step, index) => (
          <li
            key={step.key}
            style={
              {
                "--hotspot-left": SET_HOTSPOT_FRAMES[index].left,
                "--hotspot-top": SET_HOTSPOT_FRAMES[index].top,
                "--hotspot-width": SET_HOTSPOT_FRAMES[index].width,
                "--hotspot-height": SET_HOTSPOT_FRAMES[index].height,
              } as CSSProperties
            }
          >
            <span className={`set-node-static-step ${activeStep === step.key ? "active" : ""}`}>
              <small>0{index + 1}</small>
              <b>{step.label}</b>
              <em>
                <MathFormula math={step.math} />
              </em>
            </span>
          </li>
        ))}
      </ol>
    </figure>
  );
}
