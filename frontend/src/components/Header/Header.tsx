import { useState } from "react";
import { TfiClose, TfiAlignLeft } from "react-icons/tfi";

const Header = () => {
  const [nav, setNav] = useState(false);
  const handleClick = () => setNav(!nav);

  return (
    <header className="w-full  px-8 py-9 bg-blue-50 flex items-center justify-between relative">
      <div className="text-2xl font-bold text-[#0B2D6B] z-10">
        NomeLogo
      </div>

      <nav className="hidden md:flex absolute left-1/2 transform -translate-x-1/2 space-x-8">
        <span className="text-[#0B2D6B] font-medium cursor-pointer">Inicio</span>
        <span className="text-[#0B2D6B] font-medium cursor-pointer">Consultas</span>
        <span className="text-[#0B2D6B] font-medium cursor-pointer">Chatbot</span>
        <span className="text-[#0B2D6B] font-medium cursor-pointer">Admin</span>
      </nav>

      <div className="md:hidden text-[#0B2D6B] z-10" onClick={handleClick}>
        {nav ? <TfiClose size={24} /> : <TfiAlignLeft size={24} />}
      </div>

      <div
        className={`${
          nav ? "left-0" : "-left-full"
        } fixed top-0 w-[60%] h-full bg-white shadow-md border-r border-gray-200 transition-all duration-500 md:hidden`}
      >
        <ul className="p-4 space-y-4 mt-16">
          <li className="text-[#0B2D6B] font-medium">Inicio</li>
          <li className="text-[#0B2D6B] font-medium">Consultas</li>
          <li className="text-[#0B2D6B] font-medium">Chatbot</li>
          <li className="text-[#0B2D6B] font-medium">Admin</li>
        </ul>
      </div>
    </header>
  );
};

export default Header;
