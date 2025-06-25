const HeroSection = () => {
  return (
    <section className="flex flex-col items-center justify-center text-center bg-blue-50 py-20 px-4">
      <h1 className="text-4xl sm:text-5xl font-bold text-blue-900 mb-4">
        ESPECIALISTAS <br /> EM SAÚDE MÉDICA
      </h1>
      <p className="text-lg text-gray-700 mb-8 max-w-xl">
        Atendimento humanizado com tecnologia de ponta para sua saúde.
      </p>
      <button className="bg-blue-800 text-white text-lg font-semibold px-8 py-3 rounded hover:bg-blue-900 transition">
        Agendar Consulta
      </button>
    </section>
  );
};

export default HeroSection;
