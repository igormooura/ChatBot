const Footer = () => {
  const nomes = ['Arthur Andrade', 'Igor Moura', 'Hugo Souza', 'Henrico Costa', 'Erick Saraiva'];

  return (
    <footer className="w-full bg-blue-200 py-10 text-gray-800">
      <div className="max-w-5xl mx-auto px-6">
        <h2 className="text-3xl font-bold mb-10 text-center tracking-tight text-gray-900">
          Members
        </h2>
        <ul className="flex flex-wrap justify-center gap-6">
          {nomes.map((nome, index) => (
            <li
              key={index}
              className="text-gray-700 text-lg hover:text-gray-900 transition duration-300"
            >
              {nome}
            </li>
          ))}
        </ul>
        <div className="mt-10 text-center text-gray-100 text-sm">
          <p>Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
