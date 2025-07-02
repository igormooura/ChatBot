import { useState } from "react";
import Footer from "../components/Footer/Footer";
import Header from "../components/Header/Header";
import ConsultasTable from "../components/Tables/ConsultasTable";
import type { Consulta } from "../components/Tables/ConsultasTable";

const consultasIniciais: Consulta[] = [
  { id: 1, medico: "Dr. João Silva", especialidade: "Cardiologia", paciente: "Igor Moura", data: "2025-07-05", horario: "10:00" },
  { id: 2, medico: "Dra. Maria Souza", especialidade: "Dermatologia", paciente: "Ana Paula", data: "2025-07-06", horario: "11:30" },
  { id: 3, medico: "Dr. Carlos Pereira", especialidade: "Ortopedia", paciente: "Lucas Silva", data: "2025-07-10", horario: "14:00" },
  { id: 4, medico: "Dra. Fernanda Lima", especialidade: "Neurologia", paciente: "Mariana Santos", data: "2025-07-15", horario: "09:00" },
];

export const AdminPage = () => {
  const [consultas, setConsultas] = useState<Consulta[]>(consultasIniciais);

  const handleDelete = (id: number) => {
    if (window.confirm("Tem certeza que deseja deletar esta consulta?")) {
      setConsultas((prev) => prev.filter((c) => c.id !== id));
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow bg-gradient-to-r from-blue-50 via-white to-blue-50 p-8">
        <h1 className="text-4xl font-extrabold mb-10 text-center text-blue-900">Todas as Consultas Marcadas</h1>
        {consultas.length === 0 ? (
          <p className="text-center text-gray-600 text-lg">Nenhuma consulta cadastrada no momento.</p>
        ) : (
          <ConsultasTable consultas={consultas} onDelete={handleDelete} />
        )}
      </main>
      <Footer />
    </div>
  );
};
