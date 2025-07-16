import type { ReactNode } from "react";

interface BackgroundProps {
  children: ReactNode;
}

const Background = ({ children }: BackgroundProps) => {
  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-50  to-blue-50">
      {children}
    </div>
  );
};

export default Background;
