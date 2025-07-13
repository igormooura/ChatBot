import { useState } from "react";
import { TfiClose, TfiAlignLeft } from "react-icons/tfi";
import { Link } from "react-router-dom";

const Header = () => {
  const [nav, setNav] = useState(false);
  const handleClick = () => setNav(!nav);

  return (
    <header className="w-full px-8 py-9 bg-blue-50 flex items-center justify-between relative">
      <div className="text-2xl font-bold text-[#0B2D6B] z-10">NomeLogo</div>
      
      <nav className="hidden md:flex absolute left-1/2 transform -translate-x-1/2 space-x-8">
        <Link to="/" className="text-[#0B2D6B] font-medium">
          Inicio
        </Link>
        <Link to="/login" onClick={() => setNav(false)} className="text-[#0B2D6B] font-medium">
          Consultas
        </Link>
        <Link to="/chatbot" className="text-[#0B2D6B] font-medium">
          Chatbot
        </Link>
        <Link to="/admin" className="text-[#0B2D6B] font-medium">
          Admin
        </Link>
      </nav>

      {/* Mobile */}
      <div className="md:hidden text-[#0B2D6B] z-10" onClick={handleClick}>
        {nav ? <TfiClose size={24} /> : <TfiAlignLeft size={24} />}
      </div>

      {/* Mobile */}
      <div
        className={`${
          nav ? "left-0" : "-left-full"
        } fixed top-0 w-[60%] h-full bg-blue-50 shadow-md border-r border-gray-200 transition-all duration-500 md:hidden`}
      >
        <ul className="p-4 space-y-4 mt-16">
          <li>
            <Link to="/" onClick={() => setNav(false)} className="text-[#0B2D6B] font-medium">
              Inicio
            </Link>
          </li>
          <li>
            <Link to="/user" onClick={() => setNav(false)} className="text-[#0B2D6B] font-medium">
              Consultas
            </Link>
          </li>
          <li>
            <Link to="/chatbot" onClick={() => setNav(false)} className="text-[#0B2D6B] font-medium">
              Chatbot
            </Link>
          </li>
          <li>
            <Link to="/admin" onClick={() => setNav(false)} className="text-[#0B2D6B] font-medium">
              Admin
            </Link>
          </li>
        </ul>
      </div>
    </header>
  );
};

export default Header;
