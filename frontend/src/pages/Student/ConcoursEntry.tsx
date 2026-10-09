/**
 * pages/Student/ConcoursEntry.tsx
 * ================================
 * Selector de bloque temático para cursos de concursos (DIAN / SENA).
 * Sin diagnóstico, sin gamificación. Identidad Oulad sobria (.lue-dx).
 */

import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { studentApi } from "../../api/student";
import { usePracticeStore } from "../../stores/practiceStore";
import "./CourseEntry.css";
import "./ConcoursEntry.css";

export function ConcoursEntry({
  courseId,
  courseName,
}: {
  courseId: string;
  courseName: string;
}) {
  const navigate = useNavigate();
  const startSession = usePracticeStore((s) => s.startSession);

  const { data: blocks, isLoading, isError } = useQuery({
    queryKey: ["course-blocks", courseId],
    queryFn: () => studentApi.courseBlocks(courseId),
    staleTime: 5 * 60 * 1000,
  });

  const handleBlock = (block: string) => {
    startSession(courseId, block);
    navigate("/student");
  };

  const handleAll = () => {
    startSession(courseId);
    navigate("/student");
  };

  const totalItems = blocks?.reduce((s, b) => s + b.item_count, 0) ?? 0;

  return (
    <div className="lue-dx">
      <div className="dx-top">
        <button className="dx-close" onClick={() => navigate("/student/courses")} aria-label="Volver">
          ←
        </button>
        <div className="dx-grow" />
      </div>

      <div className="dx-body" style={{ alignItems: "flex-start", paddingTop: 24 }}>
        <div className="dx-center">
          <span className="dx-eyebrow">Preparación para concurso</span>
          <h1 className="cx-title">{courseName}</h1>

          {isLoading ? (
            <p className="cx-loading">Cargando bloques temáticos…</p>
          ) : isError || !blocks ? (
            <p className="cx-error">No se pudieron cargar los bloques.</p>
          ) : (
            <>
              <p className="cx-sub">
                <b>{totalItems}</b> preguntas · <b>{blocks.length}</b> bloques temáticos. Elige uno para
                practicar enfocado o repasa todo el temario.
              </p>

              <div className="cx-list">
                {blocks.map((b) => (
                  <button key={b.block} className="cx-block" onClick={() => handleBlock(b.block)}>
                    <span className="cx-block-main">
                      <span className="cx-block-name">{b.block}</span>
                    </span>
                    <span className="cx-block-count">
                      <span className="cx-n">{b.item_count}</span> preg
                    </span>
                  </button>
                ))}
              </div>

              <button className="dx-link cx-all" onClick={handleAll}>
                Practicar todo el temario →
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
