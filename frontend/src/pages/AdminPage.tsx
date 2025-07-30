import { useState, useEffect } from "react";
import axios from "axios";
import Footer from "../components/Footer/Footer";
import Header from "../components/Header/Header";
import ConsultasTable from "../components/Tables/ConsultasTable";
import type { Consulta } from "../components/Tables/ConsultasTable";
import Background from "../components/Background/Background";

interface ApiConsulta {
  id: number;
  tipo: "consulta";
  data: string;
  status: string;
  cpf_paciente: string;
  medico: string;
}

interface ApiExame {
  id: number;
  tipo: "exame";
  data: string;
  status: string;
  paciente: string;
  cpf_paciente: string;
  exame: string;
}

interface ApiResponse {
  consultas: ApiConsulta[];
  exames: ApiExame[];
}

export const AdminPage = () => {
  const [consultas, setConsultas] = useState<Consulta[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDados = async () => {
      try {
        setLoading(true);
        const response = await axios.get<ApiResponse>(
          "http://127.0.0.1:5000/todas-consultas"
        );
        const { consultas: consultasApi, exames: examesApi } = response.data;

        const dadosConsultas: Consulta[] = consultasApi.map((c) => {
          const dataIso = c.data.endsWith("Z") ? c.data : c.data + "Z";
          const dataHora = new Date(dataIso);
          return {
            id: c.id,
            medico: c.medico,
            especialidade: "Consulta Clínica",
            cpf: `Paciente (CPF: ${c.cpf_paciente})`,
            data: dataHora.toLocaleDateString("pt-BR"),
            horario: dataHora.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          };
        });

        const dadosExames: Consulta[] = examesApi.map((e) => {
          const dataHora = new Date(e.data);
          return {
            id: e.id,
            medico: "Laboratório",
            especialidade: e.exame,
            cpf: `Paciente (CPF: ${e.cpf_paciente})`,
            data: dataHora.toLocaleDateString("pt-BR"),
            horario: dataHora.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          };
        });

        setConsultas([...dadosConsultas, ...dadosExames]);
        setError(null);
      } catch (err) {
        setError(
          "Não foi possível carregar os dados. Verifique se o servidor está online."
        );
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDados();
  }, []);

  const handleDelete = (id: string | number) => {
    if (window.confirm("Tem certeza que deseja deletar este item?")) {
      setConsultas((prev) => prev.filter((c) => c.id !== id));
    }
  };

  const renderContent = () => {
    if (loading) {
      return <p className="text-center text-gray-600 text-lg">Carregando...</p>;
    }
    if (error) {
      return <p className="text-center text-red-600 text-lg">{error}</p>;
    }
    if (consultas.length === 0) {
      return (
        <p className="text-center text-gray-600 text-lg">
          Nenhum agendamento cadastrado no momento.
        </p>
      );
    }
    return <ConsultasTable consultas={consultas} onDelete={handleDelete} />;
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <Background>
        <h1 className="text-4xl font-extrabold mb-10 text-center text-blue-900">
          Todos os Agendamentos
        </h1>
        {renderContent()}
      </Background>
      <Footer />
    </div>
  );
};
