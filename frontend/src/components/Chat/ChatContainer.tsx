import type { ReactNode } from "react";

interface ChatContainerProps {
  children: ReactNode;
}

const ChatContainer = ({ children }: ChatContainerProps) => {
  return (
    <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 to-blue-200">
      <div
        className="
          w-full max-w-4xl h-[80vh] overflow-y-auto px-6 py-8
          bg-white/20 backdrop-blur-lg
          rounded-2xl shadow-xl border border-white/30
          ring-1 ring-white/40
          "
      >
        {children}
      </div>
    </div>
  );
};

export default ChatContainer;
