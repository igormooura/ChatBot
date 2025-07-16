import { useState } from "react";
import { TfiClose, TfiAlignLeft } from "react-icons/tfi";
import { Link } from "react-router-dom";

const Header = () => {
  const [navOpen, setNavOpen] = useState(false);

  const toggleNav = () => setNavOpen((prev) => !prev);
  const closeNav = () => setNavOpen(false);

  return (
    <>
      <header className="fixed top-0 left-0 w-full bg-white/80 backdrop-blur-md shadow-md z-30">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <div className="text-2xl font-bold text-blue-900 cursor-pointer">
            <Link to="/" onClick={closeNav}>
              NomeLogo
            </Link>
          </div>

          <nav className="hidden md:flex space-x-8 text-blue-900 font-medium">
            <Link to="/" onClick={closeNav} className="hover:text-blue-700 hover:underline">
              Inicio
            </Link>
            <Link to="/login" onClick={closeNav} className="hover:text-blue-700 hover:underline">
              Consultas
            </Link>
            <Link to="/chatbot" onClick={closeNav} className="hover:text-blue-700 hover:underline">
              Chatbot
            </Link>
            <Link to="/login" onClick={closeNav} className="hover:text-blue-700 hover:underline">
              Admin
            </Link>
          </nav>

          <button
            onClick={toggleNav}
            className="md:hidden text-blue-900 focus:outline-none"
            aria-label="Toggle menu"
          >
            {navOpen ? <TfiClose size={28} /> : <TfiAlignLeft size={28} />}
          </button>
        </div>
      </header>

      {/* Overlay e Menu Mobile */}
      {navOpen && (
        <div
          onClick={closeNav}
          className="fixed inset-0 bg-black/50 z-40 transition-opacity duration-300 md:hidden"
          style={{ opacity: navOpen ? 1 : 0 }}
        />
      )}

      <div
        className={`fixed top-0 left-0 w-[45%] h-full bg-white shadow-xl z-50 transition-all duration-300 ease-in-out transform ${
          navOpen ? "translate-x-0" : "-translate-x-full"
        } md:hidden`}
      >

        
        <ul className="p-4 space-y-6 mt-20">
        <div className="text-2xl font-bold text-blue-900 cursor-pointer">
            <Link to="/" onClick={closeNav}>
              NomeLogo
            </Link>
          </div>
          <li>
            <Link to="/" onClick={closeNav} className="text-blue-900 font-medium text-lg">
              Inicio
            </Link>
          </li>
          <li>
            <Link to="/login" onClick={closeNav} className="text-blue-900 font-medium text-lg">
              Consultas
            </Link>
          </li>
          <li>
            <Link to="/chatbot" onClick={closeNav} className="text-blue-900 font-medium text-lg">
              Chatbot
            </Link>
          </li>
          <li>
            <Link to="/login" onClick={closeNav} className="text-blue-900 font-medium text-lg">
              Admin
            </Link>
          </li>
        </ul>
      </div>
    </>
  );
};

export default Header;