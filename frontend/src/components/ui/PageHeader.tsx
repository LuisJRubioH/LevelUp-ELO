/**
 * components/ui/PageHeader.tsx
 * ============================
 * Encabezado de página del estudiante con identidad Oulad: eyebrow en
 * pixel-font + título Poppins + subtítulo. Estilos en StudentContent.css
 * (.sp-head / .sp-eyebrow / .sp-title / .sp-subtitle).
 */

export function PageHeader({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="sp-head">
      <span className="sp-eyebrow">{eyebrow}</span>
      <h2 className="sp-title">{title}</h2>
      {subtitle && <p className="sp-subtitle">{subtitle}</p>}
    </div>
  );
}
