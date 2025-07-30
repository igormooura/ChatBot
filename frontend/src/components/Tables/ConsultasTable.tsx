import React from 'react';
import { motion } from 'framer-motion';
import { easeOut } from 'framer-motion';

export interface Consulta {
  id: number;
  tipo: 'consulta';
  data: string;
  status: string;
  medico: string;
  especialidade?: string;
  horario?: string;
}

export interface Exam {
  id: number;
  tipo: 'exame';
  data: string;
  status: string;
  exame: string;
  horario?: string;
}

interface ConsultasTableProps {
  consultas: Consulta[];
  exames: Exam[];
  onDeleteConsulta?: (id: number) => void;
  onDeleteExame?: (id: number) => void;
  isAdmin?: boolean;
}

const animationVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: easeOut },
  },
};

const ConsultasTable: React.FC<ConsultasTableProps> = ({
  consultas,
  exames,
  onDeleteConsulta,
  onDeleteExame,
  isAdmin,
}) => {
  const combinedItems = [
    ...consultas.map((c) => ({
      ...c,
      especialidade: c.especialidade || 'Consulta Médica',
      horario: new Date(c.data).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    })),
    ...exames.map((e) => ({
      ...e,
      medico: e.exame,
      especialidade: 'Exame',
      horario: new Date(e.data).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    })),
  ];

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
            <th className="px-6 py-4 font-semibold text-blue-800">Médico / Exame</th>
            <th className="px-6 py-4 font-semibold text-blue-800">Tipo</th>
            <th className="px-6 py-4 font-semibold text-blue-800">Data</th>
            <th className="px-6 py-4 font-semibold text-blue-800">Horário</th>
            <th className="px-6 py-4 font-semibold text-blue-800">Status</th>
            {isAdmin && <th className="px-6 py-4 font-semibold text-blue-800">Ações</th>}
          </tr>
        </thead>
        <tbody>
          {combinedItems.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-6 py-4 text-center text-gray-600">
                Nenhuma consulta ou exame encontrado.
              </td>
            </tr>
          ) : (
            combinedItems.map((item) => (
              <tr
                key={`${item.tipo}-${item.id}`}
                className="border-b border-gray-200 hover:bg-blue-50 transition-colors"
              >
                <td className="px-6 py-4">
                  <p className="font-semibold text-blue-900">
                    {item.tipo === 'consulta' ? item.medico : item.exame}
                  </p>
                  <p className="text-sm text-blue-600 italic">{item.especialidade}</p>
                </td>
                <td className="px-6 py-4 text-gray-700">{item.tipo}</td>
                <td className="px-6 py-4 text-gray-700">
                  {new Date(item.data).toLocaleDateString('pt-BR')}
                </td>
                <td className="px-6 py-4 text-gray-700">{item.horario}</td>
                <td className="px-6 py-4 text-gray-700">{item.status}</td>
                {isAdmin && (
                  <td className="px-6 py-4">
                    <button
                      onClick={() =>
                        item.tipo === 'consulta'
                          ? onDeleteConsulta?.(item.id)
                          : onDeleteExame?.(item.id)
                      }
                      className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition"
                    >
                      Deletar
                    </button>
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </motion.div>
  );
};

export default ConsultasTable;
