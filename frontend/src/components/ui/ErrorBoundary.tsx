import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-[#0A0A0F] p-8 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-500/10 text-3xl">
          ⚠
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-[#F1F5F9]">
            Algo salió mal
          </h1>
          <p className="max-w-sm text-sm text-[#94A3B8]">
            Ocurrió un error inesperado. Puedes intentar recargar la página.
          </p>
          {this.state.error && (
            <p className="mt-2 font-mono text-xs text-red-400/70">
              {this.state.error.message}
            </p>
          )}
        </div>
        <button
          onClick={() => window.location.reload()}
          className="rounded-lg bg-[#6C63FF] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[#5a52d5] active:scale-95"
        >
          Recargar página
        </button>
      </div>
    );
  }
}
