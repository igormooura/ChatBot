import { useState, type ChangeEvent, type MouseEvent } from "react";
import { useNavigate } from "react-router-dom"; // Importe para navegação
import Background from "../components/Background/Background";
import Box from "../components/Box/Box";
import Header from "../components/Header/Header";
import Input from "../components/Inputs/Input";

const maskCpf = (v: string) => {
  const digits = v.replace(/\D/g, "").slice(0, 11); // mantém só números (máx. 11)
  return digits
    .replace(/(\d{3})(\d)/, "$1.$2") // 123456 → 123.456
    .replace(/(\d{3})(\d)/, "$1.$2") // 123.456789 → 123.456.789
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2"); // 123.456.78901 → 123.456.789-01
};


const LoginPage = () => {
  const [step, setStep] = useState<"email" | "code">("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [cpf, setCpf] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // Hook para redirecionar o usuário

  const handleCpfChange = (e: ChangeEvent<HTMLInputElement>) =>
    setCpf(maskCpf(e.target.value));

  // Função para solicitar o código ao backend
  const handleRequestCode = async (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!email.includes("@") || cpf.length !== 14) {
      alert("Por favor, preencha um e-mail e CPF válidos.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/auth/request-token", // ✅ ROTA CORRETA
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, cpf }),
        }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.erro || "Erro no servidor.");

      alert("Código enviado para o seu email!");
      setStep("code"); // Avança para a tela de inserir o código
    } catch (error) {
      alert(`Erro: ${error instanceof Error ? error.message : "Tente novamente."}`);
    } finally {
      setLoading(false);
    }
  };

  // Função para validar o código e fazer login
  const handleVerifyCode = async (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (code.trim().length === 0) {
      alert("Por favor, digite o código que você recebeu.");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(
        "http://127.0.0.1:5000/auth/verify-token",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: code }), // Envia o código digitado
        }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.erro || "Código inválido ou expirado.");

      // SUCESSO! O backend retornou um JWT.
      localStorage.setItem("jwt_token", data.jwt_token); // Armazena o token de sessão
      alert("Login realizado com sucesso!");
      navigate("/meu-perfil"); // Redireciona para uma página protegida
    } catch (error) {
      alert(`Erro: ${error instanceof Error ? error.message : "Tente novamente."}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Background>
        <Header />
        <div className="flex justify-center items-center min-h-screen">
          <Box>
            {step === "email" && (
              <>
                <h1 className="font-bold text-2xl">Minhas consultas</h1>
                <p className="text-gray-500 p-3">
                  Coloque seu email e CPF pra verificar quais consultas você marcou
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
                  className="btn-primary mt-4 bg-blue-600 text-white font-semibold px-10 py-2 rounded-lg shadow-md transition duration-300 ease-in-out hover:bg-blue-700"
                  disabled={loading}
                  onClick={handleRequestCode} // 👈 CHAMA A FUNÇÃO CORRETA
                >
                  {loading ? "Enviando..." : "Enviar código"}
                </button>
              </>
            )}

            {step === "code" && (
              <>
                <h1 className="font-bold text-2xl">Código de Acesso</h1>
                <p className="text-gray-500 p-3">
                  Você recebeu um código em <strong>{email}</strong>
                </p>
                <Input
                  placeholder="Digite aqui o seu código"
                  type="text" // Token pode ter letras e números
                  value={code}
                  required
                  onChange={(e) => setCode(e.target.value)} // Corrigido para setCode
                />
                <button
                  className="btn-primary mt-4 bg-blue-600 text-white font-semibold px-10 py-2 rounded-lg shadow-md transition duration-300 ease-in-out hover:bg-blue-700"
                  disabled={loading}
                  onClick={handleVerifyCode} // 👈 CHAMA A FUNÇÃO DE VERIFICAÇÃO
                >
                  {loading ? "Validando..." : "Fazer Login"}
                </button>
                <button
                  className="text-sm text-blue-500 underline mt-2"
                  disabled={loading}
                  onClick={() => setStep("email")} // Volta para a etapa anterior
                >
                  Corrigir e-mail ou CPF
                </button>
              </>
            )}
          </Box>
        </div>
      </Background>
    </>
  );
};

export default LoginPage;