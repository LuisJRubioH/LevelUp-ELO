declare module "react-katex" {
  import type { FC } from "react";
  interface MathProps {
    math: string;
    errorColor?: string;
    renderError?: (error: Error) => React.ReactNode;
  }
  const InlineMath: FC<MathProps>;
  const BlockMath: FC<MathProps>;
  export default InlineMath;
  export { InlineMath, BlockMath };
}
