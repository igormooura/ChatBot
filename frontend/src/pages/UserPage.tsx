import Background from "../components/Background/Background";
import Footer from "../components/Footer/Footer";
import Header from "../components/Header/Header";
import ConsultasTable from "../components/Tables/ConsultasTable";
import type { Consulta } from "../components/Tables/ConsultasTable";

const consultasSimuladas: Consulta[] = [
  {
    id: 1,
    medico: "Dr. João Silva",
    especialidade: "Cardiologia",
    paciente: "Igor Moura",
    data: "2025-07-05",
    horario: "10:00",
  },
  {
    id: 2,
    medico: "Dra. Maria Souza",
    especialidade: "Dermatologia",
    paciente: "Igor Moura",
    data: "2025-07-10",
    horario: "15:30",
  },
  {
    id: 3,
    medico: "Dr. Carlos Pereira",
    especialidade: "Ortopedia",
    paciente: "Igor Moura",
    data: "2025-07-20",
    horario: "09:00",
  },
];

export const Userpage = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <Background>
        <h1 className="text-4xl font-extrabold mb-10 text-center text-blue-900">
          Minhas Consultas
        </h1>
        {consultasSimuladas.length === 0 ? (
          <p className="text-center text-gray-600 text-lg">
            Você ainda não marcou nenhuma consulta.
          </p>
        ) : (
          <ConsultasTable consultas={consultasSimuladas} />
        )}
      </Background>
      <Footer />
    </div>
  );
};
