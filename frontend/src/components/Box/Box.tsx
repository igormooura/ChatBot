import type { ReactNode } from "react";
import { motion } from "framer-motion";

interface BoxProps {
  children: ReactNode;
}

const Box = ({ children }: BoxProps) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, ease: "easeOut" }}
    className="
      w-full max-w-[90%] sm:max-w-[420px] md:max-w-[480px] lg:max-w-[560px] xl:max-w-[600px]
      min-h-[350px] sm:min-h-[400px] lg:min-h-[500px]
      bg-white rounded-2xl shadow-lg space-y-4
      flex flex-col items-center justify-center
    "
  >
    {children}
  </motion.div>
);

export default Box;
