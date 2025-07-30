import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Background from '../components/Background/Background';
import Footer from '../components/Footer/Footer';
import Header from '../components/Header/Header';
import ConsultasTable from '../components/Tables/ConsultasTable';

interface Consulta {
  id: number;
  tipo: 'consulta';
  data: string;
  status: string;
  medico: string;
  especialidade?: string;
  horario?: string;
}

interface Exam {
  id: number;
  tipo: 'exame';
  data: string;
  status: string;
  exame: string;
  horario?: string;
}

interface ApiResponse {
  consultas: Consulta[];
  exames: Exam[];
}

const useUserAppointments = (cpf: string, jwtToken: string) => {
  const [consultas, setConsultas] = useState<Consulta[]>([]);
  const [exames, setExames] = useState<Exam[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  useEffect(() => {
    const fetchAppointments = async () => {
      if (!cpf || !jwtToken) {
        return;
      }
      setLoading(true);
      try {
        const response = await axios.get<ApiResponse>(
          `http://127.0.0.1:5000/consultas/${cpf}`,
          { headers: { Authorization: `Bearer ${jwtToken}` } }
        );
        setConsultas(response.data.consultas || []);
        setExames(response.data.exames || []);
        setError(null);
      } catch (error){
      console.log(error)
    
      } finally {
        setLoading(false);
      }
    };
    fetchAppointments();
  }, [cpf, jwtToken, refreshKey]);

  const refresh = () => setRefreshKey((prev) => prev + 1);

  return { consultas, exames, loading, error, refresh };
};

const UserPage: React.FC = () => {
  const rawCpf = localStorage.getItem('cpf') || '';
  const rawToken = localStorage.getItem('jwt_token') || '';
  const cpf = rawCpf.replace(/[.-]/g, '');

  let jwtToken = rawToken;
  try {
    const parsed = JSON.parse(rawToken);
    if (typeof parsed === 'string') jwtToken = parsed;
    else if (parsed?.token) jwtToken = parsed.token;
  } catch (error){
      console.log(error)
    }

  const { consultas, exames, loading, error, refresh } = useUserAppointments(cpf, jwtToken);

  const handleDeleteConsulta = async (id: number) => {
    try {
      await axios.delete(`http://127.0.0.1:5000/consultas/${id}`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      refresh();
    } catch (error){
      console.log(error)
    }

  };

  const handleDeleteExame = async (id: number) => {
    try {
      await axios.delete(`http://127.0.0.1:5000/exames/${id}`, {
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      refresh();
    } catch (error){
      console.log(error)
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <Background>
        <h1 className="text-4xl font-extrabold mb-10 text-center text-blue-900">
          Minhas Consultas e Exames
        </h1>
        {loading && <p className="text-center text-blue-600 text-lg">Carregando...</p>}
        {error && <p className="text-center text-red-600 text-lg">{error}</p>}
        <ConsultasTable
          consultas={consultas}
          exames={exames}
          onDeleteConsulta={handleDeleteConsulta}
          onDeleteExame={handleDeleteExame}
          isAdmin={false}
        />
      </Background>
      <Footer />
    </div>
  );
};

export default UserPage;
