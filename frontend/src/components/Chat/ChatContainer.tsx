import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface ChatContainerProps {
  children: ReactNode;
}

export default function ChatContainer({ children }: ChatContainerProps) {
  return (
    <div className="w-full h-screen flex items-center justify-center bg-gradient-to-br from-blue-100 to-blue-200">
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: "spring", stiffness: 120, damping: 20 }}
        className="w-full max-w-4xl h-[80vh] overflow-y-auto px-6 py-8 bg-white/20 backdrop-blur-lg rounded-2xl shadow-xl border border-white/30 ring-1 ring-white/40"
      >
        {children}
      </motion.div>
    </div>
  );
}