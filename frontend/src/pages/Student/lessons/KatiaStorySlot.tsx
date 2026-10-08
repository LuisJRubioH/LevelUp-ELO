import { MathFormula, MathText } from "../../../components/Math/MathContent";

type FormulaCaption = { math: string; caption?: string };

type Props = {
  eyebrow: string;
  title?: string;
  body: string;
  imageSrc?: string;
  imageAlt?: string;
  formula?: string;
  formulas?: FormulaCaption[];
  question?: string;
  reverse?: boolean;
};

export function KatiaStorySlot({
  eyebrow,
  title,
  body,
  imageSrc,
  imageAlt = "",
  formula,
  formulas,
  question,
  reverse = false,
}: Props) {
  return (
    <section className={`katia-story-slot ${reverse ? "reverse" : ""}`}>
      <div className="katia-story-media">
        {imageSrc ? (
          <img src={imageSrc} alt={imageAlt} loading="lazy" />
        ) : (
          <div className="katia-story-placeholder" role="img" aria-label="Imagen de KatIA aquí">
            <span>Imagen de KatIA aquí</span>
          </div>
        )}
      </div>
      <div className="katia-story-copy">
        <span>{eyebrow}</span>
        {title && <h2><MathText text={title} /></h2>}
        <p><MathText text={body} /></p>
        {formulas?.map((item, index) => (
          <div className="katia-story-formula-line" key={index}>
            <MathFormula math={item.math} />
            {item.caption && <small><MathText text={item.caption} /></small>}
          </div>
        ))}
        {formula && (
          <div className="katia-story-formula">
            <MathFormula math={formula} />
          </div>
        )}
        {question && (
          <blockquote className="katia-story-question">
            <MathText text={question} />
          </blockquote>
        )}
      </div>
    </section>
  );
}
