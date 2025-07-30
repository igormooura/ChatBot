import { useState, useEffect } from "react";
import axios from "axios";
import Footer from "../components/Footer/Footer";
import Header from "../components/Header/Header";
import ConsultasTable from "../components/Tables/ConsultasTable";
import type { Consulta, Exam } from "../components/Tables/ConsultasTable";
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
  const [items, setItems] = useState<(Consulta | Exam)[]>([]);  // mudar o estado para aceitar ambos
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
            tipo: "consulta",
            status: c.status,
            medico: c.medico,
            especialidade: "Consulta Clínica",
            data: dataHora.toISOString(),
            horario: dataHora.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          };
        });

        const dadosExames: Exam[] = examesApi.map((e) => {
          const dataHora = new Date(e.data);
          return {
            id: e.id,
            tipo: "exame",
            status: e.status,
            exame: e.exame,
            data: dataHora.toISOString(),
            horario: dataHora.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            }),
          };
        });

        setItems([...dadosConsultas, ...dadosExames]);
        setError(null);
      } catch (err) {
        console.log(err);
        setError("Erro ao carregar dados.");
      } finally {
        setLoading(false);
      }
    };

    fetchDados();
  }, []);

  const handleDelete = (id: number) => {
    if (window.confirm("Tem certeza que deseja deletar este item?")) {
      setItems((prev) => prev.filter((c) => c.id !== id));
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <Background>
        <h1 className="text-4xl font-extrabold mb-10 text-center text-blue-900">
          Todos os Agendamentos
        </h1>
        {loading && <p className="text-center text-gray-600 text-lg">Carregando...</p>}
        {error && <p className="text-center text-red-600 text-lg">{error}</p>}
        {!loading && !error && (
          <ConsultasTable
            consultas={items.filter((i): i is Consulta => i.tipo === "consulta")}
            exames={items.filter((i): i is Exam => i.tipo === "exame")}
            onDeleteConsulta={handleDelete}
            onDeleteExame={handleDelete}
            isAdmin={true}
          />
        )}
      </Background>
      <Footer />
    </div>
  );
};
