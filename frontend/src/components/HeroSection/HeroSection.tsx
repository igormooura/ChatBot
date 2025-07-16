import { motion } from "framer-motion";

const HeroSection = () => {
  return (
    <motion.section
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="flex flex-col items-center justify-center text-center bg-blue-50 w-full min-h-screen"
    >
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="text-4xl sm:text-5xl font-bold text-blue-900 mb-4"
      >
        ESPECIALISTAS <br /> EM SAÚDE MÉDICA
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.6 }}
        className="text-lg text-gray-700 mb-8 max-w-xl"
      >
        Atendimento humanizado com tecnologia de ponta para sua saúde.
      </motion.p>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="bg-blue-800 text-white text-lg font-semibold px-8 py-3 rounded hover:bg-blue-900 transition"
      >
        Agendar Consulta
      </motion.button>
    </motion.section>
  );
};

export default HeroSection;
