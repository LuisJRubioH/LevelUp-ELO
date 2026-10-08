import type { ReactNode } from "react";
import "./HubDestinationArt.css";

const DESTINATION_IMAGES: Record<string, string> = {
  "E01": "e01-granero.png",
  "E02": "e02-casa-cuentas.png",
  "E03": "e03-taller-mosaicos.png",
  "E04": "e04-comedor.png",
  "E05": "e05-invernadero.png",
  "E06": "e06-cantera.png",
  "M01": "m01-prensa-intercambio.png",
  "M02": "m02-horno-fundicion.png",
  "M03": "m03-cinta-repartidora.png",
  "M04": "m04-calibre-cero.png",
  "M05": "m05-prensa-contrapesos.png",
  "C01": "c01-corinto.png",
  "C02": "c02-rodas.png",
  "C03": "c03-delos.png",
  "C04": "c04-mileto.png",
  "C05": "c05-atenas.png",
  "C06": "c06-esparta.png",
  "A1": "a1-casa-vida.png",
  "A2": "a2-obra-piramide.png",
  "A3": "a3-campos-crecida.png",
  "A4": "a4-taller-canon.png",
  "S1": "s1-sala-troqueles.png",
  "S2": "s2-almacen-caravana.png"
};

export function HubDestinationArt({ id, children }: { id: string; children: ReactNode }) {
  const filename = DESTINATION_IMAGES[id];
  if (!filename) return <>{children}</>;
  return (
    <>
      <img className="hub-destination-image" src={`/leccion/hub-destinos/${filename}`} alt="" aria-hidden="true" width={1536} height={1024} loading="lazy" decoding="async" />
      <div className="hub-destination-caption">{children}</div>
    </>
  );
}
