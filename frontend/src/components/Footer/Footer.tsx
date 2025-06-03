const Footer = () => {
  const nomes = ['Arthur Andrade', 'Igor Moura', 'Hugo Souza', 'Henrico Costa', 'Erick Saraiva'];

  return (
    <div className="w-full bg-[#0B2D6B] mx-auto py-10 text-center text-white">
      <h2 className="text-lg font-semibold mb-4">Membros do WHATSAPP</h2>
      <ul className="space-y-2">
        {nomes.map((nome, index) => (
          <li 
            key={index} 
            className="text-gray-300 hover:text-white transition"
          >
            {nome}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Footer;