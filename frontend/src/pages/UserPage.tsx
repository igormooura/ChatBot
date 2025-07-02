import Footer from "../components/Footer/Footer";
import Header from "../components/Header/Header";

type Consulta = {
  id: number;
  medico: string;
  especialidade: string;
  paciente: string;
  data: string;
  horario: string;
};

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
      <main className="flex-grow bg-gradient-to-r from-blue-50 via-white to-blue-50 p-8">
        <h1 className="text-4xl font-extrabold mb-10 text-center text-blue-900">
          Minhas Consultas
        </h1>

        {consultasSimuladas.length === 0 ? (
          <p className="text-center text-gray-600 text-lg">
            Você ainda não marcou nenhuma consulta.
          </p>
        ) : (
          <div className="overflow-x-auto max-w-5xl mx-auto shadow-lg rounded-lg bg-white">
            <table className="w-full text-left rounded-lg">
              <thead className="bg-blue-100 border-b border-blue-300">
                <tr>
                  <th className="px-6 py-4 font-semibold text-blue-800">Médico / Especialidade</th>
                  <th className="px-6 py-4 font-semibold text-blue-800">Paciente</th>
                  <th className="px-6 py-4 font-semibold text-blue-800">Data</th>
                  <th className="px-6 py-4 font-semibold text-blue-800">Horário</th>
                </tr>
              </thead>
              <tbody>
                {consultasSimuladas.map(({ id, medico, especialidade, paciente, data, horario }) => (
                  <tr
                    key={id}
                    className="border-b border-gray-200 hover:bg-blue-50 transition-colors cursor-pointer"
                  >
                    <td className="px-6 py-4">
                      <p className="font-semibold text-blue-900">{medico}</p>
                      <p className="text-sm text-blue-600 italic">{especialidade}</p>
                    </td>
                    <td className="px-6 py-4 text-gray-700">{paciente}</td>
                    <td className="px-6 py-4 text-gray-700">{new Date(data).toLocaleDateString("pt-BR")}</td>
                    <td className="px-6 py-4 text-gray-700">{horario}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
};
