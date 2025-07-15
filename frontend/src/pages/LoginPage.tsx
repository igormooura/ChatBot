import { useState, type ChangeEvent, type MouseEvent } from "react";
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
  const [step, setStep] = useState<"email" | "code">("code");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [cpf, setCpf] = useState("");
  const [loading, setLoading] = useState(false);

  const handleCpfChange = (e: ChangeEvent<HTMLInputElement>) =>
    setCpf(maskCpf(e.target.value));

  const handleSendCode = async (e: MouseEvent<HTMLButtonElement>) => {
    // TEMPORÁRIO!!!!
    e.preventDefault();

    if (!email.includes("@")) {
      alert("Digite um email válido!");
      return;
    }
    if (cpf.length !== 14) {
      alert("Digite um CPF válido no formato 000.000.000-00");
      return;
    }

    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      alert("Código enviado para o seu email!");
    } catch {
      alert("Erro ao enviar código. Tente novamente.");
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
                <h1 className="font-bold text-2xl"> Minhas consultas </h1>
                <p className="text-gray-500 p-3">
                  Coloque seu email e CPF pra verificar quais consultas você
                  marcou
                </p>
                <p className="text-gray-500 p-3">
                  Você receberá um código no seu email para garantir seu login.
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
                  inputMode="numeric" // faz o teclado numérico abrir no mobile
                  value={cpf}
                  required
                  onChange={handleCpfChange}
                  pattern={
                    cpf.length === 14
                      ? "^(?!^(\\d)\\1{10}$)\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}$"
                      : undefined
                  }
                />

                <button
                  className="btn-primary mt-4 bg-blue-600 text-white font-semibold px-10 py-2 rounded-lg 
                            shadow-md transition duration-300 ease-in-out hover:bg-blue-700"
                  disabled={loading}
                  onClick={handleSendCode}
                >
                  {loading ? "Enviando..." : "Enviar código"}
                </button>
              </>
            )}

            {step === "code" && (
              <>
                <h1 className="font-bold text-2xl"> Código </h1>
                <p className="text-gray-500 p-3">
                  {" "}
                  Você recebeu um código em {email}
                </p>

                <Input
                  placeholder="Digite aqui o seu código"
                  type="numeric"
                  value={code}
                  required
                  onChange={(e) => setEmail(e.target.value)}
                />

                <button
                  className="btn-primary mt-4 bg-blue-600 text-white font-semibold px-10 py-2 rounded-lg 
                            shadow-md transition duration-300 ease-in-out hover:bg-blue-700"
                  disabled={loading}
                  onClick={handleSendCode}
                >
                  {loading ? "Enviando..." : "Enviar código"}
                </button>

                <button
                  className="text-sm text-blue-500 underline mt-2"
                  disabled={loading}
                  onClick={handleSendCode}
                >
                  Resend code
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
