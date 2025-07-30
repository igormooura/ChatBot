import React from "react";
import { motion } from "framer-motion";
import { easeOut } from "framer-motion";

export type Consulta = {
  id: number;
  medico: string;
  especialidade: string;
  cpf: string;
  data: string;
  horario: string;
};

interface ConsultasTableProps {
  consultas: Consulta[];
  onDelete?: (id: number) => void;
}


const animationVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0, 
    transition: { duration: 0.5, ease: easeOut }
  },
};


const ConsultasTable: React.FC<ConsultasTableProps> = ({ consultas, onDelete }) => {
  return (
    <motion.div
      className="overflow-x-auto max-w-6xl mx-auto shadow-lg rounded-lg bg-white"
      initial="hidden"
      animate="visible"
      variants={animationVariants}
    >
      <table className="w-full text-left rounded-lg">
        <thead className="bg-blue-100 border-b border-blue-300">
          <tr>
            <th className="px-6 py-4 font-semibold text-blue-800">Médico / Especialidade</th>
            <th className="px-6 py-4 font-semibold text-blue-800">Paciente</th>
            <th className="px-6 py-4 font-semibold text-blue-800">Data</th>
            <th className="px-6 py-4 font-semibold text-blue-800">Horário</th>
            {onDelete && <th className="px-6 py-4 font-semibold text-blue-800">Ações</th>}
          </tr>
        </thead>
        <tbody>
          {consultas.map(({ id, medico, especialidade, cpf, data, horario }) => (
            <tr
              key={id}
              className={`border-b border-gray-200 hover:bg-blue-50 transition-colors ${onDelete ? '' : 'cursor-default'}`}
            >
              <td className="px-6 py-4">
                <p className="font-semibold text-blue-900">{medico}</p>
                <p className="text-sm text-blue-600 italic">{especialidade}</p>
              </td>
              <td className="px-6 py-4 text-gray-700">{cpf}</td>
              <td className="px-6 py-4 text-gray-700">{new Date(data).toLocaleDateString("pt-BR")}</td>
              <td className="px-6 py-4 text-gray-700">{horario}</td>
              {onDelete && (
                <td className="px-6 py-4">
                  <button
                    onClick={() => onDelete(id)}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition"
                  >
                    Deletar
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
};

export default ConsultasTable;
