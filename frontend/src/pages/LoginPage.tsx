// src/pages/LoginPage.tsx
import { useState, type ChangeEvent } from "react";
import Background from "../components/Background/Background";
import Box from "../components/Box/Box";
import Header from "../components/Header/Header";
import Input from "../components/Inputs/Input";

const maskCpf = (v: string) => {
  const digits = v.replace(/\D/g, "").slice(0, 11); // mantém só números (máx. 11)
  return digits
    .replace(/(\d{3})(\d)/, "$1.$2")        // 123456 → 123.456
    .replace(/(\d{3})(\d)/, "$1.$2")        // 123.456789 → 123.456.789
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2"); // 123.456.78901 → 123.456.789-01
};

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [cpf, setCpf] = useState("");

  const handleCpfChange = (e: ChangeEvent<HTMLInputElement>) =>
    setCpf(maskCpf(e.target.value));

  return (
    <>
      <Header />
      <Background>
        <div className="flex justify-center items-center min-h-screen">
          <Box>
          
          <h1 className="font-bold text-2xl"> My appointments </h1>
          <p className="text-gray-500 p-3"> Coloque seu email e CPF pra verificar quais consultas você marcou</p>

            <Input
              placeholder="Email"
              type="email"
              value={email}
              required
              onChange={(e) => setEmail(e.target.value)}
            />

            <Input
              placeholder="CPF"
              inputMode="numeric"          // faz o teclado numérico abrir no mobile
              value={cpf}
              required
              onChange={handleCpfChange}
              pattern={
                cpf.length === 14 // só aplica pattern quando completo
                  ? "^(?!^(\\d)\\1{10}$)\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}$"
                  : undefined
              }
            />
          </Box>
        </div>
      </Background>
    </>
  );
};

export default LoginPage;
