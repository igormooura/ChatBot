import { useState, type ChangeEvent, type MouseEvent } from "react";
import { useNavigate } from "react-router-dom";

import Background from "../components/Background/Background";
import Box from "../components/Box/Box";
import Header from "../components/Header/Header";
import Input from "../components/Inputs/Input";
import axios from "axios";

const maskCpf = (v: string) => {
  const digits = v.replace(/\D/g, "").slice(0, 11);
  return digits
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
};

const LoginPage = () => {
  const [step, setStep] = useState<"email" | "code">("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [cpf, setCpf] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleCpfChange = (e: ChangeEvent<HTMLInputElement>) =>
    setCpf(maskCpf(e.target.value));

const handleRequestCode = async (e: MouseEvent<HTMLButtonElement>) => {
  e.preventDefault();

  console.log(`cpf: '${cpf}', email: '${email}'`);

  setLoading(true);
  try {
    if (cpf.trim() === "000.000.000-00" && email.trim().toLowerCase() === "admin") {
      localStorage.setItem("jwt_token", "jwt-token-admin-mockado");
      navigate("/admin");
    } else {
      await axios.post("http://127.0.0.1:5000/auth/request-token", { email, cpf });
      alert("Código enviado para o seu email!");
      setStep("code");
    }
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      alert(`Erro: ${error.response?.data?.erro || error.message || "Tente novamente."}`);
    } else if (error instanceof Error) {
      alert(`Erro: ${error.message}`);
    } else {
      alert("Erro desconhecido. Tente novamente.");
    }
  } finally {
    setLoading(false);
  }
};


const handleVerifyCode = async (e: MouseEvent<HTMLButtonElement>) => {
  e.preventDefault();

  if (code.trim().length === 0) {
    alert("Por favor, digite o código que você recebeu.");
    return;
  }

  setLoading(true);
  try {
    const { data } = await axios.post("http://127.0.0.1:5000/auth/verify-token", { token: code });

    localStorage.setItem("cpf", data.cpf);                // cpf puro que veio do backend
    localStorage.setItem("jwt_token", data.jwt_token); // Alterado de data.jwt_token para data.token

    alert("Login realizado com sucesso!");
    navigate("/user");
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      alert(`Erro: ${error.response?.data?.erro || error.message || "Tente novamente."}`);
    } else if (error instanceof Error) {
      alert(`Erro: ${error.message}`);
    } else {
      alert("Erro desconhecido. Tente novamente.");
    }
  } finally {
    setLoading(false);
  }
};


  return (
    <Background>
      <Header />
      <div className="flex justify-center items-center min-h-screen">
        <Box>
          {step === "email" && (
            <>
              <h1 className="font-bold text-2xl">Minhas consultas</h1>
              <p className="text-gray-500 p-3">
                Coloque seu email e CPF para verificar as consultas que você marcou. Você receberá um código no seu email para garantir seu login.
              </p>
              <Input
                placeholder="Email"
                type="email"
                value={email}
                required
                onChange={(e) => setEmail(e.target.value)}
              />
              <Input
                placeholder="CPF"
                inputMode="numeric"
                value={cpf}
                required
                onChange={handleCpfChange}
              />
              <button
                className="btn-primary mt-4 bg-blue-600 text-white font-semibold px-10 py-2 rounded-lg shadow-md transition duration-300 ease-in-out hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
                onClick={handleRequestCode}
              >
                {loading ? "Enviando..." : "Enviar código"}
              </button>
            </>
          )}

          {step === "code" && (
            <>
              <h1 className="font-bold text-2xl">Código de Verificação</h1>
              <p className="text-gray-500 p-3">
                Você recebeu um código em <strong>{email}</strong>. Por favor, insira-o abaixo.
              </p>
              <Input
                placeholder="Digite aqui o seu código"
                inputMode="numeric"
                value={code}
                required
                onChange={(e) => setCode(e.target.value)}
              />
              <button
                className="btn-primary mt-4 bg-blue-600 text-white font-semibold px-10 py-2 rounded-lg shadow-md transition duration-300 ease-in-out hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
                onClick={handleVerifyCode}
              >
                {loading ? "Verificando..." : "Verificar e Entrar"}
              </button>
              <button
                className="text-sm text-blue-500 underline mt-2 disabled:opacity-50"
                disabled={loading}
                onClick={() => setStep("email")}
              >
                Mudar email ou CPF
              </button>
            </>
          )}
        </Box>
      </div>
    </Background>
  );
};

export default LoginPage;
