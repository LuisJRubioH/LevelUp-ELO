import type { ReactNode } from "react";
import "./HubDestinationArt.css";

const DESTINATION_IMAGES: Record<string, string> = {
  "E01": "/leccion/hub-destinos/e01-granero.webp",
  "E02": "/leccion/hub-destinos/e02-casa-cuentas.webp",
  "E03": "/leccion/hub-destinos/e03-taller-mosaicos.webp",
  "E04": "/leccion/hub-destinos/e04-comedor.webp",
  "E05": "/leccion/hub-destinos/e05-invernadero.webp",
  "E06": "/leccion/hub-destinos/e06-cantera.webp",
  "M01": "/leccion/hub-destinos/m01-prensa-intercambio.webp",
  "M02": "/leccion/hub-destinos/m02-horno-fundicion.webp",
  "M03": "/leccion/hub-destinos/m03-cinta-repartidora.webp",
  "M04": "/leccion/hub-destinos/m04-calibre-cero.webp",
  "M05": "/leccion/hub-destinos/m05-prensa-contrapesos.webp",
  "C01": "/leccion/hub-destinos/c01-corinto.webp",
  "C02": "/leccion/hub-destinos/c02-rodas.webp",
  "C03": "/leccion/hub-destinos/c03-delos.webp",
  "C04": "/leccion/hub-destinos/c04-mileto.webp",
  "C05": "/leccion/hub-destinos/c05-atenas.webp",
  "C06": "/leccion/hub-destinos/c06-esparta.webp",
  "A1": "/leccion/hub-destinos/a1-casa-vida.webp",
  "A2": "/leccion/hub-destinos/a2-obra-piramide.webp",
  "A3": "/leccion/hub-destinos/a3-campos-crecida.webp",
  "A4": "/leccion/hub-destinos/a4-taller-canon.webp",
  "S1": "/leccion/hub-destinos/s1-sala-troqueles.webp",
  "S2": "/leccion/hub-destinos/s2-almacen-caravana.webp"
};

export function HubDestinationArt({ id, children }: { id: string; children: ReactNode }) {
  const src = DESTINATION_IMAGES[id];
  if (!src) return <>{children}</>;
  return (
    <>
      <img className="hub-destination-image" src={src} alt="" aria-hidden="true" width={1536} height={1024} loading="lazy" decoding="async" />
      <div className="hub-destination-caption">{children}</div>
    </>
  );
}
