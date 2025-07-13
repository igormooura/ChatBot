const Footer = () => {
  const nomes = ['Arthur Andrade', 'Igor Moura', 'Hugo Souza', 'Henrico Costa', 'Erick Saraiva'];

  return (
    <footer className="w-full bg-blue-200 py-12 text-gray-800 h-full">
      <div className=" mx-auto px-6 flex flex-col items-center">
        <h2 className="text-3xl font-semibold text-gray-900 mb-6">Members</h2>

        <ul className="flex flex-wrap justify-center gap-x-8 gap-y-4 mb-8">
          {nomes.map((nome, index) => (
            <li
              key={index}
              className="text-gray-700 text-base hover:text-gray-900 transition duration-200"
            >
              {nome}
            </li>
          ))}
        </ul>

        <p className="text-sm text-gray-600">Todos os direitos reservados.</p>
      </div>
    </footer>
  );
};

export default Footer;
